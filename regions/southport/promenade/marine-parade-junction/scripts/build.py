"""Bounded Promenade and Marine Parade junction, with explicit ownership of every surface."""
import bpy,bmesh,os,sys,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'),str(ROOT/'scripts')]
from southport3d.geometry import Mesh
from planar import subtract,area,halfplane
D=json.loads((ROOT/'research/layout.json').read_text());OSM=json.loads((ROOT/'research/route-osm.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
parts=['junction-ground'];C={}
for part in parts:C[part]=bpy.data.collections.new(part);s.collection.children.link(C[part])
def material(name,colour,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=.85
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'-normal.png')));n.image.colorspace_settings.name='Non-Color';q=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(n.outputs['Color'],q.inputs['Color']);m.node_tree.links.new(q.outputs['Normal'],p.inputs['Normal'])
 return m
mats={'paving':material('Authored pale Promenade slabs',(.60,.58,.52),'paving'),'brick':material('Authored red brick bands',(.4,.22,.17),'brick'),'asphalt':material('Authored asphalt',(.08,.09,.09),'asphalt'),'kerb':material('Granite kerb',(.43,.43,.40)),'white':material('Worn white paint',(.72,.71,.65)),'yellow':material('Worn yellow paint',(.64,.48,.12)),'tactile':material('Estimated red tactile pads',(.57,.40,.25),'tactile')}
rows=[];verticals=[]
def grade(y):
 g=D['grade'];t=max(0,min(1,(y-g['start_y'])/(g['top_y']-g['start_y'])));return g['start_z']+t*(g['top_z']-g['start_z'])
def level(road=False):return lambda x,y:grade(y)-(.12 if road else 0)
def ccw(p):
 p=[tuple(v) for v in p]
 return p if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))>0 else list(reversed(p))
def surface(name,points,mat,priority=0,z=None):
 points=ccw(points)
 points=halfplane(points,(22,1000),(22,-1000),True)
 points=halfplane(points,(85,-1000),(85,1000),True)
 if len(points)<3 or area(points)<1e-7:return
 # Convex fragments make clipping independent of optional geometry packages.
 triangles=tessellate_polygon([[Vector((x,y,0)) for x,y in points]])
 for tri in triangles:rows.append((name,[points[v] if isinstance(v,int) else (v.x,v.y) for v in tri],mat,priority,z or level()))
def quad(name,x0,y0,x1,y1,mat,priority=0,z=None):surface(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],mat,priority,z)
def strip(name,a,b,width,mat,priority=0,z=None):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<1e-5:return
 nx,ny=-dy/length*width/2,dx/length*width/2
 surface(name,[(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],mat,priority,z)
def kerb(a,b,inside=1):
 # The cap is partitioned out of paving; only the vertical face is a second mesh.
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*.18*inside,dx/length*.18*inside
 surface('kerb cap',[a,b,(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],'kerb',180)
 verticals.append((a,b))
# Measured centreline anchors, estimated asphalt half widths. At X22 the
# two edges equal the Nevill tile exactly, then transition to the mapped lanes.
stations=[(22,271.878,286.667),(31.69,277.48,291.77),(51.79,282.72,296.69),(85,290.66,305.43)]
for a,b in zip(stations,stations[1:]):
 xa,sa,na=a;xb,sb,nb=b
 surface('Promenade asphalt',[(xa,sa),(xb,sb),(xb,nb),(xa,na)],'asphalt',100,level(True))
 surface('landward pavement',[(xa,sa-5),(xb,sb-5),(xb,sb),(xa,sa)],'paving',10)
 surface('seaward pavement',[(xa,na),(xb,nb),(xb,nb+9),(xa,na+9)],'paving',10)
 # Crossing at the mapped footway X≈56; open lowered landings below.
 for lo,hi in [(xa,min(xb,53)),(max(xa,60),xb)]:
  if hi<=lo:continue
  def edge(x,j):return a[j]+(b[j]-a[j])*(x-xa)/(xb-xa)
  kerb((lo,edge(lo,1)),(hi,edge(hi,1)),-1)
  if lo>=52:kerb((lo,edge(lo,2)),(hi,edge(hi,2)),1)
# Fan-shaped Marine Parade junction: mapped turning-arm centrelines constrain
# the outside outline; the exact radius and sidewalk widths remain estimates.
road=[(23.5,285.3),(27.86,287.2),(26.6,296),(22.5,310),(35.4,310),(39.4,301.8),(44.8,299.5),(53.5,296.4),(51.79,293.29),(36.66,289.88),(31.69,280.78)]
surface('Marine Parade broad pavement',[(22,286),(31,286),(42,290),(56,297),(52,307),(44,312),(40,310),(22,310)],'paving',12)
surface('Marine Parade junction asphalt',road,'asphalt',120,level(True))
# Kerb on the hotel-side turn and short Funland-side mouth. No closing kerb
# crosses the Y310 continuation boundary or the X22/X85 tile boundaries.
turning_kerbs=[]
for edge_index in [1,2,4,5,6]:
 a,b=map(tuple,road[edge_index:edge_index+2])
 # Clip the final turning kerb where it meets the running carriageway,
 # instead of extending its cap into the overlapping junction asphalt.
 def north_edge(x):
  for lo,hi in zip(stations,stations[1:]):
   if x<=hi[0]:return lo[2]+(hi[2]-lo[2])*(x-lo[0])/(hi[0]-lo[0])
  return stations[-1][2]
 da,db=a[1]-north_edge(a[0]),b[1]-north_edge(b[0])
 if da<0 and db<0:continue
 if da*db<0:
  t=da/(da-db);join=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
  if da<0:a=join
  else:b=join
 # Leave the mapped pedestrian path across Marine Parade open near Y302.
 if min(a[1],b[1])<304 and max(a[1],b[1])>300:continue
 kerb(a,b,1);turning_kerbs.append([a,b])
(ROOT/'research/turning-kerbs.json').write_text(json.dumps(turning_kerbs,indent=2))
# Ground view towards Marine Parade resolves the substantial central splitter,
# omitted by the first aerial-only interpretation. Keep its pedestrian cut-through.
marine_island=[(33.5,289.5),(37.1,293.2),(34.2,303),(31.2,310),(29.8,310),(32,301)]
surface('Marine Parade paved splitter',marine_island,'paving',180)
for a,b in zip(marine_island,marine_island[1:]+marine_island[:1]):
 if min(a[1],b[1])<304 and max(a[1],b[1])>300:continue
 if a[1]==310 and b[1]==310:continue
 verticals.append((a,b))
for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in marine_island]]):
 pts=[marine_island[i] if isinstance(i,int) else (i.x,i.y) for i in tri]
 pts=halfplane(pts,(-100,300.6),(100,300.6),True);pts=halfplane(pts,(100,303.6),(-100,303.6),True)
 surface('Marine splitter lowered crossing',pts,'tactile',260,level(True))
