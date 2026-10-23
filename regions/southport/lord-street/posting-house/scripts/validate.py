"""Verify roof closure, open courtyard, glazing recesses and registration."""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/posting-house.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert len([o for o in meshes if o.name.startswith('Gable main ')])==2
assert len([o for o in meshes if o.name.startswith('Gable 132 white')])==3
assert len([o for o in meshes if o.name.startswith('Dormer cheek front')])==3
assert len([o for o in meshes if o.name.startswith('Chimney stack')])==6
roof=bpy.data.objects['Roof historic joined gables']
bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_manifold for e in bm.edges),'Roof is not closed'
bm.free()
# Exactly one upper roof skin and one lower skin, including the joined valleys.
roof_samples=0
for ix in range(1,40):
    x=D['historic_start']+ix*.5
    if x>=31.1:continue
    for iy in range(1,35):
        origin=Vector((x,iy*.5,26));hits=[]
        for _ in range(5):
            hit,p,n,index=roof.ray_cast(origin,Vector((0,0,-1)),distance=26)
            if not hit:break
            hits.append((p.z,n.z));origin=p+Vector((0,0,-.0001))
        assert len(hits)==2 and hits[0][1]>0 and hits[1][1]<0,(x,iy,hits)
        roof_samples+=1
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
windows=0
for ob in meshes:
    if not ob.name.startswith(('Window upper','Window 132','Window modern','Glazing warehouse','Glazing rear estimated')):continue
    origin=ob.matrix_world@Vector((.16,.25,.35))
    direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,p,n,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
    assert hit and target==ob,(ob.name,'obscured by',target.name if target else None)
    windows+=1
# Shared datum and the bank alley remain clear, with no OSM solid courtyard.
points=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert min(p.x for p in points)>31.7
assert max(p.x for p in points)<67
assert min(p.y for p in points)>-79
assert max(p.y for p in points)<-19
x0,y0=D['front_east'];x1,y1=D['front_west'];w=math.hypot(x1-x0,y1-y0);ux=(x1-x0)/w;uy=(y1-y0)/w
front=Matrix(((ux,0,uy,x0),(uy,0,-ux,y0),(0,1,0,D['base_z']),(0,0,0,1)))
p=front@Vector((24,30,-31))
hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,p,Vector((0,0,-1)),distance=35)
assert hit and 3.2<point.z<3.6,('Courtyard filled',target.name if target else None,point)
report={'meshes':len(meshes),'roof_samples':roof_samples,'clear_windows':windows,'checks':'finite meshes and UVs, packed textures, landmark counts, closed single-skin intersecting roof, clear glazing rays, alley bounds, open courtyard'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Every dormer pane remains in front of the main slope at low and high samples.
for ob in meshes:
 if ob.name.startswith('Glazing dormer sash'):
  for y in [-.68,-.45,.20,.68]:
   origin=ob.matrix_world@Vector((.12,y,.5))
   direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
   hit,p,n,i,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
   assert hit and target==ob,(ob.name,y,'Roof obscures dormer',target.name if target else None)
 if ob.name.startswith('Window upper sash'):
  origin=ob.matrix_world@Vector((.615,.24,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  distances=[]
  for other in meshes:
   inverse=other.matrix_world.inverted();hit,p,n,i=other.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized(),distance=2)
   if hit:distances.append(((other.matrix_world@p-origin).length,other.name))
  distances.sort()
  assert distances[0][1]==ob.name,(ob.name,'Window edge obscured',distances[:3])
  assert sum(abs(t-distances[0][0])<1e-5 for t,name in distances)==1,(ob.name,'Coincident reveal',distances[:3])
# Canted aprons meet the sill ledges without a view through to the wall behind.
for c in [D['historic_start']*(j+.5)/3 for j in range(3)]:
 for z in [5.46,9.46]:
  for dx in [-.65,.13,.65]:
   origin=front@Vector((c+dx,z,1.2));direction=(front.to_3x3()@Vector((0,0,-1))).normalized()
   hit,p,n,i,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1.3)
   assert hit and (front.inverted()@p).z>.70,('Open bay apron',c,z,dx,target.name if target else None)
# The 132 roof is a thin closed shell, not a filled triangular attic end.
ob=bpy.data.objects['Roof 132 main gable'];bm=bmesh.new();bm.from_mesh(ob.data)
assert all(e.is_manifold for e in bm.edges),'132 roof shell is open'
bm.free()
origin=front@Vector((D['historic_start']+1,17.5,-D['main_depth']/2))
direction=(front.to_3x3()@Vector((-1,0,0))).normalized();inverse=ob.matrix_world.inverted()
hit,p,n,i=ob.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized(),distance=2)
assert not hit,'Solid roof end duplicates 132 brick gable'
print('Dormer panes, sash-edge ownership, canted apron joins and thin 132 roof verified')
