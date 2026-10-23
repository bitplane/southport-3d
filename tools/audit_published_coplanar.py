#!/usr/bin/env python3
"""Audit immutable published GLBs in viewer coordinates; never changes assets.

Requires NumPy, Pillow (existing GLB reader), and g++. Reports are review
candidates, not a visibility test. Run each uniform viewing level separately.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
import numpy as np
from check_lods import read_glb, array, matrix

ROOT = Path(__file__).resolve().parents[1]


def primitives(path, asset):
    doc, binary = read_glb(path)
    angle = asset['rotationY']
    c, s = np.cos(angle), np.sin(angle)
    base = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.]])
    base[:3, 3] = asset['position']

    def visit(index, parent):
        node = doc['nodes'][index]
        if node.get('extensions') or 'skin' in node:
            raise ValueError(f'Unsupported node extensions: {path}: {index}')
        transform = parent @ matrix(node)
        if 'mesh' in node:
            for number, primitive in enumerate(doc['meshes'][node['mesh']]['primitives']):
                if primitive.get('mode', 4) != 4 or primitive.get('extensions') or primitive.get('targets'):
                    raise ValueError(f'Unsupported primitive: {path}: {index}/{number}')
                p = array(doc, binary, primitive['attributes']['POSITION']).astype(float)
                p = p @ transform[:3, :3].T + transform[:3, 3]
                idx = array(doc, binary, primitive['indices']).ravel().reshape(-1, 3)
                triangles = np.ascontiguousarray(p[idx], dtype='<f8')
                # Three.js reverses front-face winding for mirrored instances.
                if np.linalg.det(transform[:3, :3]) < 0:
                    triangles = np.ascontiguousarray(triangles[:, [0, 2, 1]])
                if not np.isfinite(triangles).all():
                    raise ValueError(f'Non-finite vertices: {path}')
                material = doc.get('materials', [])[primitive['material']]
                yield triangles, {'node': node.get('name', str(index)), 'node_index': index,
                                  'primitive': number, 'material': material.get('name'),
                                  'double_sided': material.get('doubleSided', False)}
        for child in node.get('children', []):
            yield from visit(child, transform)
    for index in doc['scenes'][doc.get('scene', 0)]['nodes']:
        yield from visit(index, base)


def audit_level(catalog, dist, level, executable, out):
    started = time.monotonic()
    with tempfile.TemporaryDirectory(dir=out, prefix=level+'-') as tmp:
        tmp = Path(tmp); geometry = tmp/'triangles.bin'; pairs = tmp/'pairs.bin'
        sources = []; count = 0; assets = Counter()
        with geometry.open('wb') as stream:
            for asset in catalog['assets']:
                for part in asset['parts']:
                    actual = part.get('fixedLevel', level)
                    row = part['levels'][actual]; path = dist/row['uri']
                    if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                        raise ValueError(f'Published hash mismatch: {path}')
                    part_count = 0
                    for triangles, source in primitives(path, asset):
                        source.update(asset=asset['id'], part=part['id'], level=actual,
                                      uri=row['uri'], sha256=row['sha256'], start=count,
                                      count=len(triangles))
                        sources.append(source); triangles.tofile(stream)
                        count += len(triangles); assets[asset['id']] += len(triangles)
                        part_count += len(triangles)
                    if part_count != row['triangles']:
                        raise ValueError(f'Catalog triangle count mismatch: {path}')
                print(f'{level}: loaded {asset["id"]}: {assets[asset["id"]]} triangles', flush=True)
        subprocess.run([str(executable), str(geometry), str(pairs)], check=True)
        triangles = np.memmap(geometry, dtype='<f8', mode='r', shape=(count, 3, 3))
        starts = np.array([s['start'] for s in sources]); groups = {}
        dtype = np.dtype([('a', '<u4'), ('b', '<u4'), ('area', '<f8')])
        hits = np.fromfile(pairs, dtype=dtype)
        owners_a = np.searchsorted(starts, hits['a'], side='right')-1
        owners_b = np.searchsorted(starts, hits['b'], side='right')-1
        for hit, ai, bi in zip(hits, owners_a, owners_b):
            key = (int(ai), int(bi)); a = int(hit['a']); b = int(hit['b'])
            low = np.maximum(triangles[a].min(axis=0), triangles[b].min(axis=0))
            high = np.minimum(triangles[a].max(axis=0), triangles[b].max(axis=0))
            g = groups.setdefault(key, {'a': int(ai), 'b': int(bi), 'triangle_pairs': 0,
                                       'pair_area_sum_m2': 0., 'bounds': [low.copy(), high.copy()], 'examples': []})
            g['triangle_pairs'] += 1; g['pair_area_sum_m2'] += float(hit['area'])
            g['bounds'][0] = np.minimum(g['bounds'][0], low)
            g['bounds'][1] = np.maximum(g['bounds'][1], high)
            if len(g['examples']) < 3:
                normal = np.cross(triangles[a, 1]-triangles[a, 0], triangles[a, 2]-triangles[a, 0])
                normal /= np.linalg.norm(normal)
                g['examples'].append({'triangle_a': a-sources[ai]['start'], 'triangle_b': b-sources[bi]['start'],
                                      'near_viewer_xyz': ((low+high)/2).tolist(), 'normal': normal.tolist(), 'overlap_area_m2': float(hit['area'])})
        findings = sorted(groups.values(), key=lambda g: g['pair_area_sum_m2'], reverse=True)
        for i, g in enumerate(findings):
            g['id'] = f'{level}-{i+1:06d}'
            g['bounds'] = [v.tolist() for v in g['bounds']]
            g['cross_asset'] = sources[g['a']]['asset'] != sources[g['b']]['asset']
        result = {'level': level, 'triangles': count, 'assets': dict(assets), 'sources': sources,
                  'triangle_pairs': len(hits), 'findings': findings, 'seconds': time.monotonic()-started}
        (out/f'{level}.json').write_text(json.dumps(result, indent=2)+'\n')
        print(f'{level}: {len(hits)} overlapping triangle pairs in {len(findings)} primitive-pair groups', flush=True)
        return result


def write_report(catalog, results, out):
    lines = ['# Published coplanar-overlap audit', '', f'Catalog revision: `{catalog["revision"]}`.', '',
             'Coordinates are viewer East/up/south metres. Scan includes node transforms, instances and catalog placement. '
             'Each level is one complete map, including cross-asset pairs. Fixed-level parts retain their fixed level.', '',
             'These are geometric candidates, not confirmed visible defects. Buried same-facing surfaces remain in the report. '
             'Opposite-facing seams are excluded, including double-sided materials. Mixed-LoD combinations, texture/decal depth bias '
             'and non-coplanar intersections are not tested. Plane tolerance: 0.00002 m; minimum overlap: 0.000001 m²; '
             'normal dot product ≥ 0.99999999. Tiny/degenerate triangles below the area threshold cannot generate findings.', '',
             'Area is the sum over triangle pairs, not union area; multiple duplicate layers can count an area more than once. '
             'Example coordinates locate the intersecting bounding boxes, not a guaranteed visible surface point.', '',
             '| Level | Triangles | Triangle pairs | Primitive-pair groups | Cross-asset groups |',
             '|---|---:|---:|---:|---:|']
    for r in results:
        lines.append(f'| {r["level"]} | {r["triangles"]:,} | {r["triangle_pairs"]:,} | {len(r["findings"]):,} | {sum(g["cross_asset"] for g in r["findings"]):,} |')
    for r in results:
        sources = r['sources']; lines += ['', f'## {r["level"]}: repair queue by asset', '', '| Asset | Groups touching asset | Pair-area sum m² |', '|---|---:|---:|']
        totals = {}
        for g in r['findings']:
            for asset in {sources[g['a']]['asset'], sources[g['b']]['asset']}:
                v = totals.setdefault(asset, [0, 0.]); v[0] += 1; v[1] += g['pair_area_sum_m2']
        for asset, v in sorted(totals.items(), key=lambda item: -item[1][1]):
            lines.append(f'| {asset} | {v[0]} | {v[1]:.4f} |')
        lines += ['', '### Largest candidates (cross-asset first)', '', '| ID | Surfaces | Pair-area m² | Near viewer XYZ |', '|---|---|---:|---|']
        ordered = sorted(r['findings'], key=lambda g: (not g['cross_asset'], -g['pair_area_sum_m2']))
        for g in ordered[:100]:
            names = [f'{sources[g[k]]["asset"]}/{sources[g[k]]["part"]}: {sources[g[k]]["node"]} (primitive {sources[g[k]]["primitive"]})' for k in ['a', 'b']]
            pos = ', '.join(f'{v:.3f}' for v in g['examples'][0]['near_viewer_xyz'])
            lines.append(f'| {g["id"]} | '+ ' ↔ '.join(n.replace('|', '/') for n in names)+f' | {g["pair_area_sum_m2"]:.6f} | {pos} |')
        lines += ['', f'Complete findings and exact GLB/node/primitive/triangle identifiers: [{r["level"]}.json]({r["level"]}.json).']
    (out/'report.md').write_text('\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=ROOT/'dist')
    parser.add_argument('--output', type=Path, default=ROOT/'build/coplanar-audit')
    parser.add_argument('--levels', nargs='+', choices=['detail', 'walk', 'district'], default=['district', 'walk', 'detail'])
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((args.dist/'catalog.json').read_text())
    (out/'catalog.json').write_text(json.dumps(catalog, indent=2)+'\n')
    executable = out/'coplanar-scan'
    subprocess.run(['g++', '-O3', '-std=c++17', str(ROOT/'tools/coplanar_scan.cpp'), '-o', str(executable)], check=True)
    results = []
    for level in args.levels:
        results.append(audit_level(catalog, args.dist, level, executable, out))
        write_report(catalog, results, out)
    print(f'Report: {out / "report.md"}')

if __name__ == '__main__':
    main()
