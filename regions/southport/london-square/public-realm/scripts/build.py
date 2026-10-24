"""Construct the researched square from explicit layout and reusable street parts."""
import os,sys,json,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(REPO/'lib'))
from southport3d.geometry import Mesh,text_object
from southport3d.street import sagging_chain,guardrail
sys.path.insert(0,str(ROOT/"scripts"))
from furniture_lod import furniture
from southport3d.road import marking_segments,parallel
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(ROOT/'scripts'))
from extensions import PARTS, build_extensions
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
collections={}
for name in ['ne-ground','sw-ground','island-ground','roads','perimeter','ne-furniture','sw-furniture','island-furniture']+list(PARTS):
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name]=c

def mat(name,color,texture=None,normal=False,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.82;p.inputs['Metallic'].default_value=metal
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if normal:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures/paving-normal.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
 return m
mixed=mat('Authored mixed rectangular paving',(.45,.43,.39),'mixed',True);pale=mat('Authored pale paving',(.64,.62,.55),'pale',True);dark=mat('Authored charcoal paving',(.08,.09,.10),'dark',True)
roadpavers=mat('Authored dark service road blocks',(.25,.26,.25),'service-road')
asphalt=mat('Authored asphalt',(.08,.08,.08),'asphalt');redroad=mat('Authored reddish carriageway',(.22,.11,.09),'red-road');kerb=mat('Pale granite kerb',(.40,.40,.36));yellow=mat('Faded yellow road marking',(.65,.47,.10));white=mat('Worn white road marking',(.69,.68,.60));tactile=mat('Buff tactile paving',(.48,.34,.19));iron=mat('Access covers',(.075,.08,.08),metal=.25)
fm=[mat('Painted dark iron',(.025,.033,.031),metal=.35),mat('Galvanised metal',(.45,.48,.47),metal=.65),mat('Pale backing',(.65,.65,.59)),mat('Push button edging',(.8,.48,.015)),mat('Unlit red lens',(.14,.008,.008)),mat('Unlit amber lens',(.16,.075,.005)),mat('Unlit green lens',(.004,.10,.035)),mat('Weathered bench slats',(.25,.20,.13)),mat('Dark opening',(.006,.008,.008))]

def grade(y,road=False):return D['grade']['origin_z']+D['grade']['dz_dy']*max(-36,min(36,y))-(D['grade']['road_drop'] if road else 0)
def finish(m,material,part,slope=True):
 o=m.finish([material],collections[part]);uv=o.data.uv_layers.new(name='Metric repeat')
 for f in o.data.polygons:
  for i in f.loop_indices:
   v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v.x/3.6,v.y/3.6)
 if slope:
  for v in o.data.vertices:v.co.z+=grade(v.co.y)
 o['placement_status']='Authored from photographic observations; metric dimensions estimated';return o

def polygon(name,pts,material,part,z=0):
 m=Mesh(name);area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]));pts=pts if area>0 else list(reversed(pts));m.add([(x,y,z) for x,y in pts],[tuple(range(len(pts)))]);return finish(m,material,part)
