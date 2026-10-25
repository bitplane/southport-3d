"""Run with blender -b --python-exit-code 1 --python tests/blender_bake_projection.py.
Checks the ray-direction defect, bounds, topology and atlas of the real reducer.
"""
from pathlib import Path
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'lib')]
from southport3d.geometry import Mesh
from blender_lod import reduce
m=Mesh('Source frame bounds');m.box((0,1.5,0),(1.2,3,.32));source=m.finish([])
base=dict(strategy='replace',shape='box',uv='box',bake=True,cage_extrusion_m=.4)
old=reduce(source,'legacy',base,{'texture_size':128},ROOT)
new=reduce(source,'straight',dict(base,bake_projection='face-normal'),{'texture_size':128},ROOT)
def skew(ob):
    return max(1-ob.data.vertices[i].normal.dot(p.normal) for p in ob.data.polygons for i in p.vertices)
assert skew(old)>.1,'Fixture no longer reproduces the implicit corner cage'
assert skew(new)<1e-6,'Projection rays still skew around receiver edges'
assert len(new.data.polygons)==len(old.data.polygons)==12
for axis in range(3):
    assert abs(min(v.co[axis] for v in new.data.vertices)-min(v.co[axis] for v in old.data.vertices))<1e-6
    assert abs(max(v.co[axis] for v in new.data.vertices)-max(v.co[axis] for v in old.data.vertices))<1e-6
assert all(0<=c<=1 for uv in new.data.uv_layers.active.data for c in uv.uv)
# Geometric edges remain closed even though corners have face-local normals.
from collections import Counter
edges=Counter()
for p in new.data.polygons:
    points=[tuple(round(x,6) for x in new.data.vertices[i].co) for i in p.vertices]
    for a,b in zip(points,points[1:]+points[:1]):edges[tuple(sorted((a,b)))]+=1
assert all(n==2 for n in edges.values()),'Receiver developed an open geometric edge'
print('Face-normal projection: unchanged closed box and 12 triangles, zero corner ray skew')
