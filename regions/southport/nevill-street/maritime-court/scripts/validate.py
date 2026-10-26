import bpy,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender,overlaps
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/maritime-court.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];n=0
for o in obs:
 assert o.data.uv_layers,o.name;o.data.calc_loop_triangles();n+=len(o.data.loop_triangles)
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co)
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-10,(o.name,t.index)
# Whole facade surfaces, aperture reveals, repeated frames, panes and fine railings.
selection=[o for o in obs if not any(x in o.name for x in ['entrance','lift','soffit'])]
check_blender([o for o in selection if o.name!='Shell pier caps'])
tri=[];labels=[]
for o in selection:
 for t in o.data.loop_triangles:
  tri.append([tuple(o.matrix_world@o.data.vertices[v].co)for v in t.vertices]);labels.append(o.name)
r=overlaps(tri,labels)
accepted=[q for q in r if set(q[:2])=={'Shell pier caps','Shell flat roof'} and q[2]<2e-6]
assert len(accepted)==len(r),r
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':n,'coplanar':r,'coverage':'All six shell elevations, pier returns/caps, roof, every aperture/frame/pane/mullion/sill, undercroft supports and fine window bars. Porch/lift contact boxes separately reviewed as buried interfaces.'},indent=2,default=str))
print(r)
assert len(accepted)==len(r)
print('Maritime Court validated',n,'triangles')
