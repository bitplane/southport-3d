"""Check corridor continuity, ownership, float32 geometry and furnishing placement."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path.insert(0,str(REPO/'lib'))
sys.path.insert(0,str(ROOT/'scripts'))
from southport3d.elevation import Elevations
from bhs_arcade_support import wall_x
surface=Elevations(REPO/'regions/southport/elevation/station-approach.json').surface('chapel-pedestrian')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if o.name.startswith('Ground ')]
arcade=json.loads((REPO/'regions/southport/corporation-street/former-bhs/research/arcade-support.json').read_text())
assert obs and ground
for o in obs:
 assert o.data.uv_layers and all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(o.name,t.index)
assert sum(len(o.data.loop_triangles) for o in obs)<D['budgets']['detail_triangles']
# Local ray casts test ground only: benches and bridge roofs cannot hide a hole.
def hits(x,y):
 return [(o,o.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))) for o in ground if o.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]]
def sample(x,y):
 expected=surface.height(x,y)
 h=hits(x,y);assert h,(x,y,'missing ground');assert all(abs(hit[1].z-expected)<1e-5 for o,hit in h);return h
for a,b in zip(D['centreline'],D['centreline'][1:]):
 for i in range(20):
  t=(i+.5)/20;sample(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t)
for p in [(-55,-160),(-55,-175),(-128,-110),(-162,-100),(-164,-168),(-5,-144)]:sample(*p)
# Probe both sides of the owned strip: the wall meets the building datum and
# the outer edge preserves the surrounding station ground. Interior values are
# linearly interpolated, not a second overlapping ground skin.
for y in [-119.0,-115.0,-110.0,-105.0,-100.0,-95.01]:
 wall=wall_x(arcade,y);width=arcade['width_m'];datum=arcade['building_grade_m']
 for offset in [.01,width/2,width-.01]:
  x=wall-offset;h=hits(x,y);assert len(h)==1,(x,y,h)
  expected=(1-offset/width)*datum+(offset/width)*surface.height(wall-width,y)
  assert abs(h[0][1][1].z-expected)<.01,(x,y,h[0][1][1].z,expected)
 sample(wall-width-.01,y)
for i,row in enumerate(D['placements']):
 sample(*row['xy'])
 ob=bpy.data.objects[f"Furniture {row['kind']} {i:02d}"];assert abs(ob.location.z-surface.height(*row['xy']))<1e-6
for x in [-5.301,-5.299,-4.301]:sample(x,-144)
# London owns these points; this asset must not duplicate its existing footways.
for p in [(-8,-136),(-8,-152),(0,-144)]:assert not hits(*p),(p,'London ownership overlap')
for x in [-170,-95]:
 y=next(a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1]) for a,b in zip(D['centreline'],D['centreline'][1:]) if a[0]<=x<=b[0]);sample(x-.001,y);sample(x+.001,y)
sys.path.insert(0,str(REPO/'tools'));from coplanar import check_blender
check_blender(ground)
report={'objects':len(obs),'ground_objects':len(ground),'triangles':sum(len(o.data.loop_triangles) for o in obs),'checks':'Continuous pedestrian route and access branches; furniture feet on ground; London ownership exclusions; shared tile seams; finite nondegenerate float32 triangles; no same-facing coplanar ground overlap.','limitations':D['uncertainty']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
