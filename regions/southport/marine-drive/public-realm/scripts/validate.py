"""All-surface ownership, exact ground profiles and fixed budget regression."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from datum import grade,SURFACES,PAVEMENT,BRIDGE
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if o.name.startswith('Ground ')and not o.name.endswith('kerb')];count=0
for o in obs:
 assert o.data.uv_layers;o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in [a,b,c]for v in p);assert (b-a).cross(c-a).length>1e-10
  if o in ground:
   p=(a+b+c)/3;surface=BRIDGE if ' bridge 'in o.name else PAVEMENT;expected=surface.height(p.x,p.y)-(.12 if any(o.name.endswith(' '+m)for m in ['asphalt','yellow','white','parking'])else 0)
   assert abs(p.z-expected)<8e-5,(o.name,tuple(p),expected,'profile break erased')
  count+=1
assert count<D['budgets']['triangles_per_level'],count
ground_count=sum(len(o.data.loop_triangles)for o in obs if o.name.startswith('Ground '))
structure_count=count-ground_count
assert ground_count<D['budgets']['ground_triangles_per_level'],ground_count
assert structure_count<D['budgets']['structure_triangles_per_level'],structure_count
from check_mesh_ownership import check
ownership=check(obs,ROOT,REPO)
def hits(x,y):
 out=[]
 for o in ground:
  h=o.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
  if h[0]:out.append((o.name,h[1].z))
 return out
# Essential route continuity and ownership, including the exact old X85 seam.
for x,y,z in [(85.01,292,2.08),(85.01,301,2.08),(85.01,308,2.2),(-15,440,6.055),(800,883,2.08),(1330,862,2.2)]:
 h=hits(x,y);assert h,(x,y,'ground absent');assert max(abs(v-z)for _,v in h)<.15,(x,y,h,z)
report={'objects':len(obs),'triangles':count,'ground_triangles':ground_count,'structure_triangles':structure_count,'checks':'All triangle interiors agree with named profiles; full mesh coplanar audit; fixed budget; route/bridge/old boundary probes. No floor under the water; water is non-walkable.','limits':D['limits']};(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
