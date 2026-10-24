"""Metric seam, coverage and navigable-route checks for the Nevill corridor."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
publication=json.loads((Path(__import__('os').environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/nevill-street/public-realm/publication.json').read_text())
assert all(part.get('ground') is True for part in publication['parts']), 'Every corridor part must participate in viewer ground following'
D=json.loads((ROOT/'research/layout.json').read_text());meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes and all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.y for v in points)>=41-1e-5
assert max(v.y for v in points)<317
# Y41 is a full-width ownership seam. No corridor floor extends below it.
seam=[v for v in points if abs(v.y-41)<1e-5];assert seam
assert all(-.920< v.z < -.795 for v in seam)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def sample(x,y):
 hit,p,n,idx,ob,m=bpy.context.scene.ray_cast(deps,Vector((x,y,20)),Vector((0,0,-1)),distance=30)
 assert hit,(x,y,'ground hole')
 return p.z,ob
# Route centre samples are deliberately spaced independently of construction rows.
for y in range(42,248,3):
 stations=D['stations_y_centre_halfwidth_left_right'];centre=0
 for a,b in zip(stations,stations[1:]):
  if y<=b[0]:
   t=max(0,(y-a[0])/(b[0]-a[0]));centre=a[1]+(b[1]-a[1])*t;break
 sample(centre,y)
for x,y in [(-7,60),(7,60),(-8,130),(7,130),(-22,221),(7,221),(-18,248),(-9,270),(-11,280),(-11,300),(-9,310)]:sample(x,y)
# Adjacent streaming parts must share exactly the same surface height.
for y in [95,185,248.07]:
 for x in ([0] if y<200 else [-18]):
  za,_=sample(x,y-.002);zb,_=sample(x,y+.002);assert abs(za-zb)<.002,(x,y,za,zb)
# Exported triangles must retain nonzero area after Blender's float32 conversion.
# In particular, tiny paint-cutout fragments must not collapse during snapping.
minimum_triangle_area=float('inf')
for ob in meshes:
 ob.data.calc_loop_triangles()
 for tri in ob.data.loop_triangles:
  a,b,c=(ob.data.vertices[i].co for i in tri.vertices)
  triangle_area=(b-a).cross(c-a).length/2
  assert triangle_area>1e-10,(ob.name,tri.index,'collapsed float32 triangle')
  minimum_triangle_area=min(minimum_triangle_area,triangle_area)
conform=json.loads((ROOT/'research/conform.json').read_text())
assert conform['inserted_edge_junctions']>0,'Street clipping should share paint/base edge junctions'

# Independently measure perpendicular distance from constructed paint endpoints
# to their receiving kerb segment, including mitered station changes.
for segment in json.loads((ROOT/'research/marking-centrelines.json').read_text()):
 a,b=segment['kerb'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 for p in segment['paint']:
  distance=abs((p[0]-a[0])*(-dy)+(p[1]-a[1])*dx)/length
  assert abs(distance-segment['offset'])<1e-6,(segment,distance,'varying kerb setback')
# Edge paint must not run across a side-road mouth. Test actual exported paint
# triangle interiors against the independent finite-width junction corridors.
paint_samples=0
for ob in meshes:
 if not ob.name.endswith(' yellow'):continue
 for tri in ob.data.loop_triangles:
  p=sum((ob.data.vertices[i].co for i in tri.vertices),Vector())/3
  for road in D['side_roads']:
   a,b=road['centre'],road['end'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
   along=((p.x-a[0])*dx+(p.y-a[1])*dy)/length
   across=abs((p.x-a[0])*(-dy)+(p.y-a[1])*dx)/length
   assert not (.002<along<length-.002 and across<road['width']/2-.002),(road['name'],tuple(p),'paint blocks junction')
  paint_samples+=1
assert paint_samples>0
report={'minimum_triangle_area_m2':minimum_triangle_area,'joined_edge_junctions':conform['inserted_edge_junctions'],'paint_triangle_samples':paint_samples,'ground_parts':len(publication['parts']),'objects':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),'checks':'finite meshes, UVs, packed authored maps, no ownership overlap south of seam, square road elevation, continuous route and three part seams','uncertainty':'Mapped registration with estimated widths and grade; checks establish geometric continuity, not survey accuracy.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)

# The block plan keeps open spaces navigable and excludes floor below volumes.
for x,y in [(23,154),(18,177),(12,185.2),(-45,201),(-60,205),(-40,44),(25,43),(11.5,210)]:sample(x,y)
from mathutils.geometry import tessellate_polygon
plan=json.loads((Path(__import__('os').environ['SOUTHPORT_REPO_ROOT'])/D['block_plan']).read_text())
excluded_samples=0
for block in plan['blocks']:
 poly=block['footprint'];v=[Vector((x,y,0)) for x,y in poly]
 for tri in tessellate_polygon([v]):
  pts=[v[i] if isinstance(i,int) else i for i in tri];p=sum(pts,Vector())/3
  if not 41<p.y<316:continue
  hit,*_=bpy.context.scene.ray_cast(deps,Vector((p.x,p.y,40)),Vector((0,0,-1)),distance=80)
  assert not hit,(block['id'],tuple(p),'ground intrudes into building footprint')
  excluded_samples+=1
print('Open forecourts/yard covered; building footprint samples excluded:',excluded_samples)

# Authored access routes may declare ground probes independently of their cutters.
for region in D.get('block_ground_areas',[]):
 for x,y in region.get('ground_probes',[]):
  hit,position,*_=bpy.context.scene.ray_cast(deps,Vector((x,y,40)),Vector((0,0,-1)),distance=80)
  assert hit,(region['id'],x,y,'access ground missing')
  if 'height_m' in region:assert abs(position.z-region['height_m'])<.002,(region['id'],tuple(position),'access ground datum')

# Independently test the crossing corridor and both lowered landings. The
# crossing has no kerb wall; grade and sloping pad must meet at the kerb edge.
J=json.loads((Path(__import__('os').environ['SOUTHPORT_REPO_ROOT'])/D['junction_plan']).read_text())
y=46.4
def edge_x(key):
 for a,b in zip(J[key],J[key][1:]):
  if a[1]<=y<=b[1]:return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
g=D['grade'];z=g['start_z']+(y-g['start_y'])*(g['top_z']-g['start_z'])/(g['top_y']-g['start_y'])
for side,key in [(-1,'west_kerb'),(1,'east_kerb')]:
 x=edge_x(key)
 pad,_=sample(x+side*.02,y);road,_=sample(x-side*.02,y)
 assert abs(pad-road)<.004,(key,'raised crossing kerb',pad,road,x)
 assert abs(road-(z-.12))<.002
 back,_=sample(x+side*1.28,y)
 assert abs(back-z)<.004,(key,'landing does not meet pavement')
print('Nevill crossing ramps join road and back of pavement')
