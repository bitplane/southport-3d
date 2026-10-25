"""Eastbank canvas with bounded road profiles and separate bridge/rail levels."""
import bpy,bmesh,ctypes as C,json,math,os,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from plan_geometry import Plan
from datum import grade,SURFACES,PAVEMENT
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
def rect(a,b,c,d):return [(a,c),(b,c),(b,d),(a,d)]
P=Plan();fn=P.lib.GEOSBuffer_r;fn.restype=C.c_void_p;fn.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
def buffer(g,d):return P.own(fn(P.context,g,d,5))
def line(points,width):
 g=P.own(P.read(P.context,P.reader,('LINESTRING ('+','.join(f'{x} {y}'for x,y in points)+')').encode()))
 return buffer(g,width/2)
def union(gs):return P.polygons([t for g in gs for t in P.triangles(g)])
roads=union([line(r['points'],r['width']) for r in D['roads']])
blocks=[b for f in [D['block_plan'],*D['existing_block_plans']]for b in json.loads((REPO/f).read_text())['blocks']]
station=json.loads((REPO/'regions/southport/station-quarter/public-realm/research/layout.json').read_text())
cutters=[b['footprint']for b in blocks]+station['ground_polygons']
available=P.difference(P.polygons(D['study_polygons']),P.polygons(cutters))
# The rail corridor continues beneath the deck. Outside deck width it is a real
# opening in the higher approach ground, not a second full overlapping floor.
rail_points=[[-390,-605.4],[-334,-602.1],[-280,-598.8]]
rail_area=line(rail_points,12)
deck_points=[[-337.3,-617],[-332.7,-590]]
deck_outline=parallel(deck_points,-5.5)+list(reversed(parallel(deck_points,5.5)))
deck_area=P.polygons([deck_outline])
# The station block now traces the full curved railway reservation. Preserve
# that opening at the shared boundary; only the bridge deck crosses above it.
rail_plan=REPO/'regions/southport/tulketh-railway/public-realm/research/layout.json'
rail_opening=P.polygons(json.loads(rail_plan.read_text())['rail_reservation'])
available=P.difference(available,P.difference(union([rail_area,rail_opening]),deck_area))
road=P.intersection(available,roads)
foot=P.difference(P.intersection(available,buffer(roads,D['footway_width_m'])),road)
remaining=P.difference(P.difference(available,road),foot)
# Roundabout island and splitter islands stay raised; exact planting deferred.
island=P.polygons([[( -343.7+8.1*math.cos(i*math.tau/32),-710.9+8.1*math.sin(i*math.tau/32))for i in range(32)]])
green=P.intersection(remaining,island);courts=P.difference(remaining,green)
yellow_full=union([P.difference(buffer(roads,-a),buffer(roads,-b))for a,b in [(.15,.22),(.33,.40)]])
paint_mask=P.polygons([rect(-355,-310,-675,-570)])
yellow=P.intersection(P.intersection(yellow_full,paint_mask),road)
# Conservative observed bridge-centre dashes, kept away from roundabout/junctions.
def centre(y):return -334.45+(y+602)*.19
white_full=union([line([(centre(y),y),(centre(y+3),y+3)],.10) for y in range(-666,-568,9)])
white=P.intersection(P.difference(white_full,yellow),road)
asphalt=P.difference(P.difference(road,yellow),white)
colours={'asphalt':(.09,.095,.10),'paving':(.48,.45,.40),'courts':(.34,.33,.31),'green':(.16,.24,.10),'yellow':(.8,.62,.13),'white':(.8,.8,.76),'kerb':(.42,.42,.39),'structure':(.36,.34,.30),'rail':(.22,.22,.21),'steel':(.17,.19,.20)}
mats={}
for name,col in colours.items():
 m=bpy.data.materials.new('Eastbank '+name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.9;mats[name]=m
collections={}
for i in range(6):
 name=f'section-{i}-ground';c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
for name in ['rail-ground','bridge-structure']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
compiled={}
for i,(lo,hi) in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 name=f'section-{i}-ground';cell=P.polygons([rect(-440,-170,lo,hi)])
 for mat,g in [('asphalt',asphalt),('paving',foot),('courts',courts),('green',green),('yellow',yellow),('white',white)]:
  m=Mesh('Ground '+name+' '+mat)
  for tri in P.triangles(P.intersection(g,cell)):
   # Every change of grade becomes a shared edge before planar conformance.
   for lifted in PAVEMENT.lift_triangle(tri):m.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
  if m.faces:compiled[(name,mat)]=m
import southport3d.conform as cf
cf.GRID=1/8192;cf.TOLERANCE=1e-6
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled)
road_mats={'asphalt','yellow','white'};edges=defaultdict(list)
for (name,mat),m in compiled.items():
 for face in m.faces:
  for ia,ib in zip(face,face[1:]+face[:1]):
   a,b=m.vertices[ia],m.vertices[ib];key=tuple(sorted((tuple(round(v,4)for v in a[:2]),tuple(round(v,4)for v in b[:2]))));edges[key].append((name,mat,a,b))
