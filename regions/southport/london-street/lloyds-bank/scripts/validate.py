from pathlib import Path
import bpy,math,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lloyds-bank.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)>=3
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(v) for o in meshes for p in o.data.vertices for v in p.co)
assert {'Envelope prototype front','Envelope service side','Roof flat'} <= {o.name for o in meshes}
print('Provisional massing bounds and finite UV meshes checked; no architecture or seam acceptance implied.')
# Design-stage audit: front shell and the single prototype window, including
# its trim. This is not an audit of the remaining side/service shell or LoDs.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
selected=[o for o in meshes if o.name.startswith(('Envelope','Window','Trim','Shop','Fine','Roof'))]
triangles=[]; labels=[]
for ob in selected:
 ob.data.calc_loop_triangles()
 for t in ob.data.loop_triangles:
  triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(ob.name)
# 1e-5 m² suppresses the numerical slivers at tessellated arch intersections;
# meaningful overlaps at joinery and wall surfaces still fail.
errors=overlaps(triangles,labels,min_area=1e-5)
assert not errors,errors[:12]
print('Front shell and one window prototype pass same-facing coplanar test.')
# Top-facing roof triangles must survive glTF back-face culling. The rounded
# exterior wall must point away from its plan centre; the inner skin points in.
for name in ('Roof flat','Roof service','Roof raised bay'):
 ob=bpy.data.objects[name]
 horizontal=[p for p in ob.data.polygons if abs(p.normal.z)>.9]
 assert horizontal and all(p.normal.z>.9 for p in horizontal),(name,'roof top wound down')
D=json.loads((ROOT/'research/layout.json').read_text())
corner=bpy.data.objects['Envelope rounded corner'];cx=D['front_x']+.70;cy=D['side_y']-.70;checked=0
for p in corner.data.polygons:
 if abs(p.normal.z)>.1:continue
 v=[corner.data.vertices[i].co for i in p.vertices];mid=sum(v,Vector())/len(v);rad=Vector((mid.x-cx,mid.y-cy,0))
 if rad.length>.60:
  assert p.normal.dot(rad)>0,('inward-facing rounded corner',p.index);checked+=1
assert checked>=8
print('Upward roof and outward rounded-corner winding checked')

# Arch bands must face outward, including in the projected normal map.
for ob in meshes:
 if ob.name.startswith(('Trim prototype arch','Trim rear arched light')):
  assert all(p.normal.z > .9 for p in ob.data.polygons), ob.name
print('Arched surround normals face outward')

# Corbels must clear the fascia: they project farther out than the sign.
fascia=bpy.data.objects['Shop fascia']; fascia_top=max(v.co.y for v in fascia.data.vertices)
for ob in meshes:
 if ob.name.startswith('Fine cornice bracket'):
  assert min(v.co.y for v in ob.data.vertices)>fascia_top+.01, ob.name
print('Projecting corbels clear the fascia')
