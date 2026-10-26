import bpy,json,math,os,sys
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/the-cloisters.blend'))
tri=[];labels=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 assert o.data.uv_layers,o.name
 o.data.calc_loop_triangles()
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co)
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-11,(o.name,t.index)
  tri.append([tuple(v) for v in p]);labels.append(o.name)
rows=overlaps(tri,labels);rounded=overlaps(np.asarray(tri,dtype=np.float32).astype(float),labels)
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':len(tri),'coplanar':rows,'float32':rounded,'coverage':'All exterior shell, repeated trim/joinery and inscriptions. Same-facing positive-area coplanarity, not a test for arbitrary near-plane depth conflicts.'},indent=2))
assert not [r for r in rows if r[2]>5e-6],rows[:30]
assert not [r for r in rounded if r[2]>5e-6],rounded[:30]
print('Cloisters validation',len(tri),'triangles')


import importlib.util
support=Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/lord-street/christ-church-approach/scripts/datum.py'
spec=importlib.util.spec_from_file_location('court_datum',support);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for y in [-73.78,-77.85,-81.93,-86.00]:assert abs(m.grade(-123.759662,y)-.7845)<.001
