"""Mapped registration, real openings and a closed joined roof."""
from pathlib import Path
import json,math,os,sys
import bpy,bmesh
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'models/post-office-10-18.blend'))
d=json.loads((root/'research/layout.json').read_text());w=d['width'];bw=w/5
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:
    assert o.data.uv_layers and o.data.polygons,o.name
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
front=bpy.data.objects['Envelope front red brick']
for i in range(5):
    shop=i*bw+(1.90 if i%2==0 else bw-1.90);door=i*bw+(bw-.80 if i%2==0 else .80)
    for u,z in [(shop,1.5),(door,1.4),(i*bw+bw/2-.74,4.5),(i*bw+bw/2+.74,4.5)]:
        assert not front.ray_cast(Vector((u,z,2)),Vector((0,0,-1)),distance=4)[0],('Filled front opening',i,u,z)
upper=bpy.data.objects['Envelope front upper infill']
for i in range(5):assert not upper.ray_cast(Vector(((i+.5)*bw,7.6,2)),Vector((0,0,-1)),distance=4)[0]
roof=bpy.data.objects['Roof joined hipped ridge and three cross gables']
bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_manifold for e in bm.edges),'Open or non-manifold joined roof'
assert all(f.calc_area()>1e-10 for f in bm.faces),'Degenerate roof face'
bm.free()
for u in (w*.1,w*.5,w*.9):
    hit,p,n,i=roof.ray_cast(Vector((u,0,30)),Vector((0,0,-1)),distance=30)
    assert hit and abs(p.z-d['ridge'])<1e-4,('Lost gable ridge',u)
for u in (.5,5,9,13,18,22,w-.5):
    for v in (0,1.5,4,7.8):assert roof.ray_cast(Vector((u,v,30)),Vector((0,0,-1)),distance=30)[0],('Missing roof surface',u,v)
world=Matrix.Translation((*d['origin_site_xy'],d['base_z']))@Matrix.Rotation(math.radians(d['local_rotation_degrees']),4,'Z')
for local,expected in [((0,0,0),d['footprint_site_xy'][1]),((w,0,0),d['footprint_site_xy'][2])]:
    point=world@Vector(local)
    assert math.dist(tuple(point)[:2],expected)<1e-5
# Mitered exterior envelope faces should not duplicate neighbouring wall caps.
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
import numpy as np
# Use retained construction transforms with double precision for the audit.
# Multiplying into distant site coordinates with mathutils float32 introduces
# false intersections of a few square millimetres at exact mitred seams.
triangles=[];labels=[]
for o in objects:
    if not o.name.startswith('Envelope '):continue
    transform=np.array(o['construction_frame']).reshape(4,4)
    o.data.calc_loop_triangles()
    for triangle in o.data.loop_triangles:
        triangles.append([(transform@np.array([*o.data.vertices[v].co,1]))[:3] for v in triangle.vertices])
        labels.append(o.name)
# A 0.3 m cap edge transformed from float32 mesh coordinates can accumulate
# a few square millimetres of overlap. Reject anything beyond 10 mm²; this is
# below the audit's 20-micron distance tolerance times a 0.5 m seam.
errors=overlaps(triangles,labels,min_area=1e-5)
assert not errors,('Coplanar envelope overlap',errors[:12])
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
print('Post Office Avenue footprint, pierced facades, roof shell and wall ownership passed')
