"""Bounded north-lake canvas. Polygon ownership precedes height evaluation."""
import bpy,bmesh,ctypes as C,json,math,os,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from plan_geometry import Plan
from datum import grade,SURFACES,PAVEMENT,BRIDGE,LOWER
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
def rect(a,b,c,d):return [(a,c),(b,c),(b,d),(a,d)]
P=Plan();fn=P.lib.GEOSBuffer_r;fn.restype=C.c_void_p;fn.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
def buffer(g,d):return P.own(fn(P.context,g,d,3))
# Every ownership overlay uses one binary metric grid before triangulation.
# It is exactly representable in float32 throughout this bounded site.
_diff=P.diff;_inter=P.inter;_unary=P.unary
P.diff=lambda ctx,a,b,grid:_diff(ctx,a,b,1/8192)
P.inter=lambda ctx,a,b,grid:_inter(ctx,a,b,1/8192)
P.unary=lambda ctx,a,grid:_unary(ctx,a,1/8192)
# Touching shoreline/parking boundaries may return lines; retain area ownership only.
_intersection=P.intersection;_difference=P.difference
P.intersection=lambda a,b:buffer(_intersection(a,b),0)
P.difference=lambda a,b:buffer(_difference(a,b),0)
def line(points,width):
 g=P.own(P.read(P.context,P.reader,('LINESTRING ('+','.join(f'{x} {y}'for x,y in points)+')').encode()));return buffer(g,width/2)
def union(gs):return P.polygons([t for g in gs for t in P.triangles(g)])
study=P.difference(P.polygons(D['study_polygons']),P.polygons(D['neighbour_exclusions']));lake_outer=P.polygons([D['lake_outline']]);islands=P.polygons(D['lake_islands']);lake=P.difference(lake_outer,islands)
blocks=[b for f in [D['block_plan'],*D['existing_block_plans']]for b in json.loads((REPO/f).read_text())['blocks']]
# Bridge deck is an explicit land layer above water, with no full terrain floor.
bridge_axis=[[29.8,310],*D['bridge_axis'],[-46.86,540]]
# Researched deck top ends at the rail line; outboard sloping fascia is owned
# by the independent bridge structure asset. Western anchor terraces flare.
sys.path.insert(0,str(REPO/'regions/southport/marine-drive/marine-way-bridge/scripts'))
from bridge_alignment import xy as bridge_xy,width as bridge_width,stations as bridge_stations
bridge_st=[0.,23.8,103.8,122.,128.,134.,139.,143.,147.,150.]
bridge_outline=[bridge_xy(t,-bridge_width(t))for t in bridge_st]+[bridge_xy(t,bridge_width(t))for t in reversed(bridge_st)]
bridge_deck=P.polygons([bridge_outline])
bridge_zone=union([bridge_deck,line([bridge_axis[0],bridge_xy(0,0)],14.2),line([bridge_xy(150,0),bridge_axis[-1]],14.2)])
land=P.difference(P.difference(study,lake),P.polygons([b['footprint']for b in blocks]))
available=union([land,P.intersection(study,bridge_zone)])
# Union complete road curves before carving pavement: rounded mouth returns are
# shared by road, kerb and all paint offsets. No kerb crosses an ownership cut.
road_full=union([line(r['points'],r['width'])for r in D['roads']])
# Preserve the exact existing two running-lane handover around the median.
road_full=P.difference(road_full,P.polygons([rect(85,110,275,330)]))
road_full=P.difference(road_full,P.polygons([rect(15,45,310,330)]))
road_full=union([road_full,P.polygons(D['seam_roads']+D['marine_seam_roads']),P.polygons([D['mini_roundabout']['road_outline']])])
# Keep the old approach/junction axes; replace carriageway ownership only inside
# the detailed bridge. Its observed narrow two-lane road is 6.4 m wide.
bridge_road=P.polygons([[bridge_xy(0,-3.2),bridge_xy(145,-3.2),bridge_xy(150,-3.7),bridge_xy(150,3.7),bridge_xy(145,3.2),bridge_xy(0,3.2)]])
road_full=union([P.difference(road_full,bridge_deck),bridge_road])
road=P.intersection(available,road_full)
parking=P.difference(P.intersection(available,P.polygons(D['parking_polygons'])),road)
# Seaward MarineDrive path only: inland side is asphalt parking, as in Jul2026.
coast=union([line(r['points'],r['width'])for r in D['roads']if r['name']=='Marine Drive'])
foot_full=buffer(P.difference(road_full,coast),D['footway_width_m'])
coast_path=union([P.polygons([*parallel(r['points'],r['width']/2),*reversed(parallel(r['points'],r['width']/2+3.1))])for r in D['roads']if r['name']=='Marine Drive'and r['points'][-1][0]>r['points'][0][0]])
paths=union([line(r['points'],r['width'])for r in D['paths']])
foot=P.difference(P.difference(P.intersection(available,union([foot_full,coast_path,paths,P.polygons(D['seam_paving'])])),road),parking)
foot=union([P.difference(foot,bridge_deck),P.difference(bridge_deck,road)])
# These material bands replace pavement triangles; none are floating overlays.
def bridge_strip(a,b):return P.polygons([[bridge_xy(0,a),bridge_xy(150,a),bridge_xy(150,b),bridge_xy(0,b)]])
cycle=union([bridge_strip(-4.65,-3.34),bridge_strip(3.34,4.65)])
separator=union([bridge_strip(-4.75,-4.65),bridge_strip(4.65,4.75)])
drain=union([bridge_strip(-3.34,-3.2),bridge_strip(3.2,3.34)])
cycle=P.intersection(cycle,foot);separator=P.intersection(separator,foot);drain=P.intersection(drain,foot)
foot_plain=P.difference(P.difference(P.difference(foot,cycle),separator),drain)
remaining=P.difference(P.difference(P.difference(available,road),foot),parking)
green=P.intersection(remaining,P.polygons(D['green_polygons']+D['lake_islands']))
# Northern dunes remain a broad planted reservation, rather than invented plots.
dunes=P.intersection(remaining,P.polygons([rect(100,1390,605,930)]))
green=union([green,dunes]);construction=P.intersection(P.difference(remaining,green),P.polygons(D['construction_polygons']));courts=P.difference(P.difference(remaining,green),construction)
# Double yellow follows full road boundary and is limited to evidenced main
# streets; the ownership clip never invents paint at a tile end.
marking_mask=union([line(r['points'],r['width']+1)for r in D['roads']if r['name']in ['Marine Drive','Marine Way Bridge']])
yellow_full=union([P.difference(buffer(road_full,-a),buffer(road_full,-b))for a,b in [(.15,.22),(.33,.40)]])
seam_lines=[]
for edge in D['seam_yellow_kerbs']:
 for offset in [.18,.36]:
  centre=parallel(edge,offset);seam_lines.append(P.polygons([parallel(centre,-.035)+list(reversed(parallel(centre,.035)))]))
