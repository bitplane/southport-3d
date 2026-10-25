"""Build a 3D Tiles 1.1 hierarchy (HLOD) from the published asset catalog.

Each building is one LoD unit: its parts are merged per level into one glTF so a
building never shows mixed levels. Units chain District -> Walk -> Detail with
REPLACE refinement, so a coarser tile stays visible until its replacement is
ready. Above the units, quadtree leaf cells hold merged District proxies with
small textures, and the root holds the whole town with textures flattened to
mean colours. Content is content-addressed under dist/tiles/.
"""
import hashlib
import io
import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image

VERSION = 'tiles-4'
LEVELS = ('district', 'walk', 'detail')
# Geometric error (metres) of each tile kind. With the default 8 px error target
# at 1000 px viewport height and 50 degree FOV, a tile refines within roughly
# 134 x error metres: District -> Walk at ~70 m, Walk -> Detail at ~8 m.
ERROR = {'detail': 0., 'walk': .06, 'district': .52, 'lite': 1.5, 'root': 40.}
# Texture caps keep coarse levels cheaper than the levels they stand in for.
CAP = {'detail': 4096, 'walk': 2048, 'district': 512, 'lite': 128, 'flat': 0}
UNIT_EXTENT = 96   # wider assets (roads, public realm) become one unit per part
UNIT_BYTES = 64e6  # so do assets whose merged Detail would dominate the memory budget
LEAF_SIZE = 128    # quadtree cells at or below this size hold textured proxies
LEAF_UNITS = 6


def read_glb(path):
    data = Path(path).read_bytes()
    magic, _, length = struct.unpack_from('<III', data)
    if magic != 0x46546C67 or length != len(data): raise ValueError(f'Invalid GLB: {path}')
    offset, doc, binary = 12, None, b''
    while offset < length:
        size, kind = struct.unpack_from('<II', data, offset)
        chunk = data[offset+8:offset+8+size]
        if kind == 0x4E4F534A: doc = json.loads(chunk)
        elif kind == 0x004E4942: binary = chunk
        offset += 8 + size
    return doc, binary


def write_glb(doc, binary):
    text = json.dumps(doc, separators=(',', ':')).encode()
    text += b' ' * (-len(text) % 4)
    binary += b'\0' * (-len(binary) % 4)
    total = 12 + 8 + len(text) + 8 + len(binary)
    return (struct.pack('<III', 0x46546C67, 2, total) + struct.pack('<II', len(text), 0x4E4F534A) + text +
            struct.pack('<II', len(binary), 0x004E4942) + binary)


def yaw_matrix(position, yaw):
    """Column-major glTF matrix matching three.js group.position + rotation.y."""
    c, s = math.cos(yaw), math.sin(yaw)
    return [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, position[0], position[1], position[2], 1]


def srgb_mean(image):
    """Linear mean colour of an sRGB image, as a glTF baseColorFactor."""
    rgba = np.asarray(image.convert('RGBA').resize((32, 32), Image.BILINEAR), dtype=np.float64) / 255
    rgb = rgba[..., :3]
    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    return [*linear.reshape(-1, 3).mean(axis=0).tolist(), float(rgba[..., 3].mean())]


