"""Continuous road/footway ownership, export-safe faces and overlap checks."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'tools')]
from datum import grade
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if not o.name.endswith('kerb')]
assert ground
for o in obs:
 assert o.data.uv_layers and all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(o.name,t.index)
tris=sum(len(o.data.loop_triangles) for o in obs);assert tris<D['budgets']['triangles_per_level'],tris
def hits(x,y):
 out=[]
 for o in ground:
  hit=o.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
  if hit[0]:out.append((o.name,hit[1].z))
 return out
def sample(x,y,road):
 h=hits(x,y);assert len(h)==1,(x,y,h)
 assert abs(h[0][1]-(grade(x,y)-(.12 if road else 0)))<2e-5,(x,y,h)
 return h
count=0
for r in D['roads']:
 for a,b in zip(r['points'],r['points'][1:]):
  n=max(1,int(math.dist(a,b)))
  for i in range(n):
   t=(i+.317)/n;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
   if 24<x<249 and 65.01<y<174.99:sample(x,y,True);count+=1
# Narrow footways are open on both sides, private courts separate behind them.
for x in [60,120,180]:
 for r in D['roads'][:2]:
  a,b=next((a,b) for a,b in zip(r['points'],r['points'][1:]) if a[0]<=x<=b[0]);y=a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1])
  for side in [-1,1]:sample(x,y+side*(r['width']/2+.35),False)
for x in [90,160]:
 for y in [100,164]:sample(x-.001,y,True);sample(x+.001,y,True)
for p in [(21,100.8),(22,165.45),(40,154),(225,64.9)]:assert not hits(*p),(p,'existing owner overlap')
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
report={'triangles':tris,'objects':len(obs),'road_samples':count,'footprint_exclusion_samples':footprint_samples,'checks':'Road continuity, footways, neighbour ownership, tile seams, finite nondegenerate float32 triangles, same-facing coplanar overlap.','limitations':D['limits']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Bounded service yard has one walkable owner; structures have no floor beneath.
for x,y in [(24,87),(24,93),(24,95.5)]:
 h=sample(x,y,False);assert h[0][0].endswith('service-yard'),h
for x,y in [(20.9,92),(23.5,82)]:assert not hits(x,y),('new service footprint',x,y,hits(x,y))
print('Three service-yard support and two footprint exclusion probes passed')
