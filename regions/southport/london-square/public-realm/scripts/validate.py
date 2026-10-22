from pathlib import Path
import bpy,json,math
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];layout=json.loads((ROOT/'research/layout.json').read_text())
assert len([o for o in meshes if o.name.startswith('Furniture ') and ' extension ' not in o.name])==len(layout['furniture'])
assert len([o for o in meshes if o.name.startswith('Chain ')])==2
assert all(math.isfinite(v) for o in meshes for p in o.data.vertices for v in p.co)
assert all(o.data.polygons for o in meshes)
assert all(o.data.uv_layers for o in meshes if o.name.startswith(('Surface ','Pattern ')))
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
(ROOT/'research/validation.json').write_text(json.dumps({'mesh_objects':len(meshes),'furniture_placements':len(layout['furniture']),'checks':'finite geometry, complete placement count, packed maps, ground UVs'},indent=2))
print('Public realm geometry validated')
# Validate the shared generator levers independently of published instance totals.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
sys.path.insert(0,str(ROOT/"scripts"))
from furniture_lod import furniture
for kind in {f['kind'] for f in layout['furniture']}:
 counts=[]
 for level in ['detail','walk','district']:
  m=furniture(kind,level);counts.append(sum(len(f)-2 for f in m.faces))
  assert all(math.isfinite(c) for v in m.vertices for c in v)
 assert counts[0]>counts[1]>counts[2],(kind,counts)
print('Furniture generator reductions validated')

# Every base is on its assigned pavement, including the narrowing island ends.
for f in layout['furniture']:
 x,y=f['xy']
 if f['part']=='island-furniture':
  radius=layout['island']['width']/2;cap=max(0,abs(y)-(layout['island']['length']/2-radius))
  assert x*x+cap*cap<radius*radius,(f,'off island')
 else:
  poly=layout['courts']['ne' if f['part']=='ne-furniture' else 'sw'];crosses=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):crosses.append((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))
  assert min(crosses)>=-1e-5 or max(crosses)<=1e-5,(f,'off forecourt')
  if f['kind']=='bollard':assert not (abs(x)<14 and 11<y<13),'Bollard obstructs crossing'
print('Furniture pavement containment and crossing clearance validated')

# Extension coverage, open seams, and bounded longitudinal grade.
sys.path.insert(0,str(ROOT/'scripts'))
from extensions import PARTS
assert all(bpy.data.collections.get(n) and len(bpy.data.collections[n].objects) for n in PARTS)
from landscape_lod import tree
counts=[sum(len(f)-2 for f in tree(level).faces) for level in ['detail','walk','district']]
assert counts[0]>counts[1]>counts[2],counts
from mathutils import Vector
for level in ['detail','walk','district']:
 canopy=tree(level);volume=0
 for face,material in zip(canopy.faces,canopy.indices):
  if material==0:continue
  a=Vector(canopy.vertices[face[0]])
  for j in range(1,len(face)-1):
   b,c=(Vector(canopy.vertices[k]) for k in (face[j],face[j+1]))
   assert (b-a).cross(c-a).length>1e-8,(level,'Collapsed canopy face')
   volume+=a.dot(b.cross(c))/6
 assert volume>0,(level,'Inward canopy shells')
assert len([o for o in meshes if o.name.startswith('Tree ')])==sum(len(v) for v in json.loads((ROOT/'research/streets.json').read_text())['trees'].values())
for name in ['london-1-ground','london-2-ground','london-3-ground']:
 vertices=[v.co.z for o in bpy.data.collections[name].objects for v in o.data.vertices]
 assert max(vertices)-min(vertices)<.3,(name,'Unbounded grade or furniture in ground')
print('Extended areas, tree LODs and bounded road grades validated')

# The SW return replaces underlying asphalt even though its construction
# priority is above footway height. Count triangles, not objects: batching can
# hide two coplanar layers inside one object. Avoid triangulation boundaries.
from mathutils.geometry import intersect_ray_tri
return_objects=list(bpy.data.collections['sw-garden-ground'].objects)
for ob in return_objects:ob.data.calc_loop_triangles()
for y in [-19.137,-10.137,.137,10.137,19.137]:
 hits=[]
 for ob in return_objects:
  for triangle in ob.data.loop_triangles:
   hit=intersect_ray_tri(*(ob.data.vertices[i].co for i in triangle.vertices),Vector((0,0,-1)),Vector((-69.137,y,10)),True)
   if hit is not None:hits.append((ob.name,hit.z))
 assert len(hits)==1,(y,'Overlapping return-road surfaces',hits)
print('SW return road has one physical surface after priority flattening')

rear_paving=[ob for ob in bpy.data.collections['rear-streets-ground'].objects
             if any(m.name=='Authored mixed rectangular paving' for m in ob.data.materials)]
