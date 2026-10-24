"""Bounded Nevill Street road corridor, with explicit ownership of every surface."""
import bpy,bmesh,os,sys,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'),str(ROOT/'scripts')]
from southport3d.geometry import Mesh
from southport3d.planar import subtract,area,halfplane
D=json.loads((ROOT/'research/layout.json').read_text())
OSM=json.loads((ROOT/'research/route-osm.json').read_text())
BLOCK_PLAN=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/D['block_plan']).read_text())
J=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/D['junction_plan']).read_text())
def traced_x(key,y):
 points=J[key]
 for a,b in zip(points,points[1:]):
  if a[1]<=y<=b[1]:return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
 raise ValueError((key,y))
# Both assets derive the boundary from the same trace, including all bends.
station_ys=sorted({p[1] for key in ['west_kerb','east_kerb'] for p in J[key] if p[1]>=41}|set(J['nevill_crossing_y']))
new_stations=[]
for y in station_ys:
 left,right=traced_x('west_kerb',y),traced_x('east_kerb',y)
 new_stations.append([y,(left+right)/2,(right-left)/2,-10,9.2])
D['stations_y_centre_halfwidth_left_right']=new_stations+[p for p in D['stations_y_centre_halfwidth_left_right'] if p[0]>48]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.unit_settings.system='METRIC'
parts=['lower-ground','middle-ground','upper-ground','promenade-ground']
C={}
for part in parts:
    C[part]=bpy.data.collections.new(part)
    s.collection.children.link(C[part])
def material(name,colour,texture=None):
 m=bpy.data.materials.new(name)
 m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*colour,1)
 p.inputs['Roughness'].default_value=.85
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage')
  n.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')))
  m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
  n=m.node_tree.nodes.new('ShaderNodeTexImage')
  n.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'-normal.png')))
  n.image.colorspace_settings.name='Non-Color'
  q=m.node_tree.nodes.new('ShaderNodeNormalMap')
  m.node_tree.links.new(n.outputs['Color'],q.inputs['Color'])
  m.node_tree.links.new(q.outputs['Normal'],p.inputs['Normal'])
 return m
mats={'paving':material('Authored pale Nevill slabs',(.60,.58,.52),'paving'),'brick':material('Authored red brick bands',(.4,.22,.17),'brick'),'asphalt':material('Authored asphalt',(.08,.09,.09),'asphalt'),'kerb':material('Granite kerb',(.43,.43,.40)),'white':material('Worn white paint',(.72,.71,.65)),'yellow':material('Worn yellow paint',(.64,.48,.12)),'tactile':material('Estimated buff tactile pads',(.57,.40,.25),'tactile')}
mats['junction-tactile']=material('Junction buff tactile',(.48,.45,.35),'junction-tactile')
rows=[]
verticals=[]
def grade(y):
 g=D['grade']
 t=max(0,min(1,(y-g['start_y'])/(g['top_y']-g['start_y'])))
 return g['start_z']+t*(g['top_z']-g['start_z'])
def level(road=False):
    return lambda x,y:grade(y)-(.12 if road else 0)
def ccw(p):
 p=[tuple(v) for v in p]
 return p if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))>0 else list(reversed(p))
def surface(name,points,mat,priority=0,z=None):
 points=ccw(points)
 if len(points)<3 or area(points)<1e-7:
     return
 # Convex fragments make clipping independent of optional geometry packages.
 triangles=tessellate_polygon([[Vector((x,y,0)) for x,y in points]])
 for tri in triangles:
     rows.append((name,[points[v] if isinstance(v,int) else (v.x,v.y) for v in tri],mat,priority,z or level()))
def quad(name,x0,y0,x1,y1,mat,priority=0,z=None):
    surface(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],mat,priority,z)
