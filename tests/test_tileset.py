import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import tileset
from tileset import build, read_glb, write_glb


def png(size, colour):
    buffer = io.BytesIO()
    Image.new('RGB', (size, size), colour).save(buffer, 'PNG')
    return buffer.getvalue()


def glb(path, image=None, offset=0.):
    """One textured triangle; enough structure to exercise merging."""
    positions = struct.pack('<9f', offset, 0, 0, offset + 1, 0, 0, offset, 1, 0)
    uvs = struct.pack('<6f', 0, 0, 1, 0, 0, 1)
    binary = positions + uvs
    doc = {'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': 'wall'}],
           'meshes': [{'primitives': [{'attributes': {'POSITION': 0, 'TEXCOORD_0': 1}, 'material': 0}]}],
           'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': 3, 'type': 'VEC3',
                          'min': [offset, 0, 0], 'max': [offset + 1, 1, 0]},
                         {'bufferView': 1, 'componentType': 5126, 'count': 3, 'type': 'VEC2'}],
           'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': 36}, {'buffer': 0, 'byteOffset': 36, 'byteLength': 24}],
           'materials': [{'pbrMetallicRoughness': {'metallicFactor': 0}}], 'buffers': []}
    if image:
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(image)})
        binary += image
        doc['images'] = [{'bufferView': 2, 'mimeType': 'image/png'}]
        doc['textures'] = [{'source': 0}]
        doc['materials'][0]['pbrMetallicRoughness']['baseColorTexture'] = {'index': 0}
        doc['materials'][0]['normalTexture'] = {'index': 0}
    doc['buffers'] = [{'byteLength': len(binary) + (-len(binary) % 4)}]
    data = write_glb(doc, binary)
    path.write_bytes(data)
    return {'uri': path.name, 'sha256': hashlib.sha256(data).hexdigest(), 'bounds': [[offset, 0, 0], [offset + 1, 1, 1]],
            'gpuBytesEstimate': 1000}


def catalog(tmp_path):
    big = png(2048, (200, 50, 50))
    levels = {'detail': glb(tmp_path / 'd.glb', big), 'walk': glb(tmp_path / 'w.glb', png(512, (200, 50, 50))),
              'district': glb(tmp_path / 'z.glb', png(2048, (190, 60, 50)))}
    ground = glb(tmp_path / 'g.glb', png(64, (90, 90, 90)), 0)
    road = glb(tmp_path / 'r.glb', None, 150)
    return {'assets': [
        {'id': 'house', 'position': [10, 0, 20], 'rotationY': math.pi / 2,
         'parts': [{'id': 'walls', 'bounds': levels['detail']['bounds'], 'levels': levels},
                   {'id': 'sign', 'fixedLevel': 'detail', 'bounds': ground['bounds'],
                    'levels': {'detail': ground}}]},
        {'id': 'realm', 'position': [0, 0, 0], 'rotationY': 0,
         'parts': [{'id': 'near', 'ground': True, 'bounds': ground['bounds'], 'levels': {l: ground for l in tileset.LEVELS}},
                   {'id': 'far', 'ground': True, 'bounds': road['bounds'], 'levels': {l: road for l in tileset.LEVELS}}]}]}


def tiles(node):
    yield node
    for child in node.get('children', []):
        yield from tiles(child)


def test_buildings_chain_levels_and_wide_assets_split(tmp_path):
    c = catalog(tmp_path)
    document, written, _ = build(c, tmp_path, tmp_path / 'out', tmp_path / 'cache')
    units = {}
    for t in tiles(document['root']):
        if 'unit' in t.get('extras', {}): units.setdefault(t['extras']['unit'], []).append(t)
    # The house is one unit; the 150 m wide public realm splits into its parts.
    assert sorted(units) == ['house', 'realm/far', 'realm/near']
    chain = units['house']
    assert [t['extras']['level'] for t in chain] == ['district', 'walk', 'detail']
    assert [t['geometricError'] for t in chain] == [tileset.ERROR['district'], tileset.ERROR['walk'], 0]
    assert all(t['refine'] == 'REPLACE' for t in tiles(document['root']))
    # Identical levels collapse to one tile which serves all of them.
    assert [(t['extras']['level'], t['extras']['rank'], t['geometricError']) for t in units['realm/near']] == [('detail', 1, 0)]
    assert all((tmp_path / 'out' / u).is_file() for u in written)