yellow=P.intersection(union([P.intersection(yellow_full,marking_mask),*seam_lines]),road)
white_paths=[]
for r in D['roads']:
 if r['name']not in ['Marine Drive','Marine Way Bridge']or r['width']<6:continue
 for a,b in zip(r['points'],r['points'][1:]):
  length=math.dist(a,b)
  for t in np.arange(3,length-3,12):
   aa=[a[i]+(b[i]-a[i])*t/length for i in [0,1]];bb=[a[i]+(b[i]-a[i])*min(t+3,length)/length for i in [0,1]];white_paths.append(P.polygons([parallel([aa,bb],-.05)+list(reversed(parallel([aa,bb],.05)))]))
centre=D['mini_roundabout']['centre'];disc=P.polygons([[(centre[0]+1.25*math.cos(i*math.tau/24),centre[1]+1.25*math.sin(i*math.tau/24))for i in range(24)]])
white=P.intersection(P.difference(union([*white_paths,disc]),yellow),road)
asphalt=P.difference(P.difference(road,yellow),white)
colours={'asphalt':(.085,.09,.095),'paving':(.54,.52,.47),'courts':(.35,.34,.31),'green':(.19,.27,.12),'parking':(.18,.19,.19),'yellow':(.8,.62,.13),'white':(.8,.8,.76),'kerb':(.43,.43,.4),'structure':(.35,.36,.34),'construction':(.33,.26,.18),'water':(.08,.23,.29),'blue':(.08,.17,.24),'cycle':(.30,.33,.32),'separator':(.82,.81,.75),'drain':(.065,.07,.065)}
mats={}
for name,col in colours.items():
 m=bpy.data.materials.new('Marine '+name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.9;mats[name]=m
collections={}
for name in [*[f'section-{i}-ground'for i in range(8)],'lake-water','lower-promenade-ground','shore-walls']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
lower_zone=P.polygons([rect(-90,45,376.9,410)])
compiled={};surfaces={}
for i,(lo,hi)in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 name=f'section-{i}-ground';cell=P.polygons([rect(lo,hi,D['bounds'][2],930)])
 for mat,g in [('asphalt',asphalt),('paving',foot_plain),('cycle',cycle),('separator',separator),('drain',drain),('courts',courts),('construction',construction),('green',green),('parking',parking),('yellow',yellow),('white',white)]:
  g=P.intersection(g,cell)
  for region,surface in [('main',PAVEMENT),('bridge',BRIDGE),('lower',LOWER)]:
   part=P.intersection(g,bridge_zone)if region=='bridge'else P.difference(g,bridge_zone)
   if region=='main':part=P.difference(part,lower_zone)
   elif region=='lower':part=P.intersection(part,lower_zone)
   m=Mesh('Ground '+name+' '+region+' '+mat)
   for tri in P.triangles(part):
    for lifted in surface.lift_triangle(tri):m.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
   if m.faces:compiled[(name,region,mat)]=m;surfaces[(name,region,mat)]=surface
lower=P.intersection(P.intersection(land,bridge_deck),P.polygons([rect(-90,45,376.9,410)]))
m=Mesh('Ground lower-promenade-ground lower paving')
for tri in P.triangles(lower):
 for lifted in LOWER.lift_triangle(tri):m.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
if m.faces:
 compiled[('lower-promenade-ground','lower','paving')]=m;surfaces[('lower-promenade-ground','lower','paving')]=LOWER
import southport3d.conform as cf
cf.GRID=1/8192;cf.TOLERANCE=.00019
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled,preserve_triangles=True)
road_mats={'asphalt','yellow','white','parking'};edges=defaultdict(list)
for key,m in compiled.items():
 for face in m.faces:
  for ia,ib in zip(face,face[1:]+face[:1]):
   a,b=m.vertices[ia],m.vertices[ib];e=tuple(sorted((tuple(round(v,4)for v in a[:2]),tuple(round(v,4)for v in b[:2]))));edges[e].append((key,a,b))