class Merger:
    """Copy the reachable parts of several GLBs into one, transforming each root.

    mode is a CAP key: textures larger than its cap are downsampled; 'lite' also
    drops normal/roughness maps and 'flat' replaces every texture by its mean colour.
    """

    def __init__(self, mode):
        self.mode, self.cap = mode, CAP[mode]
        self.doc = {'asset': {'version': '2.0', 'generator': 'southport3d ' + VERSION}, 'scene': 0,
                    'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [], 'accessors': [], 'bufferViews': [],
                    'materials': [], 'textures': [], 'images': [], 'samplers': [], 'buffers': []}
        self.binary = bytearray()
        self.images = {}  # source image hash -> output index (shared atlases stay shared)

    def view(self, data, target=None):
        self.binary += b'\0' * (-len(self.binary) % 8)
        row = {'buffer': 0, 'byteOffset': len(self.binary), 'byteLength': len(data)}
        if target: row['target'] = target
        self.binary += data
        self.doc['bufferViews'].append(row)
        return len(self.doc['bufferViews']) - 1

    def add(self, path, matrix, extras=None):
        doc, binary = read_glb(path)
        memo = {k: {} for k in ('node', 'mesh', 'accessor', 'material', 'texture', 'image')}
        out = self.doc

        def raw(view_index):
            v = doc['bufferViews'][view_index]
            start = v.get('byteOffset', 0)
            return binary[start:start + v['byteLength']], v

        def accessor(i):
            if i in memo['accessor']: return memo['accessor'][i]
            a = dict(doc['accessors'][i])
            if 'sparse' in a: raise ValueError(f'{path}: sparse accessors are not supported')
            if 'bufferView' in a:
                data, v = raw(a['bufferView'])
                index = self.view(data, v.get('target'))
                if 'byteStride' in v: out['bufferViews'][index]['byteStride'] = v['byteStride']
                a['bufferView'] = index
            out['accessors'].append(a)
            memo['accessor'][i] = len(out['accessors']) - 1
            return memo['accessor'][i]

        def image(i):
            if i in memo['image']: return memo['image'][i]
            src = doc['images'][i]
            if 'bufferView' not in src: raise ValueError(f'{path}: external images are not supported')
            data, _ = raw(src['bufferView'])
            digest = hashlib.sha256(data).hexdigest()
            if digest not in self.images:
                mime = src.get('mimeType', 'image/png')
                picture = Image.open(io.BytesIO(data))
                if max(picture.size) > self.cap:
                    scale = self.cap / max(picture.size)
                    size = tuple(max(1, round(n * scale)) for n in picture.size)
                    buffer = io.BytesIO()
                    picture.resize(size, Image.LANCZOS).save(buffer, 'PNG', compress_level=6)
                    data, mime = buffer.getvalue(), 'image/png'
                out['images'].append({'bufferView': self.view(data), 'mimeType': mime})
                self.images[digest] = len(out['images']) - 1
            memo['image'][i] = self.images[digest]
            return memo['image'][i]

        def texture(info):
            i = info['index']
            if i not in memo['texture']:
                t = dict(doc['textures'][i])
                t['source'] = image(t['source'])
                if 'sampler' in t:
                    out['samplers'].append(doc['samplers'][t['sampler']])
                    t['sampler'] = len(out['samplers']) - 1
                out['textures'].append(t)
                memo['texture'][i] = len(out['textures']) - 1
            return dict(info, index=memo['texture'][i])

        def mean(info):
            data, _ = raw(doc['images'][doc['textures'][info['index']]['source']]['bufferView'])
            return srgb_mean(Image.open(io.BytesIO(data)))

        def material(i):
            if i in memo['material']: return memo['material'][i]
            m = json.loads(json.dumps(doc['materials'][i]))
            pbr = m.setdefault('pbrMetallicRoughness', {})
            if self.mode in ('lite', 'flat'):
                for key in ('normalTexture', 'occlusionTexture'): m.pop(key, None)
                pbr.pop('metallicRoughnessTexture', None)
            if self.mode == 'flat':
                if 'baseColorTexture' in pbr:
                    tint = pbr.get('baseColorFactor', [1, 1, 1, 1])
                    pbr['baseColorFactor'] = [a * b for a, b in zip(tint, mean(pbr.pop('baseColorTexture')))]
                if 'emissiveTexture' in m:
                    m['emissiveFactor'] = [a * b for a, b in zip(m.get('emissiveFactor', [1, 1, 1]), mean(m.pop('emissiveTexture'))[:3])]
            for key in ('normalTexture', 'occlusionTexture', 'emissiveTexture'):
                if key in m: m[key] = texture(m[key])
            for key in ('baseColorTexture', 'metallicRoughnessTexture'):
                if key in pbr: pbr[key] = texture(pbr[key])
            for ext in m.get('extensions', {}).values():
                for key, value in list(ext.items()):
                    if isinstance(value, dict) and 'index' in value:
                        # Proxies keep extension factors but not their maps.
                        if self.mode in ('lite', 'flat'): del ext[key]
                        else: ext[key] = texture(value)
            out['materials'].append(m)
            memo['material'][i] = len(out['materials']) - 1
            return memo['material'][i]

        def mesh(i):
            if i in memo['mesh']: return memo['mesh'][i]
            m = dict(doc['meshes'][i], primitives=[])
            for p in doc['meshes'][i]['primitives']:
                p = dict(p)
                textured = self.mode != 'flat'
                attributes = {k: v for k, v in p['attributes'].items()
                              if textured or not k.startswith(('TEXCOORD', 'TANGENT'))}
                if self.mode == 'lite': attributes.pop('TANGENT', None)
                p['attributes'] = {k: accessor(v) for k, v in attributes.items()}
                if 'indices' in p: p['indices'] = accessor(p['indices'])
                if 'material' in p: p['material'] = material(p['material'])
                if 'targets' in p: raise ValueError(f'{path}: morph targets are not supported')
                m['primitives'].append(p)
            out['meshes'].append(m)
            memo['mesh'][i] = len(out['meshes']) - 1
            return memo['mesh'][i]

        def node(i):
            n = dict(doc['nodes'][i])
            if 'skin' in n or 'camera' in n: raise ValueError(f'{path}: skins and cameras are not supported')
            if 'mesh' in n: n['mesh'] = mesh(n['mesh'])
            if 'children' in n: n['children'] = [node(c) for c in n['children']]
            out['nodes'].append(n)
            return len(out['nodes']) - 1

        roots = [node(i) for i in doc['scenes'][doc.get('scene', 0)]['nodes']]
        root = {'matrix': matrix, 'children': roots}
        if extras: root['extras'] = extras
        out['nodes'].append(root)
        out['scenes'][0]['nodes'].append(len(out['nodes']) - 1)
        out['extensionsUsed'] = sorted(set(out.get('extensionsUsed', [])) | set(doc.get('extensionsUsed', [])))

    def glb(self):
        doc = {k: v for k, v in self.doc.items() if v != []}
        doc['buffers'] = [{'byteLength': len(self.binary)}]
        return write_glb(doc, bytes(self.binary))