for ob in rear_paving:ob.data.calc_loop_triangles()
for x,y in [(25.31354,-77.78526),(25.88249,-77.31763),(80.137,-83.4137),(110.137,-86.3137)]:
 hits=[]
 for ob in rear_paving:
  for triangle in ob.data.loop_triangles:
   hit=intersect_ray_tri(*(ob.data.vertices[i].co for i in triangle.vertices),Vector((0,0,-1)),Vector((x,y,10)),True)
   if hit is not None:hits.append(hit.z)
 assert len(hits)==1,(x,y,'Duplicated or missing Anchor footway fragments',hits)
print('Anchor footway cutter fragments have one pavement layer')

# The photographed garden row extends, rather than duplicates, the core row.
front=json.loads((ROOT/'research/streets.json').read_text())['sw_frontage_2024']
posts=[o for o in meshes if o.name.startswith('Furniture bollard ')]
positions=[tuple(round(c,3) for c in o.location[:2]) for o in posts]
assert len(set(positions))==len(positions),'Duplicated bollard placements'
for x in front['garden_bollards_x']:
 assert (x,front['garden_bollards_y']) in positions
 assert x>-66,'Post blocks SW garden service-road opening'
for x in front['shop_bollards_x']:
 assert (x,front['shop_bollards_y']) in positions
 assert -23.6<front['shop_bollards_y']< -21.1,'Post off frontage footway'
assert len([o for o in meshes if o.name.startswith('Garden globe lamp')])==4
from garden_front import globe_lamp,balustrade
for factory in [globe_lamp,balustrade]:
 counts=[sum(len(f)-2 for f in factory(level).faces) for level in ['detail','walk','district']]
 assert counts[0]>counts[1]>counts[2],(factory.__name__,counts)
print('Photographed garden furniture placement and LOD reductions validated')

# Cast against the assembled surface, not construction metadata: each yellow
# pair meets its neighbour and the detailed Glebe throat has one owner.
from mathutils import Vector
depsgraph=bpy.context.evaluated_depsgraph_get()
def ground_hit(x,y):
 hit,point,normal,index,ob,matrix=bpy.context.scene.ray_cast(depsgraph,Vector((x,y,30)),Vector((0,0,-1)))
 return ob,point if hit else None
for x in [-71.82,-71.64,-66.18,-66.36]:
 ob,p=ground_hit(x,.137)
 assert ob and any(m.name=='Faded yellow road marking' for m in ob.data.materials),(x,'Return lane has erased its yellow lines')
for station in [-41,41]:
 for y in [21.18,21.36,-14.98,-15.16,*([-20.92,-20.74] if station<0 else [-19.72,-19.54])]:
  left,lp=ground_hit(station-.015,y)
  right,rp=ground_hit(station+.015,y)
  assert left and right,(station,y,'uncovered seam')
  assert 'Faded yellow road marking' in [m.name for m in left.data.materials],(station,y,left.name)
  assert 'Faded yellow road marking' in [m.name for m in right.data.materials],(station,y,right.name)
  assert abs(lp.z-rp.z)<.0005,(station,y,'paint step')
for station in [-76,-116]:
 for x in [-4.12,-3.94,3.94,4.12]:
  before,p=ground_hit(x,station-.015)
  after,q=ground_hit(x,station+.015)
  assert before and after
  assert 'Faded yellow road marking' in [m.name for m in before.data.materials]
  assert 'Faded yellow road marking' in [m.name for m in after.data.materials]
  assert abs(p.z-q.z)<.0005
ob,p=ground_hit(-7,-66.5)
assert ob is None,'London Square still overlaps the detailed Glebe throat'
print('Exportable yellow-line seams and single Glebe ownership validated')

# NatWest's square corner must have a walkable apron around both elevations.
# Old generic mirrored kerbs crossed through the stone corner pier.
for x,y in [(6.3,-23.0),(7.5,-21.4),(10,-21),(20,-21),(29,-21),(5.3,-30),(5.3,-40)]:
 ob,p=ground_hit(x,y)
 assert ob and any(m.name=='Authored mixed rectangular paving' for m in ob.data.materials),(x,y,ob.name if ob else None,'NatWest apron is not paving')
 assert abs(p.z-(-.0075-.022*max(-36,min(36,y))))<.005
# The red mouth continues across the old Y=-23 rectangle seam to London Street.
for x,y in [(-4,-24),(-4,-26),(3,-24),(3,-26)]:
 ob,p=ground_hit(x,y)
 assert ob and any(m.name=='Authored reddish carriageway' for m in ob.data.materials),(x,y,'Red approach discontinuity')
print('NatWest corner pavement and red approach continuity validated')

