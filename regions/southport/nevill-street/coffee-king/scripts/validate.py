"""Check finite export, visible glazing, registration and closed doorway perimeter."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/coffee-king.blend'));bpy.context.view_layer.update()
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];deps=bpy.context.evaluated_depsgraph_get()
assert len([o for o in obs if o.name.startswith('Column Tuscan')])==4
triangles=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate export')
frame=Matrix(bpy.data.objects['Glazing tall 1']['face_frame']);direction=(frame.to_3x3()@Vector((0,0,-1))).normalized();probes=0
for i,u in enumerate(D['bays']):
 for z in ([4.05] if i==0 else [1.2,3.2,4.05])+[8.2,11.5]:
  hit,p,n,index,target,m=bpy.context.scene.ray_cast(deps,frame@Vector((u+.22,z,1)),direction,distance=2)
  assert hit and target.name.startswith(('Glazing','Frames','Blind')),(u,z,target.name if target else None)
  probes+=1
# Exterior pedestal normals must point towards the street, otherwise the
# signed normal bake makes their low-detail bases grey/inverted.
for u in D['columns']:
 for z in (.15,1.75):
  hit,p,n,index,target,m=bpy.context.scene.ray_cast(deps,frame@Vector((u,z,1)),direction,distance=2)
  assert hit and target.name.startswith('Pedestal moulding'),(u,z,target.name if target else None)
  assert n.dot(-direction)>.9,(target.name,z,'inward exterior normal')
if D['phase']=='detail':
 u=D['bays'][0]
 for x,z in [(u-.68,.3),(u+.68,.3),(u-.68,2.5),(u+.68,2.5),(u,2.9)]:
  hit,*_=bpy.context.scene.ray_cast(deps,frame@Vector((x,z,.8)),direction,distance=1.5);assert hit,('door gap',x,z)
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'));from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Wall ')])
report={'triangles':triangles,'glazing_probes':probes,'phase':D['phase'],'limitations':'Courtyard finishes and hidden rear openings deferred pending owner photos.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
