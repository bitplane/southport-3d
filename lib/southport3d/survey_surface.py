"""Bounded, piecewise-planar terrain surface with a shared metric mesh grid.

Triangulation follows the same grid and diagonals for every ownership polygon.
Material boundaries therefore cannot erase slopes or disagree at tile seams.
The survey remains a reference; water/decks/steps must use explicit surfaces.
"""
from functools import lru_cache
import math

from .planar import area, halfplane
from .terrain import Terrain, GroundControls


class SurveySurface:
    def __init__(self, terrain_path, name, bounds, grid_m=5., offset_m=0., refinements=(), controlled=False):
        self.terrain = GroundControls(terrain_path) if controlled else Terrain(terrain_path)
        if controlled and (refinements or grid_m != self.terrain.spacing):
            raise ValueError("Control surfaces use the shared coarse grid without refinements")
        self.name, self.bounds, self.spacing, self.offset = name, bounds, grid_m, offset_m
        if len(bounds) != 4 or not all(math.isfinite(v) for v in (*bounds, grid_m, offset_m)):
            raise ValueError('Invalid survey surface bounds')
        if bounds[0] >= bounds[1] or bounds[2] >= bounds[3] or grid_m <= 0:
            raise ValueError('Empty survey surface')
        self._stitch_parent = None
        self.refinements = []
        for item in refinements:
            b, step = item['bounds'], item['grid_m']
            if any(abs(v/grid_m-round(v/grid_m))>1e-8 for v in b):
                raise ValueError('Refinement boundary must follow parent grid')
            if step>=grid_m or abs(grid_m/step-round(grid_m/step))>1e-8:
                raise ValueError('Refinement must divide parent grid')
            if not self.contains(b[0],b[2]) or not self.contains(b[1],b[3]):
                raise ValueError('Refinement outside surface')
            if any(max(b[0],r.bounds[0])<min(b[1],r.bounds[1]) and max(b[2],r.bounds[2])<min(b[3],r.bounds[3]) for r in self.refinements):
                raise ValueError('Overlapping terrain refinements')
            child = SurveySurface(terrain_path, name+' refinement', b, step, offset_m)
            child.terrain = self.terrain
            child._stitch_parent = self
            self.refinements.append(child)

    def contains(self, x, y, tolerance=1e-7):
        a, b, c, d = self.bounds
        return a-tolerance <= x <= b+tolerance and c-tolerance <= y <= d+tolerance

    @lru_cache(maxsize=262144)
    def node(self, i, j):
        if self._stitch_parent:
            x,y=i*self.spacing,j*self.spacing
            a,b,c,d=self.bounds
            if min(abs(x-a),abs(x-b),abs(y-c),abs(y-d))<1e-8:
                return self._stitch_parent._coarse_height(x,y)
        return self.terrain.height(i*self.spacing, j*self.spacing)+self.offset

    def height(self, x, y):
        if not self.contains(x, y):
            raise ValueError(f'{self.name}: outside declared bounds at {(x, y)}')
        for child in self.refinements:
            if child.contains(x,y):
                return child.height(x,y)
        return self._coarse_height(x,y)

    def _coarse_height(self,x,y):
        gx, gy = x/self.spacing, y/self.spacing
        i, j = math.floor(gx), math.floor(gy)
        u, v = gx-i, gy-j
        if u+v <= 1:
            return sum(w*self.node(a,b) for a,b,w in [(i,j,1-u-v),(i+1,j,u),(i,j+1,v)] if w>1e-12)
        return sum(w*self.node(a,b) for a,b,w in [(i+1,j+1,u+v-1),(i,j+1,1-u),(i+1,j,1-v)] if w>1e-12)

    def lift_triangle(self, triangle):
        for x, y in triangle:
            if not self.contains(x, y):
                raise ValueError(f'{self.name}: triangle outside bounds')
        g = self.spacing
        imin, imax = math.floor(min(p[0] for p in triangle)/g), math.floor(max(p[0] for p in triangle)/g)
        jmin, jmax = math.floor(min(p[1] for p in triangle)/g), math.floor(max(p[1] for p in triangle)/g)
        for i in range(imin, imax+1):
            x0, x1 = i*g, (i+1)*g
            strip = halfplane(halfplane(list(triangle), (x0, 1), (x0, 0)), (x1, 0), (x1, 1))
            if len(strip) < 3 or area(strip) < 1e-10:
                continue
            for j in range(jmin, jmax+1):
                y0, y1 = j*g, (j+1)*g
                cell = halfplane(halfplane(strip, (0, y0), (1, y0)), (1, y1), (0, y1))
                if len(cell) < 3 or area(cell) < 1e-10:
                    continue
                refined=next((r for r in self.refinements if r.contains((x0+x1)/2,(y0+y1)/2)),None)
                if refined:
                    for k in range(1,len(cell)-1):
                        yield from refined.lift_triangle([cell[0],cell[k],cell[k+1]])
                    continue
                for side in (True, False):
                    poly = halfplane(cell, (x1, y0), (x0, y1), side)
                    for k in range(1, len(poly)-1):
                        tri = [poly[0], poly[k], poly[k+1]]
                        if area(tri) > 1e-10:
                            yield [(x, y, self.height(x, y)) for x, y in tri]

    def edge_points(self, a, b):
        fractions = {0., 1.}
        g = self.spacing
        # Grid axes and diagonals x+y = n*g cover every piecewise-planar break.
        for start, end in [(a[0], b[0]), (a[1], b[1]), (sum(a[:2]), sum(b[:2]))]:
            if abs(end-start) < 1e-12:
                continue
            for k in range(math.floor(min(start, end)/g)+1, math.ceil(max(start, end)/g)):
                t = (k*g-start)/(end-start)
                if 0 < t < 1:
                    fractions.add(t)
        for child in self.refinements:
            for start,end in [(a[0],b[0]),(a[1],b[1]),(sum(a[:2]),sum(b[:2]))]:
                if abs(end-start)<1e-12:continue
                g=child.spacing
                for k in range(math.floor(min(start,end)/g)+1,math.ceil(max(start,end)/g)):
                    t=(k*g-start)/(end-start)
                    x,y=a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])
                    if 0<t<1 and child.contains(x,y):fractions.add(t)
        for t in sorted(fractions):
            x, y = a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])
            yield x, y, self.height(x, y)
