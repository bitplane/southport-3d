import bpy,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/embassy-restaurant.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];tri=[];labels=[]
for o in obs:
 assert o.data.uv_layers,o.name
 o.data.calc_loop_triangles()
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co)
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-11,(o.name,t.index)
  tri.append([tuple(v) for v in p]);labels.append(o.name)
assert any(o.name=='Shell roof front' for o in obs)
assert any(o.name=='Shell roof corner' for o in obs)
rows=overlaps(tri,labels);bad=[r for r in rows if r[2]>5e-6]
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':len(tri),'coplanar':rows,'coverage':'All shell and trim meshes, including repeated joinery and text.'},indent=2))
assert not bad,bad[:20]
print('Embassy validated',len(tri),'triangles')