def obb(local, position, yaw):
    """3D Tiles box (centre + half axes) for a local box placed with a yaw."""
    c, s = math.cos(yaw), math.sin(yaw)
    centre = [(local[0][k] + local[1][k]) / 2 for k in range(3)]
    half = [(local[1][k] - local[0][k]) / 2 for k in range(3)]
    x, y, z = centre
    world = [c*x + s*z + position[0], y + position[1], -s*x + c*z + position[2]]
    return world + [c*half[0], 0, -s*half[0], 0, half[1], 0, s*half[2], 0, c*half[2]]


def obb_aabb(box):
    centre, axes = box[:3], [box[3:6], box[6:9], box[9:12]]
    extent = [sum(abs(a[k]) for a in axes) for k in range(3)]
    return [[centre[k] - extent[k] for k in range(3)], [centre[k] + extent[k] for k in range(3)]]


def aabb_box(bounds):
    centre = [(bounds[0][k] + bounds[1][k]) / 2 for k in range(3)]
    half = [max((bounds[1][k] - bounds[0][k]) / 2, .01) for k in range(3)]
    return centre + [half[0], 0, 0, 0, half[1], 0, 0, 0, half[2]]


def union(bounds):
    return [[min(b[0][k] for b in bounds) for k in range(3)], [max(b[1][k] for b in bounds) for k in range(3)]]


def units(catalog):
    """One LoD unit per building; very wide assets split into their parts."""
    result = []
    for asset in catalog['assets']:
        parts = [p for p in asset['parts'] if p['levels']]
        if not parts: continue
        local = union([r['bounds'] for p in parts for r in p['levels'].values()])
        world = obb_aabb(obb(local, asset['position'], asset['rotationY']))
        wide = max(world[1][0] - world[0][0], world[1][2] - world[0][2]) > UNIT_EXTENT
        heavy = sum(r.get('gpuBytesEstimate', 0) for _, r in level_sources({'parts': parts}, 'detail')) > UNIT_BYTES
        for group in ([[p] for p in parts] if (wide or heavy) and len(parts) > 1 else [parts]):
            bounds = union([r['bounds'] for p in group for r in p['levels'].values()])
            box = obb(bounds, asset['position'], asset['rotationY'])
            name = asset['id'] + ('/' + group[0]['id'] if len(group) < len(parts) else '')
            result.append({'id': name, 'asset': asset, 'parts': group, 'box': box, 'aabb': obb_aabb(box),
                           'ground': all(p.get('ground') for p in group)})
    return result


