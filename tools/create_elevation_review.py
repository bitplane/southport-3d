#!/usr/bin/env python3
"""Publish a disposable measured-terrain review without changing the town scene."""
import json
import math
from pathlib import Path
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'lib'))
from southport3d.terrain import Terrain


def main():
    out = ROOT/'dist/reviews/elevation'; out.mkdir(parents=True, exist_ok=True)
    t = Terrain(ROOT/'regions/southport/elevation/survey/terrain.json')
    c, s = math.cos(math.radians(43.5293)), math.sin(math.radians(43.5293))
    samples = np.load(ROOT.parent/'output/elevation/ground-samples.npz')['samples']
    lo = np.floor(samples[:, :2].min(axis=0)/5)*5
    hi = np.ceil(samples[:, :2].max(axis=0)/5)*5
    east, north = np.arange(lo[0], hi[0]+1, 5), np.arange(lo[1], hi[1]+1, 5)
    points = []
    for n in north:
        for e in east:
            x, y = c*e+s*n, -s*e+c*n
            points.append([e, t.height(x, y), -n])
    np.array(points, dtype='<f4').tofile(out/'terrain.bin')
    # Existing ground is diagnostic point geometry; it is not moved here.
    old = samples[:, [0, 2, 1]].astype('<f4'); old[:, 2] *= -1
    old.tofile(out/'published-ground.bin')
    roads = []
    for path in (ROOT/'regions/southport').rglob('research/layout.json'):
        recipe = json.loads(path.read_text())
        for road in recipe.get('roads', []):
            if not isinstance(road, dict):
                continue
            points = road.get('points', [])
            for a, b in zip(points, points[1:]):
                if len(a) != 2 or len(b) != 2:
                    continue
                length = math.dist(a, b)
                chain = []
                for f in np.linspace(0, 1, max(2, math.ceil(length/2))):
                    x, y = a[0]+f*(b[0]-a[0]), a[1]+f*(b[1]-a[1])
                    try:
                        z = t.height(x, y)+.1
                    except ValueError:
                        chain = []; break
                    chain.append([c*x-s*y, z, -(s*x+c*y)])
                for aa, bb in zip(chain, chain[1:]):
                    roads.extend([aa, bb])
    np.array(roads, dtype='<f4').tofile(out/'road-guides.bin')
    report = json.loads((ROOT.parent/'output/elevation/audit.json').read_text())
    (out/'review.json').write_text(json.dumps({'columns': len(east), 'rows': len(north),
        'localZeroODN': t.datum, 'datumStatus': t.spec['datum_status'], 'parts': report['parts'],
        'origin': json.loads((ROOT/'dist/catalog.json').read_text())['worldOrigin']}))
    # Review isolated checked packages without changing the live town catalog.
    model_files=[]
    for area,kinds in [('hoghton-street',['public-realm','frontage-placeholders']),
                       ('leicester-quarter',['public-realm','frontage-placeholders']),
                       ('stanley-street',['public-realm','frontage-placeholders']),
                       ('west-street',['public-realm','frontage-placeholders']),
                       ('lord-street',['corridor-public-realm','corridor-placeholders']),
                       ('nevill-street',['public-realm','frontage-placeholders']),
                       ('station-quarter',['public-realm','frontage-placeholders'])]:
        for kind in kinds:
            asset=f'southport.{area}.{kind}';package=ROOT/'build'/asset/'package'
            manifest=package/'manifest.json'
            if not manifest.exists():continue
            # Only terrain packages checked in this migration are included.
            recipe=ROOT/'regions/southport'/area/kind/'research/layout.json'
            if 'elevation_plan' not in json.loads(recipe.read_text()):continue
            for item in json.loads(manifest.read_text())['files']:
                if item['level']!='district':continue
                destination=Path('models')/asset/Path(item['path']).name
                (out/destination).parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(package/item['path'],out/destination)
                model_files.append(str(destination))
    (out/'models.json').write_text(json.dumps(model_files))
    shutil.copy2(ROOT/'viewer/elevation-review.html', out/'index.html')
    print('http://127.0.0.1:8765/reviews/elevation/')


if __name__ == '__main__':
    main()