def test_merged_content_places_parts_and_caps_textures(tmp_path):
    document, _, _ = build(catalog(tmp_path), tmp_path, tmp_path / 'out', tmp_path / 'cache')
    house = {t['extras']['level']: t for t in tiles(document['root']) if t.get('extras', {}).get('unit') == 'house'}
    doc, binary = read_glb(tmp_path / 'out/tiles' / house['district']['content']['uri'])
    roots = [doc['nodes'][i] for i in doc['scenes'][0]['nodes']]
    assert [r['extras'] for r in roots] == [{'asset': 'house', 'part': 'walls', 'ground': False},
                                            {'asset': 'house', 'part': 'sign', 'ground': False}]
    assert roots[0]['matrix'] == tileset.yaw_matrix([10, 0, 20], math.pi / 2)
    view = doc['bufferViews'][doc['images'][0]['bufferView']]
    image = Image.open(io.BytesIO(binary[view['byteOffset']:view['byteOffset'] + view['byteLength']]))
    assert image.size == (tileset.CAP['district'], tileset.CAP['district'])
    # Fixed-level parts draw their fixed level at every level.
    assert len(doc['images']) == 2
    # Detail keeps the 2048 px atlas whole.
    detail, binary = read_glb(tmp_path / 'out/tiles' / house['detail']['content']['uri'])
    view = detail['bufferViews'][detail['images'][0]['bufferView']]
    assert Image.open(io.BytesIO(binary[view['byteOffset']:view['byteOffset'] + view['byteLength']])).size == (2048, 2048)


def test_proxies_drop_or_flatten_textures(tmp_path):
    document, _, _ = build(catalog(tmp_path), tmp_path, tmp_path / 'out', tmp_path / 'cache')
    root = document['root']
    assert root['extras']['proxy'] in ('lite', 'flat') and root['geometricError'] == tileset.ERROR['root']
    for mode in ('lite', 'flat'):
        merger = tileset.Merger(mode)
        merger.add(tmp_path / 'd.glb', tileset.yaw_matrix([0, 0, 0], 0))
        (tmp_path / 'merged.glb').write_bytes(merger.glb())
        doc, _ = read_glb(tmp_path / 'merged.glb')
        material = doc['materials'][0]
        assert 'normalTexture' not in material
        if mode == 'flat':
            assert 'images' not in doc and 'textures' not in doc
            assert 'TEXCOORD_0' not in doc['meshes'][0]['primitives'][0]['attributes']
            factor = material['pbrMetallicRoughness']['baseColorFactor']
            assert abs(factor[0] - ((200 / 255 + .055) / 1.055) ** 2.4) < .01 and factor[1] < factor[0]
        else:
            assert doc['images'] and 'baseColorTexture' in material['pbrMetallicRoughness']


def test_content_is_cached_and_deterministic(tmp_path):
    c = catalog(tmp_path)
    first = build(c, tmp_path, tmp_path / 'out', tmp_path / 'cache')
    second = build(c, tmp_path, tmp_path / 'out', tmp_path / 'cache')
    assert first[0] == second[0] and first[1] == second[1]
    assert second[2]['built'] == 0 and second[2]['reused'] > 0
    rotated = json.loads(json.dumps(c)); rotated['assets'][0]['rotationY'] = 0
    changed = build(rotated, tmp_path, tmp_path / 'out', tmp_path / 'cache')
    assert changed[1] != first[1] and changed[1] & first[1]  # unrelated tiles are reused


def test_oriented_box_follows_asset_yaw():
    box = tileset.obb([[0, 0, 0], [20, 4, 2]], [100, 1, 50], math.pi / 2)
    assert [round(v, 6) for v in box[:3]] == [101, 3, 40]
    # The long local x axis now runs along -z; the box is not inflated to an AABB.
    assert [round(v, 6) for v in box[3:6]] == [0, 0, -10]
    assert [round(v, 6) for v in box[9:12]] == [1, 0, 0]