def strip(name,a,b,width,mat,priority=0,z=None):
 dx,dy=b[0]-a[0],b[1]-a[1]
 length=math.hypot(dx,dy)
 if length<1e-5:
     return
 nx,ny=-dy/length*width/2,dx/length*width/2
 surface(name,[(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],mat,priority,z)
def kerb(a,b,inside=1):
 # The cap is partitioned out of paving; only the vertical face is a second mesh.
 dx,dy=b[0]-a[0],b[1]-a[1]
 length=math.hypot(dx,dy)
 nx,ny=-dy/length*.18*inside,dx/length*.18*inside
 surface('kerb cap',[a,b,(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],'kerb',180)
 verticals.append((a,b))
def station(y):
 points=D['stations_y_centre_halfwidth_left_right']
 for a,b in zip(points,points[1:]):
  if y<=b[0]:
   t=max(0,(y-a[0])/(b[0]-a[0]))
   return [a[i]+t*(b[i]-a[i]) for i in range(1,5)]
 return points[-1][1:]
def marking_point(y,side,offset):
 # Intersect the two parallel offset lines at a bend (miter join). Offsetting
 # only X made the perpendicular kerb setback vary on angled transitions.
 stations=D['stations_y_centre_halfwidth_left_right']
 normals=[]
 for a,b in zip(stations,stations[1:]):
  if a[0]-1e-7<=y<=b[0]+1e-7:
   dx=(b[1]+side*b[2])-(a[1]+side*a[2])
   dy=b[0]-a[0]
   length=math.hypot(dx,dy)
   normals.append((-side*dy/length,side*dx/length))
 nx=sum(n[0] for n in normals)
 ny=sum(n[1] for n in normals)
 den=nx*normals[0][0]+ny*normals[0][1]
 c,h,_,_=station(y)
 return (c+side*h+offset*nx/den,y+offset*ny/den)
marking_segments=[]
# Derive mouth breaks from the actual angled road strips. Hand-entered Y gaps
# previously missed the lower side of West Street and left paint across asphalt.
mouth_breaks={-1:[],1:[]}
for road in D['side_roads']:
 a,b=road['centre'],road['end']
 dx,dy=b[0]-a[0],b[1]-a[1]
 length=math.hypot(dx,dy)
 side=1 if dx>0 else -1
 hits=[]
 for lo,hi in zip(D['stations_y_centre_halfwidth_left_right'],D['stations_y_centre_halfwidth_left_right'][1:]):
  pa=(lo[1]+side*lo[2],lo[0])
  pb=(hi[1]+side*hi[2],hi[0])
  # Signed perpendicular distance to the side-road axis, in metres.
  da=((pa[0]-a[0])*(-dy)+(pa[1]-a[1])*dx)/length
  db=((pb[0]-a[0])*(-dy)+(pb[1]-a[1])*dx)/length
  for bound in [-road['width']/2,road['width']/2]:
   if abs(db-da)>1e-9:
    t=(bound-da)/(db-da)
    if 0<=t<=1:
        hits.append(pa[1]+t*(pb[1]-pa[1]))
 assert len(hits)==2,(road['name'],hits)
 mouth_breaks[side].append((min(hits),max(hits)))
(ROOT/'research/marking-mouths.json').write_text(json.dumps(mouth_breaks,indent=2))
# London Square now owns the complete road and both corners below Y41.
# Retain the tiny continuation of the preceding kerb cap above Y41.
# Clipping an offset only after extending it through the seam avoids wedges.
from southport3d.road import parallel
for side,key in [(-1,'west_kerb'),(1,'east_kerb')]:
 curve=J[key]
 for a,b in zip(curve,curve[1:]):
  if b[1]==41:kerb(a,b,-side)
 inner=parallel(curve,-side*.30);outer=parallel(curve,-side*.58)
 for i in range(len(curve)-1):
  if curve[i+1][1]<41:continue
  surface('junction red edge band',[inner[i],inner[i+1],outer[i+1],outer[i]],'brick',140)
ys=sorted(set([v for pairs in mouth_breaks.values() for pair in pairs for v in pair]+[r[0] for r in D['stations_y_centre_halfwidth_left_right']]+[45,118,125,145,156,97.7,104.5,106.1,113.3,161.8,169.1,177.1,186.4,190.5,195.7,245.7,246.8]))
for ya,yb in zip(ys,ys[1:]):
 ca,ha,la,ra=station(ya)
 cb,hb,lb,rb=station(yb)
 surface('Nevill asphalt',[(ca-ha,ya),(ca+ha,ya),(cb+hb,yb),(cb-hb,yb)],'asphalt',100,level(True))
 for side in [-1,1]:
  edgea=ca+side*ha
  edgeb=cb+side*hb
  outera=la if side<0 else ra
  outerb=lb if side<0 else rb
  surface('Nevill footway',[(outera,ya),(edgea,ya),(edgeb,yb),(outerb,yb)],'paving',10)
  midpoint=(ya+yb)/2
  breaks=list(mouth_breaks[side])
  # Crossings are open, with separately authored ramps rather than a kerb barrier.
  breaks += [(246.8,249.5),tuple(J['nevill_crossing_y'])]
  if any(a<midpoint<b for a,b in breaks):
      continue
  kerb((edgea,ya),(edgeb,yb),-side)
  # Red paviour band behind the kerb, observed on the lower street; breadth estimated.
  if ya>=48:surface('red edge band',[(edgea+side*.32,ya),(edgea+side*.77,ya),(edgeb+side*.77,yb),(edgeb+side*.32,yb)],'brick',140)
  bay=(side>0 and 125<=midpoint<=156) or (side<0 and 118<=midpoint<=145)
  if ya>=41 and not bay:
   for offset in [.18,.36]:
    pa,pb=marking_point(ya,side,offset),marking_point(yb,side,offset)
    marking_segments.append({'kerb':[(edgea,ya),(edgeb,yb)],'paint':[pa,pb],'offset':offset})
    strip('double yellow',pa,pb,.07,'yellow',300,level(True))
(ROOT/'research/marking-centrelines.json').write_text(json.dumps(marking_segments,indent=2))
# Nevill signal crossing: kerb-free buff landings and sparse worn studs.
ya,yb=J['nevill_crossing_y']
for side in [-1,1]:
 ca,ha,la,ra=station(ya);cb,hb,lb,rb=station(yb)
 ea,eb=ca+side*ha,cb+side*hb
 def landing(x,y,side=side):
  c,h,_,_=station(y);distance=(x-(c+side*h))*side
  return grade(y)-.12*max(0,min(1,1-distance/1.3))
 for aa,bb in zip(ys,ys[1:]):
  if aa<ya or bb>yb:continue
  ca,ha,_,_=station(aa);cb,hb,_,_=station(bb)
  ea,eb=ca+side*ha,cb+side*hb
  surface('Nevill crossing tactile',[(ea,aa),(eb,bb),(eb+side*1.3,bb),(ea+side*1.3,aa)],'junction-tactile',210,landing)
for y in [ya,yb]:
 c,h,_,_=station(y)
 for j in range(10):
  x=c-h+.25+(2*h-.5)*j/9
  quad('Nevill crossing stud',x-.045,y-.045,x+.045,y+.045,'white',300,level(True))
# Short branches establish junction bounds without modelling the full side streets.
for road in D['side_roads']:
 a=road['centre']
 b=road['end']
 w=road['width']
 strip(road['name']+' pavement mouth',a,b,w+4.0,'paving',15)
 strip(road['name']+' road mouth',a,b,w,'asphalt',120,level(True))
 # Stops/paint are not continued through the running Nevill carriageway.
 dx,dy=b[0]-a[0],b[1]-a[1]
 length=math.hypot(dx,dy)
 nx,ny=-dy/length,dx/length
 for side in [-1,1]:
  start=tuple(a[k]+(b[k]-a[k])*.56+side*w/2*(nx,ny)[k] for k in [0,1])
  end=tuple(b[k]+side*w/2*(nx,ny)[k] for k in [0,1])
  kerb(start,end,-side)
  # Continue the adjoining street owner's inward kerb offsets across this stub.
  if road['name'] in ['Stanley Street','Bath Street','Cable Street','West Street']:
   for inset in [.185,.365]:
    pa=tuple(start[k]-side*inset*(nx,ny)[k] for k in [0,1])
    pb=tuple(end[k]-side*inset*(nx,ny)[k] for k in [0,1])
    strip(road['name']+' continuing double yellow',pa,pb,.07,'yellow',300,level(True))
# Running centre dashes, interrupted around staggered side-road mouths.
for y in range(51,241,6):
 if any(abs(y-j)<6 for j in [101.1,109.73,165.42,181.7,193.15]):
     continue
 a=station(y)
 b=station(y+2)
 strip('centre dash',(a[0],y),(b[0],y+2),.10,'white',300,level(True))
# Dated mid-street photograph shows a yellow bus bay and opposite parking.
# Exact bay endpoints are estimated; no text or current regulation is invented.
for side,ya,yb,colour,baywidth in [(1,125,156,'yellow',2.2),(-1,118,145,'white',1.9)]:
 for y in range(ya,yb,3):
  end=min(y+1.1,yb)
  a=station(y)
  b=station(end)
  strip('bay dash',(a[0]+side*(a[1]-baywidth),y),(b[0]+side*(b[1]-baywidth),end),.10,colour,300,level(True))
 for y in [ya,yb]:
  c,h,_,_=station(y)
  strip('bay end',(c+side*(h-.15),y),(c+side*(h-baywidth),y),.10,colour,300,level(True))
# Upper Nevill pedestrian areas follow mapped public-space polygons. These
# override the simpler width envelope only where the mapped shape extends it.
for wid in ['945177689','945177690']:
 poly=OSM['ways'][wid]['xy'][:-1]
 poly=halfplane(poly,(-100,185),(100,185),True)
 surface('mapped upper pedestrian apron',poly,'paving',12)
# Continue the Nevill throat into the bounded existing Promenade intersection.
upper=[[-22.02,248.07],[-14.02,248.07],[-17.15,271.9],[-28.2,268.5]]
surface('Nevill promenade throat',upper,'asphalt',130,level(True))
def south(x):
    return 263.73+.265*(x+21.2)-3.3
def north(x):
    return 270.98+.275*(x+22.68)+3.4
surface('Promenade carriageway',[(-48,south(-48)),(22,south(22)),(22,north(22)),(-48,north(-48))],'asphalt',135,level(True))
# Bounded landward footway and forecourt, stopping at the mapped Funland front.
surface('Promenade landward apron',[(-48,south(-48)-5),(-22,246.7),(12.9,260.2),(22,south(22)-5),(22,south(22)),(-48,south(-48))],'paving',14)
apron=[(-48,north(-48)),(22,north(22)),(11,307),(2.27,316.30),(-25.85,308.86),(-30.92,304.82),(-40.57,300.82),(-44.69,295.46)]
surface('Funland forecourt approach',apron,'paving',16)
# Long Promenade curb edges stop at the mapped pedestrian crossing and road mouth.
for a,b in [(-48,-29),(-16,-9),(0,22)]:
    kerb((a,south(a)),(b,south(b)),-1)
for a,b in [(-48,-15),(-10,22)]:
    kerb((a,north(a)),(b,north(b)),1)
# Ground-level crossing studs and lowered tactile landings. Exact pad dimensions
# are estimated; OSM identifies pelican crossings, lowered kerbs and tactile paving.
for y in [246.8,249.3]:
 for x in [-21.6+i*.75 for i in range(11)]:
     quad('Nevill crossing stud',x-.045,y-.045,x+.045,y+.045,'white',310,level(True))
for side in [-1,1]:
 inner=-18.02+side*4
 outer=inner+side*2
 def ramp(x,y,inner=inner,outer=outer):
     return grade(y)-.12+.12*max(0,min(1,(x-inner)/(outer-inner)))
 quad('Nevill dropped landing',min(inner,outer),246.8,max(inner,outer),249.3,'paving',200,ramp)
 ta=inner+side*.7
 tb=inner+side*1.5
 quad('Nevill tactile pad',min(ta,tb),247.1,max(ta,tb),249.0,'tactile',250,ramp)
# Two dotted edges follow the mapped crossing across the Promenade.
start=(-6.6,263.3)
end=(-12.0,278.4)
dx,dy=end[0]-start[0],end[1]-start[1]
dist=math.hypot(dx,dy)
nx,ny=-dy/dist,dx/dist
for side in [-1,1]:
 for i in range(3,int(dist/.8)-2):
  t=i*.8/dist
  x=start[0]+dx*t+side*1.25*nx
  y=start[1]+dy*t+side*1.25*ny
  if south(x)<y<north(x):
      quad('Promenade crossing stud',x-.05,y-.05,x+.05,y+.05,'white',310,level(True))
for point,other in [(start,end),(end,start)]:
 # Rectangle along the crossing axis, with footway at its outer edge and road
 # height at the toe; it cuts the estimated kerb line instead of hiding it.
 dx,dy=other[0]-point[0],other[1]-point[1]
 length=math.hypot(dx,dy)
 ux,uy=dx/length,dy/length
 vx,vy=-uy,ux
 corners=[(point[0]+u*ux+v*vx,point[1]+u*uy+v*vy) for u,v in [(-1,-1.25),(1,-1.25),(1,1.25),(-1,1.25)]]
 def ramp(x,y,p=point,ux=ux,uy=uy):
     return grade(y)-.12*max(0,min(1,((x-p[0])*ux+(y-p[1])*uy+1)/2))
 surface('Promenade dropped landing',corners,'tactile',260,ramp)
# Visible upper give-way line, with no invented words or live signal state.
for x in [-25+i*.8 for i in range(12)]:
    quad('upper give way dash',x,260.8,x+.35,260.9,'white',300,level(True))
# Block-plan surfaces observed in the aerial/3D review. Public realm owns these
# open spaces, independently of replaceable building placeholders.
for region in D.get('block_ground_areas',[]):
 surface(region['id'],region['polygon'],region['material'],8,
         (lambda x,y,z=region['height_m']:z) if 'height_m' in region else level(region['material']=='asphalt'))
# Tie the approximate old footway envelope to the nearest verified frontage.
# Only street-facing edges are eligible; rear/party edges do not gain paving.
footprints=[b['footprint'] for b in BLOCK_PLAN['blocks']]
def street_intersections(y):
 result=[]
 for poly in footprints:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if min(a[1],b[1])<=y<max(a[1],b[1]):
    t=(y-a[1])/(b[1]-a[1]);result.append(a[0]+t*(b[0]-a[0]))
 return result
for poly in footprints:
 for a,b in zip(poly,poly[1:]+poly[:1]):
  y=(a[1]+b[1])/2;x=(a[0]+b[0])/2
  if not 45<y<260 or abs(a[1]-b[1])<.1:continue
  centre=station(min(y,248.07))[0];side=1 if x>centre else -1
  ahead=[v for v in street_intersections(y) if (v-centre)*side>0]
  if not ahead or abs(x-(min(ahead) if side>0 else max(ahead)))>.01:continue
  surface('frontage tie-in',[a,b,(b[0]-side*2.1,b[1]),(a[0]-side*2.1,a[1])],'paving',5)
# Triangulated footprints clip every surface once, including the old broad
# apron. Footprints are ground outlines; do not trim to roof overhangs.
building_cutters=[]
for poly in footprints:
 v=[Vector((x,y,0)) for x,y in poly]
 for tri in tessellate_polygon([v]):
  building_cutters.append(ccw([poly[k] if isinstance(k,int) else (k.x,k.y) for k in tri]))

# Compile mutually exclusive horizontal surfaces. Paint cuts the road rather
# than hovering on nearly coplanar faces, preserving distant-view stability.
rows.sort(key=lambda row:row[3])
compiled={}
bounds=D['part_boundaries_y']
for index,(name,poly,mat,priority,zfun) in enumerate(rows):
 fragments=[ccw(poly)]
 if name=='double yellow':
  for road in D['side_roads']:
   a,b=road['centre'],road['end']
   dx,dy=b[0]-a[0],b[1]-a[1]
   length=math.hypot(dx,dy)
   nx,ny=-dy/length*road['width']/2,dx/length*road['width']/2
   cutter=ccw([(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)])
   fragments=[piece for fragment in fragments for piece in subtract(fragment,cutter)]
 for _,cutter,_,_,_ in rows[index+1:]:
  fragments=[piece for fragment in fragments for piece in subtract(fragment,ccw(cutter))]
  if not fragments:
      break
 for cutter in building_cutters:
  fragments=[piece for fragment in fragments for piece in subtract(fragment,cutter)]
  if not fragments:break
 for fragment in fragments:
  for part,ya,yb in zip(parts,bounds,bounds[1:]):
   p=halfplane(fragment,(-1000,ya),(1000,ya),True)
   p=halfplane(p,(1000,yb),(-1000,yb),True)
   if len(p)<3 or area(p)<1e-7:
       continue
   mesh=compiled.setdefault((part,mat),Mesh('Surface '+part+' '+mat))
   mesh.add([(x,y,zfun(x,y)) for x,y in p],[tuple(range(len(p)))])
for a,b in verticals:
 for part,ya,yb in zip(parts,bounds,bounds[1:]):
  low,high=sorted([a[1],b[1]])
  if high<=ya or low>=yb:
      continue
  # Segment clipping only in Y; no artificial vertical wall across a scene end.
  t0,t1=0,1
  if abs(b[1]-a[1])>1e-9:
   ts=sorted([(ya-a[1])/(b[1]-a[1]),(yb-a[1])/(b[1]-a[1])])
   t0=max(0,ts[0])
   t1=min(1,ts[1])
  if t1<=t0:
      continue
  aa=[a[i]+(b[i]-a[i])*t0 for i in [0,1]]
  bb=[a[i]+(b[i]-a[i])*t1 for i in [0,1]]
  mesh=compiled.setdefault((part,'vertical'),Mesh('Kerb '+part))
  mesh.add([(aa[0],aa[1],grade(aa[1])-.12),(bb[0],bb[1],grade(bb[1])-.12),(bb[0],bb[1],grade(bb[1])),(aa[0],aa[1],grade(aa[1]))],[(0,1,2,3)])
from southport3d.conform import conform
compiled,conform_report=conform(compiled)
(ROOT/'research/conform.json').write_text(json.dumps(conform_report,indent=2))
print('Conforming surface boundaries:',conform_report)
for (part,mat),mesh in compiled.items():
 ob=mesh.finish([mats['kerb' if mat=='vertical' else mat]],C[part])
 bm=bmesh.new()
 bm.from_mesh(ob.data)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bm.to_mesh(ob.data)
 bm.free()
 uv=ob.data.uv_layers.new(name='Metric paving repeat')
 for f in ob.data.polygons:
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   uv.data[li].uv=(v.x/3.6,v.y/3.6)
 ob['placement_status']='OSM registered, widths and heights estimated from linked imagery'
for im in bpy.data.images:
 if im.source=='FILE':
     im.pack()
s.render.engine='CYCLES'
s.cycles.samples=32
s.cycles.use_denoising=True
s.world.use_nodes=True
s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.70,.75,1)
s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN')
sun.energy=2.5
ob=bpy.data.objects.new('Sun',sun)
s.collection.objects.link(ob)
ob.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
s.collection.objects.link(cam)
s.camera=cam
cam.data.type='ORTHO'
s.render.resolution_x=1500
s.render.resolution_y=1100
s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
