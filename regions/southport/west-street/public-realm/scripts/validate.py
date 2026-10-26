"""Check unique floors, access routes, cutouts, seams and export-safe geometry."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'tools')]
from datum import grade,SURFACE
from coplanar import overlaps
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

def contains(p,x,y):
 inside=False
 for a,b in zip(p,p[1:]+p[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
buildings=list(D['extra_building_cutouts']);undercroft=None
for path in [D['block_plan'],*D['existing_block_plans']]:
 for b in json.loads((REPO/path).read_text())['blocks']:
  if path==D['block_plan'] and b['id']==D['undercroft_fill']['block_id']:undercroft=b['footprint']
  else:buildings.append(b['footprint'])
assert undercroft
def owned(x,y):return contains(D['outer'],x,y) and not any(contains(p,x,y) for p in [*D['existing_ground_exclusions'],*buildings])
def hits(x,y):
 out=[]
 for o in ground:
  hit=o.ray_cast(Vector((x,y,80)),Vector((0,0,-1)))
  if hit[0]:out.append((o.name,hit[1].z))
 return out
count=0
for r in D['roads']:
 for a,b in zip(r['points'],r['points'][1:]):
  n=max(1,int(math.dist(a,b)/2))
  for i in range(n):
   t=(i+.317)/n;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
   if not owned(x,y):continue
   h=hits(x,y);assert len(h)==1,(r['name'],x,y,h)
   assert abs(h[0][1]-(grade(x,y)-.12))<2e-5,(r['name'],x,y,h)
   count+=1
# The full running width must remain clear, not just the centreline. This
# catches a misregistered street whose edge would be clipped by a building.
road_edge_samples=0
r=D['roads'][0]
for j,(a,b) in enumerate(zip(r['points'],r['points'][1:])):
 length=math.dist(a,b);nx,ny=-(b[1]-a[1])/length,(b[0]-a[0])/length
 for t in [.2,.4,.6,.8]:
  width=r['widths'][j]*(1-t)+r['widths'][j+1]*t
  for sign in [-1,1]:
   x=a[0]*(1-t)+b[0]*t+sign*(width/2-.25)*nx;y=a[1]*(1-t)+b[1]*t+sign*(width/2-.25)*ny
   if not contains(D['outer'],x,y) or any(contains(p,x,y) for p in D['existing_ground_exclusions']):continue
   assert not any(contains(p,x,y) for p in buildings),(x,y,'building obstructs running width')
   h=hits(x,y);assert len(h)==1 and abs(h[0][1]-(grade(x,y)-.12))<2e-5,(x,y,'running edge missing',h)
   road_edge_samples+=1
footprint_samples=0
for p in buildings:
 points=[Vector((x,y,0)) for x,y in p]
 for tri in tessellate_polygon([points]):
  tri=[points[v] if isinstance(v,int) else v for v in tri];x=sum(v.x for v in tri)/3;y=sum(v.y for v in tri)/3
  assert not hits(x,y),(x,y,'floor beneath building');footprint_samples+=1
# The restored parking court is a single support surface within its boundary.
for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in undercroft]]):
 points=[Vector((x,y,0)) for x,y in undercroft];tri=[points[v] if isinstance(v,int) else v for v in tri]
 x=sum(v.x for v in tri)/3;y=sum(v.y for v in tri)/3;h=hits(x,y);assert len(h)==1,(x,y,'undercroft ground missing or doubled',h)
# New street and pavement have no holes at tile cuts.
seams=0
for x in D['tile_cuts'][1:-1]:
 a,b=next((a,b) for a,b in zip(D['roads'][0]['points'],D['roads'][0]['points'][1:]) if a[0]<=x<=b[0]);y=a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1])
 for dy in [0,4.6,-4.6]:
  for xx in [x-.003,x+.003]:
   if owned(xx,y+dy):assert len(hits(xx,y+dy))==1,(xx,y+dy,hits(xx,y+dy));seams+=1
triangles=[];labels=[]
for o in obs:
 for t in o.data.loop_triangles:
  triangles.append([tuple(o.matrix_world@o.data.vertices[i].co) for i in t.vertices]);labels.append(o.name)
residues=overlaps(triangles,labels)
# Same 1e-5 m² reporting threshold used for the neighbouring corridor's
# float32 boundary audit; preserve smaller findings in the report.
assert not [r for r in residues if r[2]>1e-5],residues
report={'triangles':tris,'objects':len(obs),'road_samples':count,'road_edge_samples':road_edge_samples,'footprint_exclusion_samples':footprint_samples,'tile_seam_samples':seams,'float32_overlap_residues':residues,'overlap_area_limit_m2':1e-5,'checks':'Unique road floor, building exclusions, tile seams, finite nondegenerate float32 geometry, coplanar overlap.','limitations':D['limits']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
