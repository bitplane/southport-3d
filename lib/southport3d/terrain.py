"""Measured bare-earth reference, not an implicit walkable surface.

Coordinates are memorial site XY metres. Callers must choose whether a feature
belongs on terrain, a bridge, a building floor or a water surface. Elevations
are orthometric ODN, converted to the documented local datum on request.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np


def validate_tile(data):
    if set(data.files) != {'odn_mm', 'valid'}:
        raise ValueError('Unexpected terrain payload')
    z, valid = data['odn_mm'], data['valid']
    if z.dtype != np.int16 or valid.dtype != np.bool_ or z.ndim != 2 or z.shape != valid.shape:
        raise ValueError('Invalid terrain tile types or dimensions')
    if min(z.shape) < 2:
        raise ValueError('Empty terrain tile')


class Terrain:
    def __init__(self, path):
        self.path = Path(path)
        self.spec = json.loads(self.path.read_text())
        if self.spec['schema_version'] != 1 or self.spec['crs'] != 'EPSG:27700':
            raise ValueError('Unsupported terrain frame')
        self.matrix = self.spec['site_xy_to_bng_affine']
        self.datum = self.spec['local_zero_odn_m']
        self.tiles = self.spec['tiles']
        self.tile_size = self.spec['tile_size_m']
        self.resolution = self.spec['resolution_m']

    @lru_cache(maxsize=16)
    def _tile(self, key):
        if key not in self.tiles:
            raise ValueError('Terrain outside measured coverage: '+key)
        with np.load(self.path.parent/self.tiles[key]['path'], allow_pickle=False) as data:
            validate_tile(data)
            return data['odn_mm'].copy(), data['valid'].copy()

    def bng(self, x, y):
        m = self.matrix
        return x*m[0][0]+y*m[1][0]+m[2][0], x*m[0][1]+y*m[1][1]+m[2][1]

    def _pixel(self, e, n):
        size, res = self.tile_size, self.resolution
        west, south = math.floor(e/size)*size, math.floor(n/size)*size
        key = f'{west}_{south}'
        z, valid = self._tile(key)
        col, row = int(math.floor((e-west)/res)), int(math.floor((south+size-n)/res))
        if not valid[row, col]:
            raise ValueError(f'No terrain return at {e}, {n}')
        return float(z[row, col])/1000

    def height_odn(self, x, y):
        e, n = self.bng(x, y)
        res = self.resolution
        west = math.floor(e/res-.5)*res+.5*res
        south = math.floor(n/res-.5)*res+.5*res
        u, v = (e-west)/res, (n-south)/res
        # Resolve each pixel independently so tile borders never clamp or seam.
        return sum(weight*self._pixel(ee, nn) for ee, nn, weight in [
            (west, south, (1-u)*(1-v)), (west+res, south, u*(1-v)),
            (west, south+res, (1-u)*v), (west+res, south+res, u*v)] if weight > 1e-12)

    def height(self, x, y):
        return self.height_odn(x, y)-self.datum


class GroundControls:
    """Editable coarse site heights, independent of the reference raster at build time."""
    def __init__(self, path):
        self.spec = json.loads(Path(path).read_text())
        if self.spec.get('schema_version') != 1:
            raise ValueError('Unsupported ground controls')
        self.spacing = self.spec['grid_m']
        self.nodes = self.spec['heights_m']
        if self.spacing <= 0 or not all(math.isfinite(v) for v in self.nodes.values()):
            raise ValueError('Invalid ground controls')

    def height(self, x, y):
        gx, gy = x/self.spacing, y/self.spacing
        i, j = math.floor(gx), math.floor(gy)
        u, v = gx-i, gy-j
        def node(a,b):
            try: return self.nodes[f'{a},{b}']
            except KeyError: raise ValueError(f'Missing ground control {(a,b)}') from None
        if u+v <= 1:
            return sum(w*node(a,b) for a,b,w in [(i,j,1-u-v),(i+1,j,u),(i,j+1,v)] if w>1e-12)
        return sum(w*node(a,b) for a,b,w in [(i+1,j+1,u+v-1),(i,j+1,1-u),(i+1,j,1-v)] if w>1e-12)