curbs={}
def on_station_boundary(point):
 for polygon in station['ground_polygons']:
  for a,b in zip(polygon,polygon[1:]+polygon[:1]):
   dx,dy=b[0]-a[0],b[1]-a[1];l2=dx*dx+dy*dy
   if not l2:continue
   t=max(0,min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/l2))
   if math.hypot(point[0]-a[0]-t*dx,point[1]-a[1]-t*dy)<.0003:return True
 return False
for hits in edges.values():
 if not any(h[1]in road_mats for h in hits):continue
 road_hit=next(h for h in hits if h[1]in road_mats)
 midpoint=[(road_hit[2][i]+road_hit[3][i])/2 for i in range(2)]
 if not any(h[1]not in road_mats for h in hits) and not (len(hits)==1 and on_station_boundary(midpoint)):continue
 name,_,a,b=road_hit;m=curbs.setdefault((name,'kerb'),Mesh('Ground '+name+' kerb'));za,zb=grade(*a[:2]),grade(*b[:2]);m.add([(a[0],a[1],za-.12),(b[0],b[1],zb-.12),(b[0],b[1],zb),(a[0],a[1],za)],[(3,2,1,0)])
for (name,mat),m in compiled.items():m.vertices=[(x,y,grade(x,y)-(.12 if mat in road_mats else 0))for x,y,z in m.vertices]
compiled.update(curbs)
def finish(m,mat,collection):
 ob=m.finish([mats[mat]],collections[collection]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.new(name='Metric ground');
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 return ob
for (name,mat),m in compiled.items():finish(m,mat,name)
# Close the exposed cutting boundaries down to the independent rail datum.
# The deck opening itself stays clear; only ground edges beside the reservation
# receive a retaining envelope. Fine masonry and real bank slopes are deferred.
contains=P.lib.GEOSCovers_r;contains.restype=C.c_char;contains.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p]
opening=P.difference(union([rail_area,rail_opening]),buffer(deck_area,.01))
banks=Mesh('Structure railway retaining envelope')
for hits in edges.values():
 if len(hits)!=1:continue
 name,mat,a,b=hits[0];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<.001:continue
 x=(a[0]+b[0])/2+dy/length*.003;y=(a[1]+b[1])/2-dx/length*.003
 point=P.own(P.read(P.context,P.reader,f'POINT ({x} {y})'.encode()))
 if contains(P.context,opening,point)!=b'\x01':continue
 za=grade(*a[:2])-(.12 if mat in road_mats else 0);zb=grade(*b[:2])-(.12 if mat in road_mats else 0)
 banks.add([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],zb),(a[0],a[1],za)],[(0,1,2,3)])
finish(banks,'structure','bridge-structure')
rail=SURFACES.surface('eastbank-rail-cutting');m=Mesh('Ground railway cutting')
for tri in P.triangles(P.intersection(rail_area,P.polygons([rect(-385,-285,-620,-580)]))):
 for lifted in rail.lift_triangle(tri):m.add(lifted,[(0,1,2)])
finish(m,'rail','rail-ground')
# Structurally bounded slab underside and sides; visible top belongs solely to
# the road/pavement meshes. No full box top coplanar with the road surface.
m=Mesh('Structure bridge slab')
for tri in P.triangles(deck_area):
 for t in PAVEMENT.lift_triangle(tri):m.add([(x,y,z-.8)for x,y,z in t],[(2,1,0)])
for a,b in zip(deck_outline,deck_outline[1:]+deck_outline[:1]):
 points=list(PAVEMENT.edge_points(a,b))
 for a,b in zip(points,points[1:]):m.add([(a[0],a[1],a[2]-.8),(b[0],b[1],b[2]-.8),(b[0],b[1],b[2]-.15),(a[0],a[1],a[2]-.15)],[(0,1,2,3)])
finish(m,'structure','bridge-structure')
# Plain panel parapet envelope follows the observed side walls. Mosaic imagery
# is not copied; fine panels deferred to a later structural detail pass.
for side in [-1,1]:
 m=Mesh('Structure bridge parapet '+str(side));edge=parallel(deck_points,side*5.34)
 outline=parallel(edge,-.16)+list(reversed(parallel(edge,.16)))
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline,outline[1:]+outline[:1]))<0:outline.reverse()
 for tri in P.triangles(P.polygons([outline])):
  for lifted in PAVEMENT.lift_triangle(tri):
   m.add(lifted,[(2,1,0)]);m.add([(x,y,z+1.15)for x,y,z in lifted],[(0,1,2)])
 for a,b in zip(outline,outline[1:]+outline[:1]):
  points=list(PAVEMENT.edge_points(a,b))
  for a,b in zip(points,points[1:]):m.add([a,b,(b[0],b[1],b[2]+1.15),(a[0],a[1],a[2]+1.15)],[(0,1,2,3)])
 finish(m,'structure','bridge-structure')
P.close();(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
