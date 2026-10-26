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
# Probe the centre of the upper gate rail, not the float32 reed-tip boundary.
from mathutils import Vector,Matrix
D=json.loads((ROOT/'research/layout.json').read_text())
T=Matrix(((-.0003,1,0,D['x']),(-1,.0125,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
for name,p,direction,distance,wanted in [('gate',(-1,12.1,2.14),(1,0,0),2,True),('wall',(-1,13.8,1.5),(1,0,0),2,True),('open delivery lane',(-1,15.5,1.5),(1,0,0),3,False),('rear projection',(6,14,4),(0,-1,0),2,True)]:
 ray=(T.to_3x3()@Vector(direction)).normalized();hit,at,normal,face,ob,mat=s.ray_cast(deps,T@Vector(p),ray,distance=distance)
 assert hit==wanted,(name,'missing or obstructed',hit)
 if hit:assert normal.dot(ray)<-.5,(name,'inward facing surface',normal)
print('Four independently located yard probes passed')

# Measured geometry, not source constants: the glyphs must clear the real duct.
sign=[o for o in meshes if o.name=='Architecture return lettering']
duct=[o for o in meshes if o.name.startswith('Architecture return duct') and 'bracket' not in o.name]
assert sign and duct
zs=lambda obs:[(o.matrix_world@v.co).z-D['base_z'] for o in obs for v in o.data.vertices]
a,b=zs(sign),zs(duct)
assert min(a)-max(b)>.25,('duct/letter clearance',min(a),max(b))
assert 3.60<min(a)<3.70 and max(a)<4.13,('fascia glyph bounds',min(a),max(a))
assert 3.32<max(b)<3.37 and 2.98<min(b)<3.04,('duct vertical registration',min(b),max(b))
print('Return glyph/duct clearance',min(a)-max(b),'metres')

for u in (.8,2,4.4):
 ray=(T.to_3x3()@Vector((1,0,0))).normalized()
 hit,at,normal,face,ob,mat=s.ray_cast(deps,T@Vector((-2,D['depth']-u,3.18)),ray,distance=2)
 assert hit and ob.name.startswith('Architecture return duct') and normal.dot(ray)<-.8,('duct winding',u,hit,ob.name if ob else None,tuple(normal))
print('Three outward duct surface probes passed')

# The broad shallow roof must not inherit pale lead from the yard fittings.
front=bpy.data.objects.get('Shell roof front')
assert front is not None
material=front.data.materials[0]
colour=material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
assert max(colour[:3])<.10 and material.name=='Dark charcoal shallow roof covering',('Pale front roof regression',material.name,tuple(colour))