def level_sources(unit, level):
    """GLB records drawn for a unit at a level; fixed-level parts never change."""
    rows = []
    for part in unit['parts']:
        name = part.get('fixedLevel') or level
        record = part['levels'].get(name) or next(part['levels'][l] for l in reversed(LEVELS) if l in part['levels'])
        rows.append((part, record))
    return rows


class Builder:
    def __init__(self, source, dist, cache):
        self.source, self.dist, self.cache = Path(source), Path(dist), Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        (self.dist / 'tiles').mkdir(parents=True, exist_ok=True)
        self.written, self.stats = set(), {'tiles': 0, 'built': 0, 'reused': 0}

    def content(self, mode, sources):
        """sources: [(record, matrix, extras)]. Returns a content-addressed URI."""
        recipe = json.dumps([VERSION, mode, [(r['sha256'], m, e) for r, m, e in sources]], sort_keys=True)
        key = hashlib.sha256(recipe.encode()).hexdigest()
        pointer = self.cache / (key + '.uri')
        if pointer.exists() and (self.dist / 'tiles' / pointer.read_text()).exists():
            self.stats['reused'] += 1
            uri = pointer.read_text()
        else:
            merger = Merger(mode)
            for record, matrix, extras in sources:
                merger.add(self.source / record['uri'], matrix, extras)
            data = merger.glb()
            uri = f'{hashlib.sha256(data).hexdigest()}.glb'
            path = self.dist / 'tiles' / uri
            if not path.exists():
                tmp = path.with_suffix('.tmp'); tmp.write_bytes(data); tmp.replace(path)
            tmp = pointer.with_suffix('.tmp'); tmp.write_text(uri); tmp.replace(pointer)
            self.stats['built'] += 1
        self.written.add('tiles/' + uri)
        return uri

    def sources(self, unit, level):
        asset = unit['asset']
        matrix = yaw_matrix(asset['position'], asset['rotationY'])
        return [(record, matrix, {'asset': asset['id'], 'part': part['id'], 'ground': bool(part.get('ground')),
                                 **({'supportSurface':part['supportSurface']} if part.get('supportSurface') else {})})
                for part, record in level_sources(unit, level)]

    def unit_tile(self, unit):
        """District -> Walk -> Detail chain; identical consecutive levels collapse."""
        runs = []
        for level in LEVELS:
            signature = [r['sha256'] for _, r in level_sources(unit, level)]
            if runs and runs[-1]['signature'] == signature: runs[-1]['level'] = level
            else: runs.append({'signature': signature, 'level': level, 'coarsest': level})
        tile = None
        for run in reversed(runs):
            # A run draws (and is capped as) its finest level; rank records the coarsest level it stands in for.
            uri = self.content(run['level'], self.sources(unit, run['level']))
            node = {'boundingVolume': {'box': unit['box']}, 'geometricError': ERROR[run['level']] if tile else 0.,
                    'refine': 'REPLACE', 'content': {'uri': uri},
                    'extras': {'unit': unit['id'], 'level': run['level'], 'rank': LEVELS.index(run['coarsest']) + 1}}
            if tile: node['children'] = [tile]
            tile = node
            self.stats['tiles'] += 1
        return tile

    def proxy(self, members, mode):
        return self.content(mode, [s for unit in members for s in self.sources(unit, 'district')])

    def tree(self, members, bounds, size):
        """Quadtree over unit centres. Leaf cells hold a merged lite proxy of their units;
        inner nodes are empty so a view keeps at most one proxy cell plus the root resident."""
        aabb = union([u['aabb'] for u in members])
        # Empty inner nodes must refine whenever the root does, or they would draw nothing.
        node = {'boundingVolume': {'box': aabb_box(aabb)}, 'geometricError': ERROR['root'], 'refine': 'REPLACE',
                'extras': {'size': size, 'rank': 0}}
        self.stats['tiles'] += 1
        if size <= LEAF_SIZE or len(members) <= LEAF_UNITS:
            node['children'] = [self.unit_tile(u) for u in sorted(members, key=lambda u: u['id'])]
            node['content'] = {'uri': self.proxy(members, 'lite')}
            node['geometricError'] = ERROR['lite']
            node['extras']['proxy'] = 'lite'
        else:
            half = size / 2; quads = {}
            for u in members:
                c = [(u['aabb'][0][k] + u['aabb'][1][k]) / 2 for k in (0, 2)]
                key = (c[0] >= bounds[0] + half, c[1] >= bounds[1] + half)
                quads.setdefault(key, []).append(u)
            node['children'] = [self.tree(quads[key], (bounds[0] + half * key[0], bounds[1] + half * key[1]), half)
                                for key in sorted(quads)]
        return node


