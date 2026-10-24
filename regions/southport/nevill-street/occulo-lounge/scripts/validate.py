"""Check export precision, uncovered glazing, roof registration and wall conflicts."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/occulo.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.view_layer.update()
assert len([o for o in obs if o.name.startswith('Column fluted')])==9
assert len([o for o in obs if o.name.startswith('Rooflight glass')])==2
assert len([o for o in obs if o.name.startswith('Pediment main')])==1
triangles=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.matrix_world@o.data.vertices[i].co for i in t.vertices)
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate float32 export')
# Probe an off-mullion point in each tall pane; walls must have actual holes.
deps=bpy.context.evaluated_depsgraph_get();probes=0
for o in obs:
 if not o.name.startswith('Window ') or 'vent' in o.name or 'oculus' in o.name:continue
 frame=Matrix(o['face_frame']);inv=frame.inverted()
 local=[inv@v.co for v in o.data.vertices]
 xs=[v.x for v in local];ys=[v.y for v in local]
 u=(max(xs)+min(xs))/2+.16;z=(max(ys)+min(ys))/2+.16
 origin=frame@Vector((u,z,1));direction=(frame.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and target.name.startswith('Window '),(o.name,'glazing blocked',target.name if target else None)
 probes+=1
# Rays through the doorway perimeter must meet masonry or its carved trim,
# including the narrow space between the timber frame and the architrave.
frame=Matrix(bpy.data.objects['Door shadow']['face_frame'])
u=json.loads((ROOT/'research/layout.json').read_text())['front_bays'][1]
entrance_probes=0
for side in (-1,1):
 for offset in (1.015,1.21,1.46):
  for z in (.15,2.,4.60):
   for slope in (-.35,0,.35):
    origin=frame@Vector((u+side*offset,z,.6))
    direction=(frame.to_3x3()@Vector((slope,0,-1))).normalized()
    hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1.5)
    assert hit,('entrance perimeter gap',side,offset,z,slope)
    entrance_probes+=1
# Sample visible lettering faces, preventing a correctly named but buried sign.
letter_checks={}
for name,outward in [('Sign Lord gold',(0,-1,0)),('Sign Nevill gold',(1,0,0)),('Sign established',(0,-1,0)),('Sign date',(0,-1,0))]:
 o=bpy.data.objects[name];normal=Vector(outward);good=total=0.
 for p in o.data.polygons:
  if p.normal.dot(normal)<.98 or p.area<1e-7:continue
  point=sum((o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
  hit,loc,n,index,target,matrix=bpy.context.scene.ray_cast(deps,point+normal*.035,-normal,distance=.045)
  total+=p.area
  if hit and target==o:good+=p.area
 assert total and good/total>.98,(name,'lettering obscured',good/total if total else 0)
 letter_checks[name]=good/total
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'));from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Wall ')])
report={'triangles':triangles,'window_probes':probes,'entrance_perimeter_probes':entrance_probes,'letter_visibility':letter_checks,'checks':'Finite float32 triangles/UVs; glazing rays; scoped wall coplanar audit; nine columns, two rooflights, one front pediment','limitations':'Metric scale estimated; rear lower detail and exact carved relief depth unresolved.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