def rect(name,x0,y0,x1,y1,material,part,z=.002):return polygon(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],material,part,z)
def line(name,pts,width,material,part,z=.003):
 m=Mesh(name)
 for a,b in zip(pts,pts[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
  if not l:continue
  nx,ny=-dy/l*width/2,dx/l*width/2;m.add([(a[0]-nx,a[1]-ny,z),(b[0]-nx,b[1]-ny,z),(b[0]+nx,b[1]+ny,z),(a[0]+nx,a[1]+ny,z)],[(0,1,2,3)])
 return finish(m,material,part)
def open_kerb(points,inside,part):
 inner=parallel(points,inside*.19)
 mesh=Mesh('Kerb aligned street edge')
 for i,(a,b) in enumerate(zip(points,points[1:])):
  p,q=inner[i],inner[i+1]
  # Top faces must point upward on either side of the directed kerb. The
  # ground cutter skips downward faces, otherwise leaving paving underneath.
  top=(3,2,5,4) if inside>0 else (4,5,2,3)
  mesh.add([(a[0],a[1],-.12),(b[0],b[1],-.12),(b[0],b[1],.004),(a[0],a[1],.004),(p[0],p[1],.004),(q[0],q[1],.004)],[(0,1,2,3),top])
 return finish(mesh,kerb,part)


def london_kerb(side):
 if side>0:return [(4.3,-154),(4.3,-25.3)]
 return [(side*4.3,-154),(side*4.3,-46),(side*6.2,-36),(side*6.2,-27.3)]


def paint_edge(name, points, side, part, bounds=None, closed=False):
 from southport3d.planar import halfplane
 # Offset both paint edges along the whole kerb curve, so neighbouring
 # segments share exact mitred vertices instead of separate rectangle ends.
 for distance in (.18,.36):
  left=parallel(points,side*distance+.075/2,closed)
  right=parallel(points,side*distance-.075/2,closed)
  for i in range(len(left)-1):
   poly=[left[i],right[i],right[i+1],left[i+1]]
   if bounds:
    x0,y0,x1,y1=bounds
    for c,d in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:
     poly=halfplane(poly,c,d,True)
   if len(poly)>=3:polygon('Marking '+name,poly,yellow,part,-.111)



def offset(pts,amount):
 # Offset closed CCW polygons with bounded mitres.
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))<0:pts=list(reversed(pts))
 result=[]
 for i,p in enumerate(pts):
  prev=Vector(p)-Vector(pts[i-1]);nxt=Vector(pts[(i+1)%len(pts)])-Vector(p);prev.normalize();nxt.normalize();a=Vector((prev.y,-prev.x));b=Vector((nxt.y,-nxt.x));n=a+b;n.normalize();result.append(tuple(Vector(p)+n*(amount/max(.3,n.dot(a)))))
 return result

def edge(name,pts,part):
 inner=offset(pts,-.19);outer=offset(pts,0);m=Mesh('Kerb '+name)
 for i in range(len(pts)):
  j=(i+1)%len(pts)
  if abs(outer[i][0])>40.9 and abs(outer[j][0])>40.9:continue  # open scene boundary, not a kerb
  m.add([(outer[i][0],outer[i][1],-.12),(outer[j][0],outer[j][1],-.12),(outer[j][0],outer[j][1],.004),(outer[i][0],outer[i][1],.004),(inner[i][0],inner[i][1],.004),(inner[j][0],inner[j][1],.004)],[(0,1,2,3),(3,2,5,4)])
 finish(m,kerb,part)
 # Cut the pair at the actual tile boundary, not the expanded offset polygon.
 # There is no return line on an ownership boundary.
 q=pts if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))>0 else list(reversed(pts))
 curves=list(marking_segments(q,-1,(-41,-36,41,36),closed=True))
 for _,(a,b) in curves:
  if abs(a[0])>=40.999 and abs(b[0])>=40.999:continue
  line('Marking double yellow '+name,[a,b],.075,yellow,'roads',-.111)

# Rounded Prezzo kerb observed in August 2024 Street View. Radius/registration
# are visually calibrated; reuse this boundary for paving, kerb and road paint.
prezzo_curve=[(-12.4+6.2*math.cos(t),-27.3+6.2*math.sin(t))
 for t in [math.pi/2-i*math.pi/24 for i in range(13)]]
prezzo_approach=[(-41,-21.1)]+prezzo_curve

# Road base is continuous. Red surfacing is the island-loop material observed in imagery.
rect('Surface roads',-41,-27,41,36,asphalt,'roads',-.12)
rect('Surface London neck',-10,-36,8.5,-27,asphalt,'roads',-.12)
polygon('Surface red island carriageways',[(-18,21),(18,21),(14,19),(13,16),(13.1,-19),
 (8,-19.9),(5.5,-21.4),(4.3,-25.3),(4.3,-28),(-6.2,-28),
 *list(reversed(prezzo_curve)),(-13.1,-19),(-13,16),(-14,19)],redroad,'roads',-.118)
