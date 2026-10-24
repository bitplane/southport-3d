"""Check finite nondegenerate geometry, real facade apertures and open yard."""
import bpy,math,os,sys,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/willow-grove.blend'));s=bpy.context.scene;bpy.context.view_layer.update()
obs=[o for o in s.objects if o.type=='MESH'];tris=0
for o in obs:
 assert o.data.uv_layers and o.data.polygons,o.name
 o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate')
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
deps=bpy.context.evaluated_depsgraph_get();n=0
for bay in D['bay_centres']:
 for off in D['light_offsets']:
  for z in (6.1,9.8):
   hit,at,normal,i,o,m=s.ray_cast(deps,T@Vector((D['front_left']+bay+off,-1,z)),(T.to_3x3()@Vector((0,1,0))).normalized(),distance=2)
   assert hit and o.name.startswith('Architecture lord'),(bay,off,z,o.name if o else None);n+=1
for u in D['boots_bays']:
 for z in (6.5,11.2):
  hit,at,normal,i,o,m=s.ray_cast(deps,T@Vector((-1,D['wing_start']+u+.15,z)),(T.to_3x3()@Vector((1,0,0))).normalized(),distance=2)
  assert hit and o.name.startswith('Architecture nevill'),(u,z,o.name if o else None);n+=1
for y in (39,44,49):
 hit,*_=s.ray_cast(deps,T@Vector((14.5,y,1)),Vector((0,0,1)),distance=20);assert not hit,('yard filled',y)
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Shell ')])
report={'triangles':tris,'aperture_probes':n,'yard_probes':3,'phase':D['phase']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