for ob in meshes:
 if ob.name.startswith('Furniture bench extension'):
  y=ob.location.y
  expected=1 if 0<y<25 else -1
  facing_y=-math.cos(ob.rotation_euler.z)
  assert facing_y*expected>.99,(ob.name,'bench faces away from intended footway')
print('Lord Street bench seats face the footway, with backs toward planting or shops')

# The Prezzo apron must meet both elevations and remain inside the rounded kerb.
for x,y in [(-22,-22),(-12,-22),(-9,-24),(-7,-27),(-8,-30)]:
 ob,p=ground_hit(x,y)
 assert ob and any(m.name=='Authored mixed rectangular paving' for m in ob.data.materials),(x,y,'Prezzo apron missing')
for x,y in [(-7.5,-23),(-5.8,-28)]:
 ob,p=ground_hit(x,y)
 assert ob and not any(m.name=='Authored mixed rectangular paving' for m in ob.data.materials),(x,y,'Prezzo paving extends into carriageway')
print('Rounded Prezzo pavement and open carriageway validated')

# New routes must be continuous driveable surfaces, including their shared
# T-junction and the existing stub. These rays exclude building models.
for x,y in [(25,-83.5),(40,-84.8),(67.66,-87.56),(100,-90.55),(150,-95.2),(68.1,-28),(68,-50),(67.8,-75),(67.7,-83)]:
 ob,p=ground_hit(x,y)
 assert ob and any(m.name=='Authored asphalt' for m in ob.data.materials),(x,y,'Road extension blocked or missing')
for x,y in [(40,-79),(80,-83.5),(110,-86.3),(80,-94.4),(65.1,-40),(70.8,-45),(-11,-80),(-11,-90),(85,-20),(125,-18.5)]:
 ob,p=ground_hit(x,y)
 assert ob and any(m.name=='Authored mixed rectangular paving' for m in ob.data.materials),(x,y,ob.name if ob else None,'New frontage pavement missing')
print('Post Office / Anchor connection and new frontage paving validated')

for y in [-79.18,-79.36,-87.82,-87.64]:
 left,lp=ground_hit(24.985,y);right,rp=ground_hit(25.015,y)
 assert left and right and all(any(m.name=='Faded yellow road marking' for m in o.data.materials) for o in [left,right]),(y,'Anchor yellow pair does not meet across ownership seam')
 assert abs(lp.z-rp.z)<.0005
print('Anchor Street ownership seam has continuous road-edge paint')

assert all(f.area>=1e-8 for o in bpy.data.collections['rear-streets-ground'].objects for f in o.data.polygons),'Degenerate corridor faces'

# Distinctive signal and lamp silhouettes must survive every generator level.
from mathutils import Vector
for kind in ['pedestrian','signal','lord-street-lamp']:
 for level in ['detail','walk','district']:
  m=furniture(kind,level)
  for face in m.faces:
   a=Vector(m.vertices[face[0]])
   area=sum((Vector(m.vertices[face[j]])-a).cross(Vector(m.vertices[face[j+1]])-a).length/2 for j in range(1,len(face)-1))
   assert area>1e-9,(kind,level,'Collapsed furniture face')
  if kind=='pedestrian':
   for material in [4,6]:
    faces=[f for f,mi in zip(m.faces,m.indices) if mi==material]
    assert faces and all(m.vertices[i][1]<-.24 for f in faces for i in f),(level,'Pedestrian glyph buried')
  if kind=='lord-street-lamp':
   for sign in [-1,1]:
    assert any(v[1]*sign>1.1 and v[2]>5.0 for v in m.vertices),(level,'Missing twin arm')
print('Signal glyph depths, twin lamp arms and non-degenerate local furniture checked')

# Grate metal/slots own their footprint; yellow and white paint cannot cover it.
road_objects=list(bpy.data.collections['roads'].objects)
for ob in road_objects:ob.data.calc_loop_triangles()
for side in [-1,1]:
 for y in [-10,8]:
  for dx,dy in [(-.123,.031),(.017,.113),(.123,-.079)]:
   hits=[]
   for ob in road_objects:
    for tri in ob.data.loop_triangles:
     hit=intersect_ray_tri(*(ob.data.vertices[i].co for i in tri.vertices),Vector((0,0,-1)),Vector((side*12.85+dx,y+dy,10)),True)
     if hit is not None:hits.append((ob,tri.material_index))
   assert len(hits)==1,('Overlapping grate surfaces',side,y,dx,dy,[(o.name,i) for o,i in hits])
   assert hits[0][0].data.materials[hits[0][1]].name in ['Access covers','Pale granite kerb'],'Paint across drainage grate'
print('All four drainage grates own their road-surface footprint')
