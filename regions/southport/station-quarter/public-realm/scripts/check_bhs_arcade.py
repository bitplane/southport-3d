"""Check actual station/approach GLBs at the BHS arcade and Chapel seams."""
import json
import sys
from pathlib import Path

import numpy as np

repo = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(repo / 'tools'), str(repo / 'lib'), str(Path(__file__).parent)]
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations
from bhs_arcade_support import wall_x

spec = json.loads((repo / 'regions/southport/corporation-street/former-bhs/research/arcade-support.json').read_text())
surface = Elevations(repo / 'regions/southport/elevation/station-approach.json').surface('chapel-pedestrian')
station_layout = json.loads((repo / 'regions/southport/station-quarter/public-realm/research/layout.json').read_text())
identity = {'rotationY': 0, 'position': [0, 0, 0]}
station = repo / 'build/southport.station-quarter.public-realm/package'
approach = repo / 'build/southport.lord-street.christ-church-approach/package'


def triangles(path):
    return np.concatenate([t for t, _ in primitives(path, identity)])


def height(ts, x, y):
    a, b, c = ts[:, 0], ts[:, 1], ts[:, 2]
    z = -y  # The exported glTF frame is x, up, south.
    den = (b[:, 2]-c[:, 2])*(a[:, 0]-c[:, 0]) + (c[:, 0]-b[:, 0])*(a[:, 2]-c[:, 2])
    good = np.abs(den) > 1e-10
    u, v = np.zeros(len(den)), np.zeros(len(den))
    u[good] = ((b[good, 2]-c[good, 2])*(x-c[good, 0]) + (c[good, 0]-b[good, 0])*(z-c[good, 2]))/den[good]
    v[good] = ((c[good, 2]-a[good, 2])*(x-c[good, 0]) + (a[good, 0]-c[good, 0])*(z-c[good, 2]))/den[good]
    mask = good & (u >= -1e-7) & (v >= -1e-7) & (u+v <= 1+1e-7)
    values = u[mask]*a[mask, 1] + v[mask]*b[mask, 1] + (1-u[mask]-v[mask])*c[mask, 1]
    assert len(values) and np.ptp(values) < 2e-4, (x, y, values)
    return float(values.mean())


for level in ('detail', 'walk', 'district'):
    st = triangles(station / f'middle-ground-{level}.glb')
    ap = triangles(approach / f'passage-ground-{level}.glb')
    width, datum = spec['width_m'], spec['building_grade_m']
    errors = []
    for y in (-119., -115., -110., -105., -100., -95.01):
        wall = wall_x(spec, y)
        inner = height(st, wall-.01, y)
        outer = height(st, wall-width-.01, y)
        assert abs(inner-datum) < .004, (level, y, inner, datum)
        assert abs(outer-surface.height(wall-width-.01, y)) < .002, (level, y, outer)
        if y >= -115:  # Farther south, the opposite placeholder owns this edge.
            west0, west1 = station_layout['ground_polygons'][3][0], station_layout['ground_polygons'][3][3]
            edge = west0[0]+(y-west0[1])*(west1[0]-west0[0])/(west1[1]-west0[1])
            hs, ha = height(st, edge+.001, y), height(ap, edge-.001, y)
            errors.append(abs(hs-ha))
            assert abs(hs-ha) < .003, (level, y, 'west arcade edge', hs, ha)
    # Opposite samples straddle the station/approach boundary without relying
    # on a single shared edge hit or on one owner's Blender source geometry.
    for offset in (.1, .6, 1., 1.5, 1.9, 2.1, 3.0):
        ys, ya = -95.001, -94.999
        hs = height(st, wall_x(spec, ys)-offset, ys)
        ha = height(ap, wall_x(spec, ya)-offset, ya)
        errors.append(abs(hs-ha))
        assert abs(hs-ha) < .003, (level, offset, hs, ha)
    for y in (-94.9, -94., -93.1):
        assert abs(height(ap, wall_x(spec, y)-.01, y)-datum) < .004, (level, y)
    # The south fan and the Chapel threshold share this diagonal boundary.
    a, b = spec['front_threshold_outer'], spec['wall_south']
    for t in (.1, .3, .5, .7, .9):
        x, y = a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])
        hs, ha = height(st, x-.001, y), height(ap, x+.001, y)
        errors.append(abs(hs-ha))
        assert abs(hs-ha) < .003, (level, t, hs, ha)
    print(level, 'BHS arcade exported contacts pass; max offset-sample seam difference', max(errors), 'm')
