"""Asset geometry and measured footprint guards, run on the isolated master."""
import bpy,json,math,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-16-22.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
minimum=1.;count=0
for o in meshes:
 assert o.data.uv_layers,o.name
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co),o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];area=(b-a).cross(c-a).length/2
  assert area>1e-12,(o.name,area);minimum=min(minimum,area);count+=1
assert any(o.name.startswith('Shell roof front') for o in meshes)
assert any(o.name.startswith('Shell roof rear') for o in meshes)
assert any(o.name.startswith('Shell chamfer') for o in meshes)
triangles=[];labels=[]
for o in meshes:
 for t in o.data.loop_triangles:
  triangles.append([tuple(o.matrix_world@o.data.vertices[i].co) for i in t.vertices]);labels.append(o.name)
residual=overlaps(triangles,labels)
# At ~100m site coordinates, clipped float32 boundaries can leave square-
# millimetre numerical slivers. Enforce 5mm², and report every smaller candidate.
assert not [row for row in residual if row[2]>5e-6],residual[:12]
report={'objects':len(meshes),'triangles':count,'minimum_triangle_area':minimum,'coplanar_numeric_residuals':residual,'status':'Finite triangulated surfaces, UVs, explicit chamfer and unequal roof planes. All meshes checked for coplanar conflicts above 5 square millimetres; smaller float32 candidates reported.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2))
print(report)
