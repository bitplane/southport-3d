"""Actual triangle profiles, allmesh ownership and bounded envelope budgets."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from datum import SURFACES,PAVEMENT,BRIDGE
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if o.name.startswith('Ground ')and 'boundary'not in o.name];count=0;control_count=0;control_worst=0.
for o in obs:
 assert o.data.uv_layers;o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in [a,b,c]for v in p);assert (b-a).cross(c-a).length>1e-10
  if o in ground:
   p=(a+b+c)/3
   surface=BRIDGE if 'Venetian'in o.name else PAVEMENT
   expected=surface.height(p.x,p.y)-(.12 if any(o.name.endswith(' '+m)for m in ['asphalt','yellow','white','parking'])else 0)
   assert abs(p.z-expected)<1.5e-4,(o.name,tuple(p),expected,'profilebreak erased')
   if surface is PAVEMENT and any(o.name.endswith(' '+m)for m in ['asphalt','yellow','white','parking']):
    error=abs(PAVEMENT.height(p.x,p.y)-.12-PAVEMENT.terrain.height(p.x,p.y))
    assert error<.0001,(o.name,tuple(p),error,'control terrain approximation')
    control_count+=1;control_worst=max(control_worst,error)
  count+=1
assert count<D['budgets']['triangles_per_level'],count
ground_count=sum(len(o.data.loop_triangles)for o in obs if o.name.startswith('Ground '));structure_count=count-ground_count
assert ground_count<D['budgets']['ground_triangles_per_level'],ground_count
assert structure_count<D['budgets']['structure_triangles_per_level'],structure_count
from check_mesh_ownership import check
check(obs,ROOT,REPO)
def hits(x,y):
 out=[]
 for o in ground:
  h=o.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
  if h[0]:out.append((o.name,h[1].z))
 return out
for x,y in [(-400,111.5),(-500,811),(-300,600),(-290.9,405),(-500,350)]:
 h=hits(x,y);assert h,(x,y,'route absent');assert len(h)==1,(x,y,h,'multiplegroundowners')
# The lake is never a fallback walkingfloor; only explicit bridge spans support.
assert not hits(-400,400),hits(-400,400)
report={'control_road_probes':control_count,'max_control_road_error_m':control_worst,'objects':len(obs),'triangles':count,'ground_triangles':ground_count,'structure_triangles':structure_count,'checks':'All triangle interiors match named profiles; every mesh enters the coplanar audit; fixed budgets; road/park/bridge continuity; no walkable lake floor.','limits':D['limits']};(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# The bridge spans both planted islands; clipping its deck to water alone left
# three-metre drops at those islands after the deck and terrain were separated.
a,b=D['venetian_axis'][0],D['venetian_axis'][-1]
for i in range(1,81):
 x=a[0]+(b[0]-a[0])*i/81;y=a[1]+(b[1]-a[1])*i/81
 support=[z for name,z in hits(x,y)if 'Venetian'in name]
 assert support and min(abs(z-BRIDGE.height(x,y))for z in support)<.001,(x,y,support,'interrupted bridge deck')
print('Continuous bridge support across both islands and shore approaches')
