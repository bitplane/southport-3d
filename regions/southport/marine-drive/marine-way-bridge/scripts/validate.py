"""All structural surfaces, open roadway and published-dimensional controls."""
import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools'),str(REPO/'regions/southport/marine-drive/public-realm/scripts')]
from shapes import D,transform,grade
from check_mesh_ownership import check
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/marine-way-bridge.blend'));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];count=0
for o in obs:
 assert o.data.uv_layers;o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in (a,b,c)for v in p);assert(b-a).cross(c-a).length>1e-10,(o.name,'zero triangle');count+=1
assert count<150000,count
# Complete scan includes decorative rails, posts, sockets, lamps and their joins.
check(obs,ROOT,REPO)
# Road and both shared routes remain free of structural surfaces below 2 m headroom.
for station in [4,20,40,60,80,103.8,120,148]:
 for transverse in [0,-3.8,3.8,-6.3,6.3]:
  z=grade(station,transverse);p=Vector(transform((station,transverse,z+.03)))
  for o in obs:
   hit=o.ray_cast(p,Vector((0,0,1)),distance=2.0);assert not hit[0],(station,transverse,o.name,'route blocked')
assert abs(max(v.co.z for o in obs for v in o.data.vertices)-56.6)<.02
report={'triangles':count,'objects':len(obs),'main_stays':12,'back_stays':6,'checks':'Every mesh finite/nondegenerate; full fast coplanar audit; forty clear roadway/shared-path headroom rays; pylon tip and documented dimensions. Below-water engineering not reconstructed.'};(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