def fill_bounds(catalog, root, source):
    """Older catalogs omitted lower-level bounds; recover them from package metadata or the GLB."""
    from publication import inspect_glb
    for asset in catalog['assets']:
        manifest = Path(root) / 'build' / asset['id'] / 'package/manifest.json'
        known = {f['sha256']: f['bounds'] for f in json.loads(manifest.read_text()).get('files', [])} if manifest.exists() else {}
        for part in asset['parts']:
            for level in part['levels'].values():
                if 'bounds' not in level:
                    level['bounds'] = known.get(level['sha256']) or inspect_glb(Path(source) / level['uri'])['bounds']


def build(catalog, source, dist, cache):
    """Write tile content under dist/tiles; return (tileset, tile URIs, stats)."""
    builder = Builder(source, dist, cache)
    members = units(catalog)
    if not members: raise ValueError('No publishable parts to tile')
    world = union([u['aabb'] for u in members])
    size = LEAF_SIZE
    while size < max(world[1][0] - world[0][0], world[1][2] - world[0][2]): size *= 2
    # Ground and buildings get separate quadtrees: wide ground sections would otherwise
    # swell building cells, and a camera inside a cell's box forces that cell to refine.
    trees = [builder.tree(group, (world[0][0], world[0][2]), size)
             for group in ([u for u in members if not u['ground']], [u for u in members if u['ground']]) if group]
    # The root draws the whole town untextured, so the first frame shows everything.
    root = {'boundingVolume': {'box': aabb_box(world)}, 'geometricError': ERROR['root'], 'refine': 'REPLACE',
            'content': {'uri': builder.proxy(members, 'flat')}, 'children': trees, 'extras': {'proxy': 'flat', 'rank': 0}}
    tileset = {'asset': {'version': '1.1', 'gltfUpAxis': 'Z', 'generator': 'southport3d ' + VERSION},
               'extras': {'frame': 'East, up, south (metres); glTF content is already in this frame',
                          'geometricError': ERROR, 'textureCaps': CAP, 'units': len(members)},
               'geometricError': ERROR['root'] * 2, 'root': root}
    return tileset, builder.written, builder.stats


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def index_scene(root, dist=None, source=None):
    """Tile the last-good catalog and write the scene bootstrap; returns (scene, resource URIs)."""
    root = Path(root); dist = Path(dist or root / 'dist'); source = Path(source or dist)
    catalog = json.loads((source / 'catalog.json').read_text())
    fill_bounds(catalog, root, source)
    world = json.loads((root / 'viewer/world.json').read_text())
    tileset, written, _ = build(catalog, source, dist, root / 'build/tiles-cache')
    data = encoded(tileset)
    uri = f'tiles/{hashlib.sha256(data).hexdigest()}.json'
    if not (dist / uri).exists():
        tmp = dist / (uri + '.tmp'); tmp.write_bytes(data); tmp.replace(dist / uri)
    scene = {k: catalog[k] for k in ('worldOrigin', 'coordinateSystem', 'lodPolicy', 'viewerVersion')}
    scene.update(schema_version=3, catalogRevision=catalog['revision'], tileset=uri,
                 streaming={'budget': world.get('streaming', {}).get('budget', 1 << 30)},
                 assets=[{k: v for k, v in a.items() if k != 'parts'} for a in catalog['assets']])
    scene['revision'] = hashlib.sha256(encoded(scene)).hexdigest()
    tmp = dist / 'scene.json.tmp'; tmp.write_bytes(encoded(scene)); tmp.replace(dist / 'scene.json')
    return scene, written | {uri}


if __name__ == '__main__':
    import argparse, time
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='directory holding catalog.json and its GLBs (default dist/)')
    parser.add_argument('--dist', type=Path, help='directory receiving tiles/ and scene.json (default dist/)')
    args = parser.parse_args()
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    started = time.monotonic()
    scene, written = index_scene(Path(__file__).resolve().parents[1], args.dist, args.source)
    print(scene['tileset'], len(written), 'files', f'{time.monotonic() - started:.1f}s')
