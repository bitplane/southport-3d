"""Scoped ground ownership, neighbour boundaries and public access regressions."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'tools')]
from datum import grade,SURFACE
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if not o.name.endswith('kerb')]
assert ground
for o in obs:
 assert o.data.uv_layers and all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(o.name,t.index)
  if o in ground:
   centre=(a+b+c)/3;expected=grade(centre.x,centre.y)-(.12 if any(o.name.endswith(' '+k) for k in ['asphalt','yellow','white']) else 0)
   assert abs(centre.z-expected)<1e-4,(o.name,t.index,'terrain plane erased',centre.z,expected)
tris=sum(len(o.data.loop_triangles) for o in obs);assert tris<D['budgets']['triangles_per_level'],tris
def hits(x,y):
 out=[]
 for o in ground:
  hit=o.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
  if hit[0]:out.append((o.name,hit[1].z))
 return out
def sample(x,y,road):
 h=hits(x,y);assert len(h)==1,(x,y,h)
 assert abs(h[0][1]-(grade(x,y)-(.12 if road else 0)))<3e-5,(x,y,h)
 return h
count=0
for r in D['roads']:
 for a,b in zip(r['points'],r['points'][1:]):
  n=max(1,int(math.dist(a,b)))
  for i in range(n):
   t=(i+.317)/n;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
   if 218.01<x<609.99 and 65.01<y<229.99 and not(x<250.01 and y<175.01):sample(x,y,True);count+=1
# Public seam rays have one owner and the inherited road datum.
seams=0
for x,y in [(250.001,98.841),(250.001,162.357),(371.92,65.001),(541.56,65.001),(350-.001,98),(350+.001,98),(450-.001,97),(450+.001,97)]:sample(x,y,True);seams+=1
for x,y in [(249.99,100),(400,64.99),(611,100),(400,230.01)]:assert not hits(x,y),(x,y,'neighbour/outer ownership overlap')
footprint_samples=0
for path in [D['block_plan'],*D['existing_block_plans']]:
 for block in json.loads((REPO/path).read_text())['blocks']:
  points=[Vector((x,y,0)) for x,y in block['footprint']]
  for tri in tessellate_polygon([points]):
   tri=[points[v] if isinstance(v,int) else v for v in tri]
   x=sum(v.x for v in tri)/3;y=sum(v.y for v in tri)/3
   assert not hits(x,y),(block['id'],x,y,'floor beneath building')
   footprint_samples+=1
check_blender(obs)
report={'triangles':tris,'objects':len(obs),'road_samples':count,'seam_samples':seams,'footprint_exclusion_samples':footprint_samples,'checks':'Every new ground mesh, kerb and paint; road access continuity; footprint floor exclusion; exact ownership cuts; same-facing coplanar overlap; finite export-safe triangle coordinates.','limitations':D['limits']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
