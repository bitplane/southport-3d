#!/usr/bin/env python3
"""Validate emitted GLBs, embedded textures, bounds and manifest file hashes."""
import io
import json
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from southport3d.lod import sha256


def read_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data)
    if magic != b'glTF' or version != 2 or length != len(data):
        raise ValueError('Invalid GLB header')
    offset, document, binary = 12, None, None
    while offset < length:
        size, kind = struct.unpack_from('<I4s', data, offset)
        offset += 8
        chunk = data[offset:offset + size]
        if len(chunk) != size:
            raise ValueError('Truncated GLB chunk')
        if kind == b'JSON':
            document = json.loads(chunk)
        elif kind == b'BIN\0':
            binary = chunk
        offset += size
    if document is None or binary is None:
        raise ValueError('GLB must embed JSON and binary data')
    if any('uri' in b for b in document.get('buffers', [])):
        raise ValueError('External buffers are not portable')
    return document, binary


def array(doc, binary, index):
    accessor = doc['accessors'][index]
    if 'sparse' in accessor:
        raise ValueError('Sparse accessors not supported by this validator')
    view = doc['bufferViews'][accessor['bufferView']]
    dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[accessor['componentType']]
    columns = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[accessor['type']]
    itemsize = np.dtype(dtype).itemsize
    offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    return np.ndarray((accessor['count'], columns), dtype=dtype, buffer=binary,
                      offset=offset, strides=(view.get('byteStride', columns * itemsize), itemsize))


def matrix(node):
    if 'matrix' in node:
        return np.asarray(node['matrix']).reshape(4, 4).T
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    rotation = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                         [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                         [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    result = np.eye(4)
    result[:3, :3] = rotation @ np.diag(node.get('scale', [1, 1, 1]))
    result[:3, 3] = node.get('translation', [0, 0, 0])
    return result


def verify_glb(path, row):
    doc, binary = read_glb(path)
    points, triangle_count = [], 0

    def walk(index, parent):
        nonlocal triangle_count
        node = doc['nodes'][index]
        transform = parent @ matrix(node)
        if 'mesh' in node:
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                if primitive.get('mode', 4) != 4:
                    raise ValueError('Only triangle primitives supported')
                attributes = primitive['attributes']
                if not {'POSITION', 'NORMAL', 'TEXCOORD_0', 'TANGENT'} <= attributes.keys():
                    raise ValueError('Missing position, normal, UV or tangent attribute')
                positions = array(doc, binary, attributes['POSITION'])
                if not np.isfinite(positions).all():
                    raise ValueError('Invalid positions')
                indices = array(doc, binary, primitive['indices']).ravel()
                if len(indices) % 3 or indices.max() >= len(positions):
                    raise ValueError('Invalid triangle indices')
                triangle_count += len(indices) // 3
                homogeneous = np.column_stack([positions, np.ones(len(positions))])
                gltf_world = (transform @ homogeneous.T).T[:, :3]
                points.append(gltf_world[:, [0, 2, 1]] * [1, -1, 1])
                mat = doc['materials'][primitive['material']]
                pbr = mat['pbrMetallicRoughness']
                if not ('normalTexture' in mat and 'baseColorTexture' in pbr and 'metallicRoughnessTexture' in pbr):
                    raise ValueError('Missing baked PBR channels')
                if mat.get('alphaMode', 'OPAQUE') != 'OPAQUE':
                    raise ValueError('Bake coverage alpha must not make stone transparent')
        for child in node.get('children', []):
            walk(child, transform)

    for root in doc['scenes'][doc.get('scene', 0)]['nodes']:
        walk(root, np.eye(4))
    if triangle_count != row['triangles']:
        raise ValueError('Exported triangle count differs from baked mesh')
    positions = np.concatenate(points)
    exported_bounds = np.array([positions.min(axis=0), positions.max(axis=0)])
    if not np.allclose(exported_bounds, row['bounds'], atol=1e-4, rtol=0):
        raise ValueError('GLB transform/bounds mismatch')
    if len(doc.get('images', [])) < 3:
        raise ValueError('Expected base colour, normal and packed material textures')
    for image in doc['images']:
        if 'uri' in image:
            raise ValueError('GLB must embed its images')
        view = doc['bufferViews'][image['bufferView']]
        start = view.get('byteOffset', 0)
        with Image.open(io.BytesIO(binary[start:start + view['byteLength']])) as decoded:
            if decoded.size != (row['texture_size'], row['texture_size']):
                raise ValueError('Texture resolution differs from manifest')
            decoded.verify()


def check(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'manifest.json').read_text())
    if not manifest['targets']:
        raise ValueError('Empty LOD manifest')
    total = 0
    for target in manifest['targets']:
        previous = target['source_triangles']
        if [x['id'] for x in target['lods']] != [x['id'] for x in manifest['levels']]:
            raise ValueError('Incomplete levels')
        for row in target['lods']:
            if row.get('strategy') == 'omit':
                if row['triangles'] != 0 or not row.get('reason'):
                    raise ValueError('Omitted targets need a reason and zero geometry')
                previous = 0
                continue
            if not 0 < row['triangles'] <= previous:
                raise ValueError('LOD triangle counts must decrease')
            previous = row['triangles']
            if row['sampled_surface_error']['max_m'] > row['max_sampled_error_m']:
                raise ValueError('Sampled geometry error exceeds declared tolerance')
            for record in [row['glb'], *row['textures']]:
                path = (root / record['uri']).resolve()
                if not path.is_relative_to(root):
                    raise ValueError('Manifest path escapes output')
                if path.stat().st_size != record['bytes'] or sha256(path) != record['sha256']:
                    raise ValueError(f'Output changed: {record["uri"]}')
            verify_glb(root / row['glb']['uri'], row)
            total += 1
    print(f'Validated {total} GLBs: triangles, transforms, PBR channels, textures and hashes.')


if __name__ == '__main__':
    check(sys.argv[1])