rect('Surface Lord Street service pavers',-41,-23.6,-13.1,-14.8,roadpavers,'roads',-.117)
rect('Surface St Georges service pavers',13.1,-23.6,41,-14.8,roadpavers,'roads',-.117)
for side,label in [(1,'ne'),(-1,'sw')]:
 pts=D['courts'][label];polygon('Surface '+label+' mixed paving',pts,mixed,label+'-ground');edge(label+' forecourt',pts,label+'-ground')
 # Paving panel runs along site X from road to colonnade, not along the building elevation.
 x0,x1=sorted([side*D['patterns']['panel_x_min'],side*D['patterns']['panel_x_max']]);rect('Pattern '+label+' field',x0,-6.8,x1,6.8,dark,label+'-ground',.005)
 for yy in [-7.6,6.8]:rect('Pattern '+label+' pale border',x0,yy,x1,yy+.8,pale,label+'-ground',.006)
 for k,xx in enumerate(D['patterns']['court_centres_x']):
  x=side*xx;rect('Pattern '+label+' square',x-2.25,-2.25,x+2.25,2.25,pale,label+'-ground',.008)
  rect('Pattern '+label+' square inset',x-1.05,-1.05,x+1.05,1.05,dark,label+'-ground',.010)
  for yy in [-5.6,4.15]:rect('Pattern '+label+' side bar',x-2.1,yy,x+2.1,yy+1.45,pale,label+'-ground',.008)
  if k==2:
   # Checker at the colonnade end, inside nested square borders.
   rect('Pattern '+label+' checker border',x-1.75,-1.75,x+1.75,1.75,dark,label+'-ground',.011)
   rect('Pattern '+label+' checker backing',x-1.5,-1.5,x+1.5,1.5,pale,label+'-ground',.012)
   for i in range(3):
    for j in range(3):
     if (i+j)%2==0:rect('Pattern '+label+' checker',x-1.2+i*.8,-1.2+j*.8,x-.4+i*.8,-.4+j*.8,dark,label+'-ground',.013)
# Island is a capsule, with continuous curved kerb and central motif around the obelisk.
r=7.6;cy=17.1-r;island=[(r*math.cos(t),cy+r*math.sin(t)) for t in [i*math.pi/32 for i in range(33)]]+[(r*math.cos(t),-cy+r*math.sin(t)) for t in [math.pi+i*math.pi/32 for i in range(33)]]
polygon('Surface island',island,mixed,'island-ground',.0075);edge('island',island,'island-ground')
rect('Pattern island charcoal field',-5.8,-10,5.8,10,dark,'island-ground',.013)
rect('Pattern island pale square',-4.5,-4.5,4.5,4.5,pale,'island-ground',.015)
rect('Pattern island central inset',-2.7,-2.7,2.7,2.7,dark,'island-ground',.017)
for y in [-8.5,6.8]:rect('Pattern island end bar',-4.4,y,4.4,y+1.7,pale,'island-ground',.015)
for x in [-5.1,3.8]:
 for y in [-5.9,3.8]:rect('Pattern island corner bar',x,y,x+1.3,y+2.1,pale,'island-ground',.015)
# Bounded outer continuity surfaces; detailed streets beyond the square await their own assets.
for s in [-1,1]:
 x0,x1=sorted([s*6.2,s*41])
 if s<0:
  polygon('Surface Prezzo corner pavement',[(-41,-29),(-6.2,-29)]+list(reversed(prezzo_approach)),mixed,'perimeter')
 else:
  polygon('Surface NatWest corner pavement',[(4.3,-27),(41,-27),(41,-19.9),
   (8,-19.9),(6.5,-20.3),(5.4,-21),(4.7,-22.4),(4.35,-24.5),(4.3,-25.3)],mixed,'perimeter')
 x0,x1=sorted([s*(6.2 if s<0 else 4.3),s*(10 if s<0 else 8.5)]);rect('Surface London neck footway',x0,-36,x1,(-29 if s<0 else -27),mixed,'perimeter')
 x0,x1=sorted([s*6,s*41]);rect('Surface perimeter north approximate',x0,31,x1,36,mixed,'perimeter')