# The adjacent July 2026 panorama resolves a second, narrower splitter in the
# mouth. Its plan is estimated from the mapped lane split and image proportions.
slender=[(30,289),(31,289.2),(28.8,299),(27.8,298.8)]
surface('Marine narrow splitter',slender,'paving',180)
for a,b in zip(slender,slender[1:]+slender[:1]):verticals.append((a,b))
# Hotel-side yellow lines visibly turn into Marine Parade. Offset each polyline
# segment perpendicularly and use miter intersections at its sampled corners.
curve=[(35.4,310),(39.4,301.8),(44.8,299.5),(52.1,296.9)]
for offset in [.18,.36]:
 shifted=[]
 for i,p in enumerate(curve):
  ns=[]
  for j in [i-1,i]:
   if not 0<=j<len(curve)-1:continue
   a,b=curve[j:j+2];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);ns.append((dy/length,-dx/length))
  nx,ny=sum(n[0] for n in ns),sum(n[1] for n in ns);den=nx*ns[0][0]+ny*ns[0][1]
  shifted.append((p[0]+offset*nx/den,p[1]+offset*ny/den))
 for a,b in zip(shifted,shifted[1:]):strip('observed turning yellow line',a,b,.07,'yellow',300,level(True))
# July 2026 ground panorama resolves a continuous paved central refuge,
# interrupted by a red lowered crossing. Its width remains visually estimated.
def median_y(x):
 for a,b in zip(stations,stations[1:]):
  if x<=b[0]:
   t=(x-a[0])/(b[0]-a[0]);return (a[1]+a[2]+t*(b[1]+b[2]-a[1]-a[2]))/2
 return (stations[-1][1]+stations[-1][2])/2
for xa,xb in [(38,53.5),(59,85)]:
 pts=[(xa,median_y(xa)-.9),(xb,median_y(xb)-.9),(xb,median_y(xb)+.9),(xa,median_y(xa)+.9)]
 if xa==38:pts=[(xa,median_y(xa)),(xa+1.8,median_y(xa+1.8)-.9),*pts[1:3],(xa+1.8,median_y(xa+1.8)+.9)]
 surface('observed central paved refuge',pts,'paving',180)
 for a,b in zip(pts,pts[1:]+pts[:1]):
  if abs(a[0]-85)<1e-5 and abs(b[0]-85)<1e-5:continue
  verticals.append((a,b))