curbs={}
for hits in edges.values():
 low=[h for h in hits if h[0][2]in road_mats];high=[h for h in hits if h[0][2]not in road_mats]
 if not(low and high):continue
 if low[0][0][1]!=high[0][0][1]:continue
 key,a,b=low[0];name,region,_=key;surface=surfaces[key];m=curbs.setdefault((name,region,'kerb'),Mesh('Ground '+name+' '+region+' kerb'));za,zb=surface.height(*a[:2]),surface.height(*b[:2]);m.add([(a[0],a[1],za-.12),(b[0],b[1],zb-.12),(b[0],b[1],zb),(a[0],a[1],za)],[(3,2,1,0)])
for key,m in compiled.items():m.vertices=[(x,y,surfaces[key].height(x,y)-(.12 if key[2]in road_mats else 0))for x,y,z in m.vertices]
compiled.update(curbs)
def finish(m,mat,collection):
 ob=m.finish([mats[mat]],collections[collection]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 if m.name.startswith('Ground ')and 'kerb'not in m.name:
  for face in ob.data.polygons:face.use_smooth=True
 uv=ob.data.uv_layers.new(name='Metric ground')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 return ob
print('Compiled topology', {mat:sum(len(m.faces) for (n,r,k),m in compiled.items()if k==mat)for mat in colours},flush=True)
for(name,region,mat),m in compiled.items():finish(m,mat,name)
m=Mesh('Structure lake water');water=SURFACES.surface('marine-lake')
# Water retains a separate non-walkable layer underneath the bridge.
for tri in P.triangles(P.intersection(study,lake)):
 for lifted in water.lift_triangle(tri):m.add(lifted,[(0,1,2)])
finish(m,'water','lake-water')
# All bridge structural surfaces now belong to marine-way-bridge.
def wall_strip(points,width,height,surface,name,mat,collection):
 outline=parallel(points,-width/2)+list(reversed(parallel(points,width/2)));m=Mesh('Structure '+name)
 for tri in P.triangles(P.polygons([outline])):
  for t in surface.lift_triangle(tri):m.add([(x,y,z+height)for x,y,z in t],[(0,1,2)])
 for a,b in zip(outline,outline[1:]+outline[:1]):
  q=list(surface.edge_points(a,b))
  for a,b in zip(q,q[1:]):m.add([a,b,(b[0],b[1],b[2]+height),(a[0],a[1],a[2]+height)],[(0,1,2,3)])
 finish(m,mat,collection)
# Metric low sea wall follows the outside of the observed seaward walking strip.
wall_strip(parallel(D['coast_wall_axis'],6.85),.32,.8,PAVEMENT,'continuous sea wall','structure','shore-walls')
P.close();(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
