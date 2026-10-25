"""Verify road profiles, multi-level bridge support and unique surface ownership."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from datum import grade,SURFACES
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if o.name.startswith('Ground ') and not o.name.endswith('kerb')]
count=0
for o in obs:
 assert o.data.uv_layers
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in [a,b,c]for v in p);assert (b-a).cross(c-a).length>1e-10
  if o in ground:
   p=(a+b+c)/3;expected=0 if 'railway' in o.name else grade(p.x,p.y)-(.12 if any(o.name.endswith(' '+m)for m in ['asphalt','yellow','white'])else 0)
   assert abs(p.z-expected)<7e-5,(o.name,tuple(p),expected,'lost profile break')
  count+=1
assert count<D['budgets']['triangles_per_level'],count
check_blender(obs)
def hits(x,y):
 result=[]
 for o in ground:
  h=o.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
  if h[0]:result.append((o.name,h[1].z))
 return result
# Same XY supports two distinct levels, without filling the bridge opening.
h=hits(-334.3,-602);assert len(h)==2,h;assert abs(min(z for _,z in h))<1e-5;assert abs(max(z for _,z in h)-(grade(-334.3,-602)-.12))<5e-5
# Retaining envelopes must not seal the rail tunnel at the deck edges.
for y in [-604.94,-600.42]:
 for o in obs:
  if 'retaining envelope' not in o.name:continue
  for direction in [-1,1]:
   hit=o.ray_cast(Vector((-334.3,y,1.7)),Vector((direction,.06*direction,0)),distance=15)
   assert not hit[0],('Retaining wall blocks railway',y,direction)
samples=0
for y in range(-688,-35,2):
 points=[p for r in D['roads']if r['name']=='Eastbank Street'for p in r['points']]
 segments=[(a,b)for r in D['roads']if r['name']=='Eastbank Street'for a,b in zip(r['points'],r['points'][1:])if min(a[1],b[1])<=y<=max(a[1],b[1])]
 if not segments:continue
 a,b=segments[0];t=(y-a[1])/(b[1]-a[1]);x=a[0]+t*(b[0]-a[0]);h=hits(x,y)
 assert any(abs(z-(grade(x,y)-.12))<8e-5 for _,z in h),(x,y,h)
 samples+=1
# Shared northern boundary matches legacy Lord gradient exactly.
for x in [-256.5,-254]:
 h=hits(x,-35.001);assert h,(x,h);assert abs(max(z for _,z in h)-(.762522-.12))<1e-4,h
# Vertical face closes the 120mm external ownership step at Chapel; road-facing.
x=-257+(-125+108)*3.8/29
kerb_hits=[]
for o in obs:
 if o.name.endswith('kerb'):
  h=o.ray_cast(Vector((x-.1,-125,.72)),Vector((1,0,0)))
  if h[0] and abs(h[1].x-x)<.001:kerb_hits.append(h)
assert kerb_hits and all(h[2].x<0 for h in kerb_hits),'Chapel ownership kerb missing or reversed'
report={'objects':len(obs),'triangles':count,'road_profile_samples':samples,'checks':'Every triangle profile plane, two bridge levels at shared XY, north handover, all ground/structure coplanar surfaces, finite nondegenerate geometry.','limitations':D['limits']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