# Evinced hotel-side double yellow: perpendicular offsets, and an open gap at
# the crossing landing. Exact waiting restrictions remain outside this model.
for offset in [.18,.36]:
 a=(60,stations[2][2]+(60-stations[2][0])*(stations[3][2]-stations[2][2])/(85-stations[2][0]));b=(85,stations[3][2]);dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 shift=(dy/length*offset,-dx/length*offset)
 strip('observed yellow kerb line',(a[0]+shift[0],a[1]+shift[1]),(b[0]+shift[0],b[1]+shift[1]),.07,'yellow',300,level(True))
# Crossing studs follow mapped footway vectors. Painted studs are cut into the
# asphalt; the pale areas beyond the road are sloping tactile/footway landings.
def crossing(a,b,width):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length;vx,vy=-uy,ux
 for side in [-1,1]:
  for i in range(1,int(length/.8)):
   t=i*.8;x=a[0]+ux*t+side*width/2*vx;y=a[1]+uy*t+side*width/2*vy
   quad('crossing stud',x-.045,y-.045,x+.045,y+.045,'white',310,level(True))
 for p,sgn in [(a,1),(b,-1)]:
  pts=[(p[0]+u*ux+v*vx,p[1]+u*uy+v*vy) for u,v in [(-.8,-width/2),(.8,-width/2),(.8,width/2),(-.8,width/2)]]
  def ramp(x,y,p=p,sgn=sgn):return 2.2-.12*max(0,min(1,(((x-p[0])*ux+(y-p[1])*uy)*sgn+.8)/1.6))
  surface('estimated crossing landing',pts,'tactile',260,ramp)
crossing((58.3,284.6),(55.2,297.5),2.5)
# Red cut-through remains at road level between the raised refuge ends.
quad('red median cut-through',55.2,median_y(56.7)-1.0,58.2,median_y(56.7)+1.0,'tactile',260,level(True))
crossing((25.7,300.6),(38.9,303.5),2.5)
# Only clearly visible lane separation is represented. No guessed waiting
# restrictions, words, arrows, live signal state or legal traffic orders.
for x in range(63,84,6):
 y=290.5+(x-63)*.25;strip('lane separator',(x,y),(x+2,y+.5),.10,'white',300,level(True))
# Compile mutually exclusive horizontal surfaces. Paint cuts the road rather
# than hovering on nearly coplanar faces, preserving distant-view stability.
rows.sort(key=lambda row:row[3]);compiled={};bounds=D['part_boundaries_y']
for index,(name,poly,mat,priority,zfun) in enumerate(rows):
 fragments=[ccw(poly)]
 for _,cutter,_,_,_ in rows[index+1:]:
  fragments=[piece for fragment in fragments for piece in subtract(fragment,ccw(cutter))]
  if not fragments:break
 for fragment in fragments:
  for part,ya,yb in zip(parts,bounds,bounds[1:]):
   p=halfplane(fragment,(-1000,ya),(1000,ya),True);p=halfplane(p,(1000,yb),(-1000,yb),True)
   if len(p)<3 or area(p)<1e-7:continue
   mesh=compiled.setdefault((part,mat),Mesh('Surface '+part+' '+mat));mesh.add([(x,y,zfun(x,y)) for x,y in p],[tuple(range(len(p)))])
for a,b in verticals:
 for part,ya,yb in zip(parts,bounds,bounds[1:]):
  low,high=sorted([a[1],b[1]])
  if high<=ya or low>=yb:continue
  # Segment clipping only in Y; no artificial vertical wall across a scene end.
  t0,t1=0,1
  if abs(b[1]-a[1])>1e-9:
   ts=sorted([(ya-a[1])/(b[1]-a[1]),(yb-a[1])/(b[1]-a[1])]);t0=max(0,ts[0]);t1=min(1,ts[1])
  if t1<=t0:continue
  aa=[a[i]+(b[i]-a[i])*t0 for i in [0,1]];bb=[a[i]+(b[i]-a[i])*t1 for i in [0,1]]
  mesh=compiled.setdefault((part,'vertical'),Mesh('Kerb '+part))
  mesh.add([(aa[0],aa[1],grade(aa[1])-.12),(bb[0],bb[1],grade(bb[1])-.12),(bb[0],bb[1],grade(bb[1])),(aa[0],aa[1],grade(aa[1]))],[(0,1,2,3)])
from conform import conform
compiled,conform_report=conform(compiled)
(ROOT/'research/conform.json').write_text(json.dumps(conform_report,indent=2))
print('Conforming surface boundaries:',conform_report)
for (part,mat),mesh in compiled.items():
 ob=mesh.finish([mats['kerb' if mat=='vertical' else mat]],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.new(name='Metric paving repeat')
 for f in ob.data.polygons:
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/3.6,v.y/3.6)
 ob['placement_status']='OSM registered, widths and heights estimated from linked imagery'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
