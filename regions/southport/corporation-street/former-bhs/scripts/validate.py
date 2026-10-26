from pathlib import Path
import bpy, math, os, sys
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'));from coplanar import overlaps
bpy.ops.wm.open_mainfile(filepath=str(R/'models/former-bhs.blend'));tri=[];labels=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 assert o.data.uv_layers,o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert all(math.isfinite(c) for v in p for c in v)
  assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-11
  tri.append([tuple(v) for v in p]);labels.append(o.name)
for data in (tri,np.asarray(tri,dtype=np.float32).astype(float)):
 rows=overlaps(data,labels);assert not [r for r in rows if r[2]>1e-5],rows[:20]
print('Provisional massing: %d triangles; ownership check passed'%len(tri))
# Independent area source coordinates must meet the authored building footprint.
import json
from mathutils import Vector
D=json.loads((R/'research/layout.json').read_text());X,Y,Z=D['origin'];W,L,F,A=D['width'],D['length'],D['front_depth'],D['arcade_wing_width'];B=W-D['corp_range_width']
def world(u,v,z=0):
 t=v/L;q=u/W
 return (X+u+t*(2.189*(1-q)+.498*q),Y+v+(1-t)*2.862*(1-q)+t*(-.016+.694*q),Z+z)
repo=Path(os.environ['SOUTHPORT_REPO_ROOT']);P=json.loads((repo/'regions/southport/lord-street/christ-church-approach/research/layout.json').read_text())
for actual,pair in zip(P['former_bhs_court'],[(A,F),(B,F),(B,L),(A,L)]):
 expected=world(*pair);assert math.dist(actual,expected[:2])<2e-6,(actual,expected)
# The actual court must remain open above two floor probes, away from tower.
for u,v in [((A+B)/2,F+8),((A+B)/2,L-4)]:
 x,y,z=world(u,v);hit,loc,norm,index,ob,matrix=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,y,Z+30)),Vector((0,0,-1)))
 assert not hit,(u,v,ob.name,tuple(loc))
print('Court registration and unobstructed sky probes passed')
# Independent District receivers must not overlap before any bake is attempted.
sys.path.insert(0,str(R/'scripts'));import district
for part,faces in district.surfaces(R).items():
 surface_tri=[];names=[]
 for f in faces:
  for ids in ((0,1,2),(0,2,3)):
   surface_tri.append([f['vertices'][i] for i in ids]);names.append(f['name'])
 conflicts=[r for r in overlaps(surface_tri,names) if r[2]>1e-5]
 assert not conflicts,(part,conflicts[:20])
print('District receiver ownership passed')
# A ray at each dormer window must hit glazing before the host roof plane.
# This specifically guards against the former buried-window regression.
schedule=json.loads((R/'research/elevation-schedule.json').read_text())
def first_ray(a,b):
 a=Vector(a);direction=(Vector(b)-a).normalized()
 return bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),a,direction)
for u,width,kind in schedule['dormers']['chapel']:
 u+=width*.22
 hit,loc,norm,index,ob,m=first_ray(world(u,-1,14.4),world(u,3,14.4))
 assert hit and 'Dormer glazing' in ob.name,(u,ob.name if hit else 'miss',tuple(loc) if hit else None)
for v,width,kind in schedule['dormers']['corporation']:
 v+=width*.22
 hit,loc,norm,index,ob,m=first_ray(world(W+1,v,14.4),world(W-3,v,14.4))
 assert hit and 'Return dormer glazing' in ob.name,(v,ob.name if hit else 'miss',tuple(loc) if hit else None)
print('Dormer glazing visibility rays passed')
# Gallery apertures must remain open until the inset rear glazing: guard against
# a generic wall helper accidentally closing the colonnade at the facade line.
for a,b,expected in [
 ((18.15,-2,10.0),(18.15,2,10.0),'Glazing Chapel gallery back'),
 ((W+2,2.8,10.0),(W-2,2.8,10.0),'Glazing Corporation gallery back'),
 ((15.8,-3,6.07),(15.8,1,6.07),'Glazing inner round bay'),
 ((W+3,1.0,6.07),(W-2,1.0,6.07),'Glazing corner round bay')]:
 hit,loc,norm,index,ob,m=first_ray(world(*a),world(*b))
 assert hit and expected in ob.name,(expected,ob.name if hit else 'miss',tuple(loc) if hit else None)
print('Gallery recess and rounded bay rays passed')
# Top-down probes ensure every cut dormer opening is covered by its own cap.
for u,width,kind in schedule['dormers']['chapel']:
 hit,loc,norm,index,ob,m=first_ray(world(u,1.5,25),world(u,1.5,10))
 assert hit and 'dormer cap' in ob.name.lower(),(u,ob.name if hit else 'miss')
for v,width,kind in schedule['dormers']['corporation']:
 hit,loc,norm,index,ob,m=first_ray(world(W-1.4,v,25),world(W-1.4,v,10))
 assert hit and 'dormer cap' in ob.name.lower(),(v,ob.name if hit else 'miss')
print('Dormer cap coverage rays passed')