# The mapped Prezzo corner reveals the old generic footway was too far back.
# Retain building registration and give its doorway an estimated continuous approach.
from southport3d.landscape import capped_wall
approach=prezzo_approach
open_kerb(approach,-1,'perimeter')
paint_edge('Prezzo approach edge',approach,1,'roads',(-41,-36,41,36))
natwest_approach=[(4.3,-25.3),(4.35,-24.5),(4.7,-22.4),(5.4,-21),
 (6.5,-20.3),(8,-19.9),(41,-19.9)]
open_kerb(natwest_approach,-1,'perimeter')
paint_edge('NatWest approach edge',natwest_approach,1,'roads',(-41,-36,41,36))
# Continuous London Street neck edges use the same setback as its first tile.
for side in [-1,1]:
 x=side*(6.2 if side<0 else 4.3)
 end=-27.3 if side<0 else -25.3
 open_kerb([(x,-36),(x,end)],-side,'perimeter')
 paint_edge('London neck edge',london_kerb(side),side,'roads',(-10,-36,8.5,end))

# Flaring approach divider seen from London Street, rather than a paint line
# ending at the rectangular red-material patch. Dimensions are visual estimates.
line('Marking London approach divider',[(-.3,-35),(0,-29),(-.6,-24),(-2.6,-19)],.10,white,'roads',-.110)
line('Marking London approach fork',[(0,-29),(2,-24),(5.9,-19)],.10,white,'roads',-.110)

# Observed crossing studs and stop bars; positions follow the reconstructed kerb geometry.
for s in [-1,1]:
 x0,x1=sorted([s*7.8,s*12.9])
 for y in [11,13]:
  for i in range(9):rect('Marking crossing stud',x0+i*(x1-x0)/8-.045,y-.045,x0+i*(x1-x0)/8+.045,y+.045,white,'roads',-.114)
 rect('Marking stop bar',x0,14.3,x1,14.55,white,'roads',-.114)
 # Tactile pads are explicitly estimated, not a compliance claim.
 for x,part in [(s*6.2,'island-ground'),(s*14.2,('ne' if s>0 else 'sw')+'-ground')]:
  rect('Tactile estimated crossing pad',x-.4,11,x+.4,13,tactile,part,.020)
 for y in [-7,3]:
  x=s*10.1;m=Mesh('Marking direction arrow');pts=[(-.12,-1),(.12,-1),(.12,.35),(.5,.35),(0,1),(-.5,.35),(-.12,.35)]
  # opposite directions around the island
  polygon('Marking direction arrow',[(x+s*a,y+s*b) for a,b in pts],white,'roads',-.113)
# Dashed Lord Street centre line, interrupted across junction and crossings.
for x in range(-42,42,6):
 if -14<x<16:continue
 rect('Marking Lord Street lane dash',max(-41,x),25.55,min(41,x+2),25.65,white,'roads',-.111)
# Access covers and drains: generic dimensions, placements explicitly interpreted.
for side,label in [(1,'ne'),(-1,'sw')]:
 for x,y in [(20,8),(28,-9)]:
  rect('Cover access '+label,side*x-.3,y-.3,side*x+.3,y+.3,iron,label+'-ground',.015)
 for y in [-10,8]:
  x=side*12.85;rect('Marking drainage grate',x-.15,y-.24,x+.15,y+.24,iron,'roads',-.112)
  for i in range(6):line('Marking drainage slots',[(x-.11,y-.2+i*.08),(x+.11,y-.2+i*.08)],.015,kerb,'roads',-.111)
