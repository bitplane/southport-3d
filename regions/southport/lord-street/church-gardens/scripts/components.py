"""Authored garden silhouettes; planting dimensions are supplied by the layout."""
import math
from southport3d.geometry import Mesh
from southport3d.street import furniture
from southport3d.landscape import tree


def hedge(level='detail', name='Hedge'):
    mesh = Mesh(name)
    segments, rings = {'detail': (10, 6), 'walk': (7, 4), 'district': (4, 3)}[level]
    # Unit-length hedge uses a solid low envelope and rounded, irregular crown.
    mesh.box((0, 0, .38), (1, .75, .76), 0)
    mesh.ellipsoid((0, 0, .69), (.53, .43, .35), 1, segments, rings)
    if level != 'district':
        for x, y, z in [(-.3, -.12, .79), (.3, .08, .84)]:
            mesh.ellipsoid((x, y, z), (.25, .33, .25), 2, segments, rings)
    return mesh


def lantern(level='detail', name='Lantern'):
    mesh = Mesh(name)
    n = {'detail': 16, 'walk': 8, 'district': 5}[level]
    profile = [(0, .13), (.12, .13), (.17, .09), (.6, .075), (2.9, .045), (3.08, .075)]
    mesh.lathe((0, 0), profile if level != 'district' else [profile[i] for i in (0, 2, 4, 5)], n, 0)
    # Four-sided historic lantern, tapered glass, cap and finial. Glass is opaque
    # pale grey; no invented glow or baked directional light.
    mesh.add([(-.10,-.10,3.08),(.10,-.10,3.08),(.10,.10,3.08),(-.10,.10,3.08),
              (-.21,-.21,3.57),(.21,-.21,3.57),(.21,.21,3.57),(-.21,.21,3.57)],
             [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],2)
    for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:
        mesh.tube([(x*.10,y*.10,3.08),(x*.21,y*.21,3.57)],.018,0,max(4,n//2))
    mesh.lathe((0,0),[(3.55,.30),(3.60,.30),(3.78,.07),(3.83,.055)],4,0)
    mesh.ellipsoid((0,0,3.87),(.06,.06,.08),0,n,max(3,n//2))
    return mesh


def build_lod(name, settings, asset_dir):
    kind, level = settings['kind'], settings['level']
    factory = {'tree': tree, 'hedge': hedge, 'lantern': lantern}.get(kind)
    mesh = factory(level, name) if factory else furniture(kind, level, name)
    return mesh.finish([])
