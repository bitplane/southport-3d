"""Actual triangle profiles, allmesh ownership and bounded envelope budgets."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from datum import SURFACES,PAVEMENT,BRIDGE
from venetian_ground import Transition,at,L,HALF_WIDTH,RAIL_OFFSET,PIERS,RAIL_START,RAIL_END,assert_frame,green_at,V,local
assert_frame(BRIDGE)
LANDING=Transition(PAVEMENT,BRIDGE,'landing');LOWER=Transition(PAVEMENT,BRIDGE,'lower')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if o.name.startswith('Ground ')and 'boundary'not in o.name];count=0;control_count=0;control_worst=0.
for o in obs:
 assert o.data.uv_layers;o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in [a,b,c]for v in p);assert (b-a).cross(c-a).length>1e-10
  if o in ground and not o.name.startswith(('Ground island ','Ground Venetian lower access steps')):
   p=(a+b+c)/3
   surface=BRIDGE if 'Venetian'in o.name else LANDING if ' landing ' in o.name else LOWER if ' lower ' in o.name else PAVEMENT
   expected=surface.height(p.x,p.y)-(.12 if any(o.name.endswith(' '+m)for m in ['asphalt','yellow','white','parking'])else 0)
   if surface in (LANDING,LOWER):
    assert abs(p.z-expected)<.1,(o.name,tuple(p),expected,'transition approximation')
    for v in (a,b,c):
     exact=surface.height(v.x,v.y)-(.12 if any(o.name.endswith(' '+m)for m in ['asphalt','yellow','white','parking'])else 0)
     assert abs(v.z-exact)<.001,(o.name,tuple(v),exact,'transition vertex')
   else:assert abs(p.z-expected)<1.5e-4,(o.name,tuple(p),expected,'profilebreak erased')
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

# Bounded Venetian transitions: at the Kings Gardens side the local mainland
# agrees with the deck edge, and the Princes Park path remains below the deck.
for t in (1,5,10,13):
 for side in (-1,1):
  inner=hits(*at(t,side*2.0));outer=hits(*at(t,side*3.2))
  deck=[z for name,z in inner if name=='Ground Venetian bridge top']
  bank=[z for name,z in outer if ' landing ' in name]
  assert deck and bank,(t,side,inner,outer,'landing support absent')
  assert abs(deck[0]-bank[0])<.08,(t,side,deck,bank,'landing edge step')
under=hits(*at(151,0))
deck=[z for name,z in under if name=='Ground Venetian bridge top']
lower=[z for name,z in under if ' lower ' in name]
assert deck and lower and deck[0]-lower[0]>.0,(under,'separate lower support missing')
assert deck[0]-.3-lower[0]>1.7,(under,'insufficient underside clearance')
for j in range(11):
 o=-2.6-(j+.5)*3.6/11
 stair=[z for name,z in hits(*at(151,o)) if name=='Ground Venetian lower access steps']
 assert stair,(j,o,'stair tread absent')
print('Venetian landing edges and distinct lower support: checked; underside clearance',round(deck[0]-.3-lower[0],3),'m')

# Check the actual authored mesh at both edges, piers and intervening rails.
# These rays use the independent elevation profile and include every pier,
# profile knot and both approaches; they do not merely test the generator.
deck=bpy.data.objects['Ground Venetian bridge top']
rails=bpy.data.objects['Structure Venetian open handrails and base rails']
greenrails=bpy.data.objects['Structure Venetian island metal railings']
posts=bpy.data.objects['Structure Venetian panelled piers']
def up_contact(obj,t,o,offset=0):
 x,y=at(t,o);z=BRIDGE.height(x,y)+offset
 hit,point,_,_=obj.ray_cast(Vector((x,y,z-.4)),Vector((0,0,1)))
 assert hit and abs(point.z-z)<.001,(obj.name,t,o,tuple(point) if hit else None,z)
 return point.z
probes=0
for t in [i*L/160 for i in range(1,160)]+[s for s in BRIDGE.stations if .25<s<L-.25]:
 for side in (-1,1):
  for off in (0,HALF_WIDTH-.02):
   up_contact(deck,t,side*off);probes+=1
for t in PIERS:
 for side in (-1,1):
  for dt in (-.20,0,.20):
   for do in (-.20,0,.20):
    up_contact(deck,t+dt,side*RAIL_OFFSET+do)
    up_contact(posts,t+dt,side*RAIL_OFFSET+do);probes+=2
for j in range(1,400):
 t=RAIL_START+j*(RAIL_END-RAIL_START)/400
 if any(abs(t-p)<.25 for p in PIERS):continue
 for side in (-1,1):
  if side==-1 and 150.27<t<151.73:continue
  up_contact(deck,t,side*RAIL_OFFSET)
  obj=greenrails if green_at(t) else rails;half=.0275 if green_at(t) else .08
  up_contact(obj,t,side*RAIL_OFFSET,.055 if green_at(t) else .16)
  x,y=at(t,side*RAIL_OFFSET-.2);z=BRIDGE.height(x,y)+.002
  hit,point,_,_=obj.ray_cast(Vector((x,y,z)),Vector((V[0],V[1],0)),distance=.4)
  assert hit and abs(local(point.x,point.y)[1]-(side*RAIL_OFFSET-half))<.002,(obj.name,t,side,tuple(point) if hit else None)
  probes+=3
print('Venetian deck, plinth and rail base contacts:',probes,'native mesh probes')

# On the flat Kings approach, test the horizontal route through the shoreline
# wall. A vertical ground ray cannot see a vertical wall blocking the deck.
wall=bpy.data.objects['Structure formal water edge']
x,y=at(10,0);z=BRIDGE.height(x,y)+.2
from venetian_ground import U
hit,point,_,_=wall.ray_cast(Vector((x,y,z)),Vector((U[0],U[1],0)),distance=10)
assert not hit,('Shore wall blocks bridge approach',tuple(point))
print('Kings approach wall clearance: checked')

# Openings and flared capitals are tested on the actual native mesh: the side
# walls must let a ray through each opening while their lower web remains, and
# the pier must be wider near its head than at water level.
spandrel=bpy.data.objects['Structure Venetian pierced arch spandrels']
piers=bpy.data.objects['Structure Venetian flat span piers']
for t in (66.3,67.5,68.7,91.3,92.5,93.7):
 q=(t-80)/15;soffit=-2.10+2.35*(1-q*q);top=BRIDGE.height(*at(t))-.3
 for side in (-1,1):
  x,y=at(t,side*2.65);direction=Vector((-side*V[0],-side*V[1],0))
  hole=(soffit+top)/2;hit,point,_,_=spandrel.ray_cast(Vector((x,y,hole)),direction,distance=.7)
  assert not hit,('Filled spandrel opening',t,side,tuple(point))
  hit,point,_,_=spandrel.ray_cast(Vector((x,y,soffit+.05)),direction,distance=.7)
  assert hit,('Missing lower arch web',t,side)
# A ray that passed through the larger middle opening is blocked by the lower
# web near the innermost tip, confirming a taper rather than a rectangle.
for t in (69.2,90.8):
 q=(t-80)/15;soffit=-2.10+2.35*(1-q*q);top=BRIDGE.height(*at(t))-.3
 for side in (-1,1):
  x,y=at(t,side*2.65);direction=Vector((-side*V[0],-side*V[1],0))
  assert spandrel.ray_cast(Vector((x,y,(soffit+top)/2)),direction,distance=.7)[0],('Untapered arch opening',t,side)
for side in (-1,1):
 direction=Vector((V[0],V[1],0));top=BRIDGE.height(*at(13))-.3
 for t,depth in ((13.8,.05),(14.8,.01)):
  x,y=at(t,side*2.05-.7)
  high=piers.ray_cast(Vector((x,y,top-depth)),direction,distance=1.4)[0]
  low=piers.ray_cast(Vector((x,y,-2.335294+.5)),direction,distance=1.4)[0]
  assert high and not low,('Flat-span pier haunch silhouette',t,side,high,low)
print('Venetian pierced arch and flared pier profiles: checked')