# One source mesh per furniture family, independent transforms for every placement.
prototypes={}
for i,record in enumerate(D['furniture']):
 kind=record['kind'];name=f'Furniture {kind} {i:03d}';x,y=record['xy']
 if kind not in prototypes:
  ob=furniture(kind,'detail',name).finish(fm,collections[record['part']]);prototypes[kind]=ob
 else:
  ob=prototypes[kind].copy();ob.data=prototypes[kind].data;collections[record['part']].objects.link(ob);ob.name=name
 ob.location=(x,y,grade(y)+(.0075 if record['part']=='island-furniture' else 0));ob.rotation_euler.z=math.radians(record['yaw']);ob['source']=record['source'];ob['placement_uncertainty_m']=1.5
for side in [-1,1]:
 pts=[(side*6.95,y,grade(y)+.0075) for y in [-10,-7.5,-5,-2.5,0,2.5,5,7.5,10]]
 m=sagging_chain(pts);m.name='Chain island '+str(side);m.finish(fm,collections['island-furniture'])
 label='ne' if side>0 else 'sw';pts=[(side*x,y,grade(y)) for x,y in [(14.2,17),(15.5,19),(18,20),(22,20)]]
 m=guardrail(pts);m.name='Guardrail '+label;m.finish(fm,collections[label+'-furniture'])
build_extensions(globals())

# Remove underlying surfaces rather than relying on millimetre depth offsets.
# This prevents z-fighting in browsers and other GLB viewers, at oblique distances.
sys.path.insert(0,str(ROOT/'scripts'))
from southport3d.planar import subtract,area
from mathutils.geometry import tessellate_polygon
for part,collection in collections.items():
 if part.endswith('-furniture'):continue
 rows=[]
 for o in list(collection.objects):
  for face in o.data.polygons:
   points=[tuple(o.data.vertices[i].co) for i in face.vertices]
   offsets=[p[2]-grade(p[1]) for p in points]
   if max(offsets)-min(offsets)>1e-5:continue  # vertical kerb face
   xy=[(p[0],p[1]) for p in points]
   # Earlier road/footway clipping can retain repeated boundary corners. A
   # zero-length cutter edge classifies the entire subject as both inside and
   # outside, duplicating pavement fragments instead of subtracting a strip.
   xy=[p for i,p in enumerate(xy) if math.dist(p,xy[i-1])>1e-8]
   if len(xy)<3:continue
   signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))
   if signed<=0:continue
   # Convex quads/outline faces are common; triangulate concave arrow faces.
   crosses=[(xy[(i+1)%len(xy)][0]-xy[i][0])*(xy[(i+2)%len(xy)][1]-xy[(i+1)%len(xy)][1])-(xy[(i+1)%len(xy)][1]-xy[i][1])*(xy[(i+2)%len(xy)][0]-xy[(i+1)%len(xy)][0]) for i in range(len(xy))]
   cutters=[xy] if min(crosses)>=-1e-7 else [[xy[v] if isinstance(v,int) else (v.x,v.y) for v in tri] for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in xy]])]
   cutters=[c for c in cutters if area(c)>1e-9]
   rows.append((o,face.index,sum(offsets)/len(offsets),xy,cutters))
 replacements={}
 order={(o,index):i for i,(o,index,*_) in enumerate(rows)}
 for o,index,z,xy,_ in rows:
  fragments=[xy]
  for other,otherindex,oz,_,cutters in rows:
   # Road offsets encode layering priority before all road materials are
   # flattened to the same physical datum below. Even a high-priority return
   # lane must cut the underlying asphalt or the two become coplanar later.
   road_materials=[asphalt,redroad,roadpavers,yellow,white]
   both_road=(o.data.materials[0] in road_materials and other.data.materials[0] in road_materials)
   # Paint belongs above every carriageway, including high-priority returns.
   drainage=o.name.startswith('Marking drainage')
   other_drainage=other.name.startswith('Marking drainage')
   if drainage or other_drainage:both_road=True
   priority=(3 if 'slots' in o.name else 2)+z if drainage else (1+z if both_road and o.data.materials[0] in [yellow,white] else z)
   other_priority=(3 if 'slots' in other.name else 2)+oz if other_drainage else (1+oz if both_road and other.data.materials[0] in [yellow,white] else oz)
   if other_priority<priority-1e-6:continue
   if oz-z>.04 and not both_road:continue
   if abs(other_priority-priority)<=1e-6 and order[(other,otherindex)]<=order[(o,index)]:continue
   for cutter in cutters:
    fragments=[piece for frag in fragments for piece in subtract(frag,cutter)]
  replacements[(o,index)]=(z,fragments)
 for o in list(collection.objects):
  m=Mesh(o.name)
  for face in o.data.polygons:
   if (o,face.index) in replacements:
    z,fragments=replacements[(o,face.index)]
    for poly in fragments:m.add([(x,y,grade(y)+z) for x,y in poly],[tuple(range(len(poly)))])
   else:
    pts=[tuple(o.data.vertices[i].co) for i in face.vertices];m.add(pts,[tuple(range(len(pts)))])
  if not m.faces:bpy.data.objects.remove(o,do_unlink=True);continue
  o.data.clear_geometry();o.data.from_pydata(m.vertices,[],m.faces);o.data.update()
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Metric repeat')
  for f in o.data.polygons:
   for i in f.loop_indices:
    v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v.x/3.6,v.y/3.6)

