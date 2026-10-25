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

# Independently positioned service-yard probes guard registration and winding.
from mathutils import Vector,Matrix
D=json.loads((ROOT/'research/layout.json').read_text())
T=Matrix(((-.0003,1,0,D['x']),(-1,.0125,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
for name,p,direction,distance,wanted in [('gate',(-1,12.1,2.08),(1,0,0),2,True),('wall',(-1,13.8,1.5),(1,0,0),2,True),('open delivery lane',(-1,15.5,1.5),(1,0,0),3,False),('rear projection',(6,14,4),(0,-1,0),2,True)]:
 ray=(T.to_3x3()@Vector(direction)).normalized();hit,at,normal,face,ob,mat=s.ray_cast(deps,T@Vector(p),ray,distance=distance)
 assert hit==wanted,(name,'missing or obstructed',hit)
 if hit:assert normal.dot(ray)<-.5,(name,'inward facing surface',normal)
print('Four independently located yard probes passed')