# Height offsets above were ordering priorities for cutouts, not floating paint.
# Flatten road materials onto their physical datum after clipping.
for part,collection in collections.items():
 if part.endswith('-furniture'):continue
 for ob in collection.objects:
  if ob.data.materials and ob.data.materials[0] in [mixed,pale,dark,kerb]:
   for vertex in ob.data.vertices:
    if abs(vertex.co.z-grade(vertex.co.y))<.04:vertex.co.z=grade(vertex.co.y)
  if ob.name.startswith('Marking drainage') or (ob.data.materials and ob.data.materials[0] in [asphalt,redroad,roadpavers,yellow,white]):
   for vertex in ob.data.vertices:
    vertex.co.z=grade(vertex.co.y)-.12

# Tactile crossing at the mapped Sainsbury's path: drop the pavement to the
# carriageway at each kerb while retaining the higher rear landing.
for ob in collections['ne-garden-ground'].objects:
 if ob.name.startswith('Surface Sainsbury ramp') or ob.name.startswith('Tactile Sainsbury'):
  south='south' in ob.name
  low=min(v.co.y for v in ob.data.vertices);high=max(v.co.y for v in ob.data.vertices)
  for vertex in ob.data.vertices:
   fraction=max(0,min(1,(vertex.co.y-low)/(high-low) if south else (high-vertex.co.y)/(high-low)))
   vertex.co.z=grade(vertex.co.y)-.12*fraction

# Drop the London Street landing edge to road level; keep adjoining footway level.
for o in collections['london-3-ground'].objects:
 if o.name.startswith(('Surface crossing ramp','Tactile London')):
  for v in o.data.vertices:
   v.co.z-=.12*max(0,min(1,(5.4-abs(v.co.x))/1.1))

# Pools are horizontal even though surrounding lawn/edging follows the site grade.
# Do this after the plan cutouts, so the lawn cannot fill the basin at its high end.
for o in bpy.data.objects:
 if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Still dark pool water':
  ys=[v.co.y for v in o.data.vertices];zs=[v.co.z-grade(v.co.y) for v in o.data.vertices]
  water_z=grade((min(ys)+max(ys))/2)+sum(zs)/len(zs)
  for v in o.data.vertices:v.co.z=water_z

# Batch authored surface pieces by policy/material within each spatial part.
# Furniture stays instanced; avoid hundreds of draw calls for individual paint strips.
for collection in collections.values():
 groups={}
 for o in list(collection.objects):
  if o.type=='MESH' and o.name.split(' ')[0] in {'Surface','Pattern','Marking','Cover','Tactile'}:
   groups.setdefault((o.name.split(' ')[0],o.data.materials[0].name),[]).append(o)
 for (family,material),objects in groups.items():
  if len(objects)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
  objects[0].name=family+' '+collection.name+' '+material

# Resolve boundary T-junctions across all ground parts together, including
# painted strips and the independent street tiles. Furniture stays instanced.
import southport3d.conform as conforming
# Broad 0.2 mm insertion admitted off-edge points into thin kerb caps,
# creating inverted triangle fans. Keep only genuinely shared boundaries.
conforming.GRID=1e-6
conforming.TOLERANCE=1e-7
conform=conforming.conform
compiled={}
for part,collection in collections.items():
 if part.endswith('-furniture'):continue
 for ob in collection.objects:
  mesh=Mesh(ob.name)
  for face in ob.data.polygons:
   pts=[tuple(ob.data.vertices[i].co) for i in face.vertices]
   # Triangulate first: the conformer expects convex faces, and this asset also
   # contains concave arrows and rounded court outlines.
   for tri in tessellate_polygon([[Vector(p) for p in pts]]):
    mesh.add([pts[v] if isinstance(v,int) else tuple(v) for v in tri],[(0,1,2)])
  compiled[ob.name]=mesh
import numpy as np
for mesh in compiled.values():mesh.vertices=np.asarray(mesh.vertices,dtype=np.float32).tolist()
compiled,report=conform(compiled)
for name,mesh in compiled.items():
 ob=bpy.data.objects[name]
 ob.data.clear_geometry()
 ob.data.from_pydata(mesh.vertices,[],mesh.faces)
 ob.data.update()
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='Metric repeat')
 for face in ob.data.polygons:
  for loop in face.loop_indices:
   v=ob.data.vertices[ob.data.loops[loop].vertex_index].co
   uv.data[loop].uv=(v.x/3.6,v.y/3.6)
# Clipping meeting road strips can leave zero-area slivers after float conversion.
# Remove those faces in the new corridor rather than exporting invalid normals.
import bmesh
# A near-collinear cap fan can fold after float32 rounding even with strict
# insertion tolerance. Discard only microscopic inverted residues; larger
# inverted tops remain an error in validation, never silently reversed.
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith('Kerb aligned street edge'):
  bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update()
  bad=[f for f in bm.faces if f.normal.z<-.5 and f.calc_area()<1e-5]
  if bad:
   print('Discarding float32 kerb cap residues',ob.name,len(bad),sum(f.calc_area() for f in bad))
   bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);ob.data.update()
  bm.free()
for ob in list(collections['rear-streets-ground'].objects)+list(collections['block-ground'].objects):
 bm=bmesh.new();bm.from_mesh(ob.data)
 bad=[f for f in bm.faces if f.calc_area()<1e-7]
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 bm.to_mesh(ob.data);bm.free();ob.data.update()
 # Mesh polygons use float32 area calculations; a long collinear triangle can
 # have nonzero BMesh area but collapse after conversion. Check that result too.
 collapsed=[f.index for f in ob.data.polygons if f.area<1e-8]
 if collapsed:
  bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
  bmesh.ops.delete(bm,geom=[bm.faces[i] for i in collapsed],context='FACES_ONLY')
  bm.to_mesh(ob.data);bm.free();ob.data.update()
(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2))

# Pack generated images for self-contained source output; no external reference pixels.
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.world.color=(.35,.35,.35)
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.4;o=bpy.data.objects.new('Sun',sun);scene.collection.objects.link(o);o.rotation_euler=(.5,-.4,-.5)
data=bpy.data.cameras.new('Area overview');cam=bpy.data.objects.new('Area overview',data);scene.collection.objects.link(cam);cam.location=(205,-242,220);cam.rotation_euler=(Vector((25,-48,0))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=285;scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
print('Public realm built:',len(D['furniture']),'furniture placements')
