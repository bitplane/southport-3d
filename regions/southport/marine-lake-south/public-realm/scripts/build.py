"""Separate southlake ownership canvas, with formal lido and soft park bank."""
import bpy,bmesh,ctypes as C,json,math,os,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from plan_geometry import Plan
from datum import SURFACES,PAVEMENT,BRIDGE
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
P=Plan();fn=P.lib.GEOSBuffer_r;fn.restype=C.c_void_p;fn.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
def buffer(g,d):return P.own(fn(P.context,g,d,3))
_diff=P.diff;_inter=P.inter;_unary=P.unary
P.diff=lambda ctx,a,b,grid:_diff(ctx,a,b,1/8192)
P.inter=lambda ctx,a,b,grid:_inter(ctx,a,b,1/8192)
P.unary=lambda ctx,a,grid:_unary(ctx,a,1/8192)
_intersection=P.intersection;_difference=P.difference
P.intersection=lambda a,b:buffer(_intersection(a,b),0)
P.difference=lambda a,b:buffer(_difference(a,b),0)
def line(points,width):
 g=P.own(P.read(P.context,P.reader,('LINESTRING ('+','.join(f'{x} {y}'for x,y in points)+')').encode()));return buffer(g,width/2)
def union(gs):return P.polygons([t for g in gs for t in P.triangles(g)])
def rect(a,b,c,d):return [(a,c),(b,c),(b,d),(a,d)]
def neighbour_geometry():
 data=json.loads((ROOT/'research/neighbour-ownership.json').read_text());polys=[]
 for record in data['polygons']:
  rings=[]
  for points in [record['outer'],*record['holes']]:rings.append('('+','.join(f'{x} {y}'for x,y in points+[points[0]])+')')
  polys.append('POLYGON ('+','.join(rings)+')')
 return P.own(P.read(P.context,P.reader,('GEOMETRYCOLLECTION ('+','.join(polys)+')').encode()))
study=P.difference(P.difference(P.polygons(D['study_polygons']),P.polygons(D['old_marine_study'])),neighbour_geometry())
lake_outer=P.polygons([D['lake_outline']]);islands=P.polygons(D['lake_islands']);lake=P.difference(lake_outer,islands)
blocks=[b for f in [D['block_plan'],*D['existing_block_plans']]for b in json.loads((REPO/f).read_text())['blocks']if not b.get('base_clearance_m')]
land=P.difference(P.difference(study,lake),P.polygons([b['footprint']for b in blocks]))
# Keep the deck continuous across the islands; only its dry-shore approaches
# replace underlying paving. Island ground remains a separate layer below it.
bridge=P.intersection(study,line(D['venetian_axis'],D['venetian_width_m']))
land=P.difference(land,P.difference(bridge,lake_outer))
# Preserve the registered incoming WestStreet tangent and width at X−172.
road_geometries=[];foot_geometries=[]
for r in D['roads']:
 g=line(r['points'],r['width']);road_geometries.append(g);foot_geometries.append(buffer(g,r['footway']))
west=json.loads((REPO/'regions/southport/west-street/public-realm/research/layout.json').read_text())['roads'][0]
west_patch=P.polygons([rect(-205,-171,130,160)])
raw_west=union([line(r['points'],r['width']+6)for r in D['roads']if r['name']=='West Street'])
road_full=union(road_geometries);foot_full=union(foot_geometries)
# Shared road centre shifts from OSM roofparallax to the previously researched axis.
new_west=[[-210,136.5],[-180,140.208],[-157.32,144.581]]
road_full=P.difference(road_full,P.intersection(west_patch,raw_west));road_full=union([road_full,P.intersection(west_patch,line(new_west,5.8))])
foot_full=P.difference(foot_full,P.intersection(west_patch,raw_west));foot_full=union([foot_full,P.intersection(west_patch,line(new_west,9.8))])
road=P.intersection(land,road_full)
parking=P.difference(P.intersection(land,P.polygons(D['parking_polygons'])),road)
paths=union([line(r['points'],r['width'])for r in D['paths']if not r['bridge']])
# Formal path bands follow the actual boundary. The other lake bank stays soft.
shore=line(D['formal_shoreline'],2*D['lido_width_m']);lido=P.intersection(land,P.difference(shore,lake_outer))
upper=P.intersection(land,P.difference(buffer(shore,D['upper_walk_width_m']),shore))
foot=P.difference(P.difference(P.intersection(land,union([foot_full,paths,lido,upper])),road),parking)
remaining=P.difference(P.difference(P.difference(land,road),parking),foot)
green=P.intersection(remaining,P.polygons(D['green_polygons']));sand=P.intersection(P.difference(remaining,green),P.polygons([D['sand_reservation']]));courts=P.difference(P.difference(remaining,green),sand)
# Paint is cut into its carriageway, never laid above a duplicate asphalt face.
major=union([line(r['points'],r['width']+.1)for r in D['roads']if r['name']in ['The Promenade','Marine Drive','West Street','Esplanade','Coronation Walk']])
yellow_full=union([P.difference(buffer(road_full,-a),buffer(road_full,-b))for a,b in [(.15,.22),(.33,.40)]])
yellow=P.intersection(P.intersection(yellow_full,major),road)
white_rows=[]
for r in D['roads']:
 if r['name']not in ['The Promenade','Marine Drive','Esplanade']or r['width']<6:continue
 for a,b in zip(r['points'],r['points'][1:]):
  length=math.dist(a,b)
  for t in np.arange(3,length-3,12):
   aa=[a[i]+(b[i]-a[i])*t/length for i in [0,1]];bb=[a[i]+(b[i]-a[i])*min(t+3,length)/length for i in [0,1]]
   white_rows.append(P.polygons([parallel([aa,bb],-.05)+list(reversed(parallel([aa,bb],.05)))]))
white=P.intersection(P.difference(union(white_rows),yellow),road)
asphalt=P.difference(P.difference(road,yellow),white)
# The old regional plateau and hand-built access planes are superseded by
# measured terrain. Distinct bridge/water layers remain explicit below.
regions=[]
colours={'asphalt':(.085,.09,.095),'paving':(.54,.52,.47),'courts':(.35,.34,.31),'green':(.19,.27,.12),'parking':(.18,.19,.19),'yellow':(.8,.62,.13),'white':(.8,.8,.76),'kerb':(.43,.43,.4),'structure':(.35,.36,.34),'sand':(.54,.48,.36),'water':(.08,.23,.29)}
mats={}
for name,col in colours.items():
 m=bpy.data.materials.new('Southlake '+name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.9;mats[name]=m
collections={}
for name in [*[f'cell-{i:02d}-ground'for i in range(24)],'venetian-ground','lake-water','shore-walls']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
compiled={};surfaces={};road_mats={'asphalt','yellow','white','parking'}
for ix,(lo,hi)in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 for iy,(bottom,top)in enumerate(zip(D['row_cuts'],D['row_cuts'][1:])):
  name=f'cell-{ix*4+iy:02d}-ground';cell=P.polygons([rect(lo,hi,bottom,top)])
  for mat,g in [('asphalt',asphalt),('paving',foot),('courts',courts),('green',green),('sand',sand),('parking',parking),('yellow',yellow),('white',white)]:
   rest=P.intersection(g,cell)
   active_regions=[]
   for region,zone,surface in [*active_regions,('main',None,PAVEMENT)]:
    part=P.intersection(rest,zone)if zone else rest
    if zone:rest=P.difference(rest,zone)
    m=Mesh('Ground '+name+' '+region+' '+mat)
    for tri in P.triangles(part):
     for lifted in surface.lift_triangle(tri):m.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
    if m.faces:compiled[(name,region,mat)]=m;surfaces[(name,region,mat)]=surface
# The Venetian bridge is a separate walkable surface above nonwalkable water.
bridge_mesh=Mesh('Ground Venetian bridge top')
for tri in P.triangles(bridge):
 for lifted in BRIDGE.lift_triangle(tri):bridge_mesh.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
if bridge_mesh.faces:compiled[('venetian-ground','bridge','paving')]=bridge_mesh;surfaces[('venetian-ground','bridge','paving')]=BRIDGE
import southport3d.conform as cf
cf.GRID=1/8192;cf.TOLERANCE=.00019
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled,preserve_triangles=True,weld_distance=5e-5)
def h(key,p):return surfaces[key].height(*p[:2])-(.12 if key[2]in road_mats else 0)
edges=defaultdict(list)
for key,m in compiled.items():
 for face in m.faces:
  for ia,ib in zip(face,face[1:]+face[:1]):
   a,b=m.vertices[ia],m.vertices[ib];e=tuple(sorted((tuple(round(v,4)for v in a[:2]),tuple(round(v,4)for v in b[:2]))));edges[e].append((key,a,b))
verticals={}
for hits in edges.values():
 if len(hits)!=2:continue
 (ka,a,b),(kb,_,_)=hits
 # The elevated deck owns its shallow fascia. Do not fill its open underside
 # with a terrain retaining wall or duplicate the fascia at shore approaches.
 if 'bridge'in (ka[1],kb[1]):continue
 za,zb=h(ka,a),h(ka,b);zc,zd=h(kb,a),h(kb,b)
 if max(abs(za-zc),abs(zb-zd))<1e-5:continue
 # One owner for every material/profile boundary face, including lido and
 # raised Esplanade walls; no closed surface is repeated under a wall.
 name,region,_=ka;mat='kerb'if max(abs(za-zc),abs(zb-zd))<.13 else 'structure';target=name if mat=='kerb'else'shore-walls'
 m=verticals.setdefault((target,mat),Mesh(('Ground 'if mat=='kerb'else'Structure ')+target+' boundary '+mat))
 m.add([(a[0],a[1],za),(b[0],b[1],zb),(b[0],b[1],zd),(a[0],a[1],zc)],[(0,1,2,3)])
for key,m in compiled.items():m.vertices=[(x,y,h(key,(x,y)))for x,y,z in m.vertices]
def finish(m,mat,collection):
 ob=m.finish([mats[mat]],collections[collection]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 # Terrain triangles share vertices and smooth normals. Flat per-face normals
 # made the exporter duplicate nearly every corner, tripling transfer size.
 # Keep vertical kerbs/retaining faces in their separate hard-edged objects.
 if m.name.startswith('Ground ')and 'boundary'not in m.name:
  for face in ob.data.polygons:face.use_smooth=True
 uv=ob.data.uv_layers.new(name='Metric surface')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 return ob
for(name,region,mat),m in compiled.items():finish(m,mat,name)
for(target,mat),m in verticals.items():finish(m,mat,target)
water=SURFACES.surface('south-water');m=Mesh('Structure southlake water')
for tri in P.triangles(P.intersection(study,lake)):
 for lifted in water.lift_triangle(tri):m.add(lifted,[(0,1,2)])
finish(m,'water','lake-water')
# Waterline facade is unique: the lido owns its top and this strip its exposed
# vertical edge. No fabricated cap is laid over the walkable paving.
lido_surface=PAVEMENT;m=Mesh('Structure formal water edge')
def clipped_segments(a,b):
 raw=P.own(P.read(P.context,P.reader,('LINESTRING ('+','.join(f'{x} {y}'for x,y in [a,b])+')').encode()))
 g=_intersection(raw,study);out=[]
 def visit(o):
  if P.kind(P.context,o)==1:
   seq=P.seq(P.context,o);n=C.c_uint();P.size(P.context,seq,C.byref(n));points=[]
   for i in range(n.value):
    x,y=C.c_double(),C.c_double();P.x(P.context,seq,i,C.byref(x));P.y(P.context,seq,i,C.byref(y));points.append((x.value,y.value))
   out.extend(zip(points,points[1:]))
  else:
   for i in range(P.count(P.context,o)):visit(P.child(P.context,o,i))
 visit(g);return out
for a,b in zip(D['formal_shoreline'],D['formal_shoreline'][1:]):
 for start,end in clipped_segments(a,b):
  points=list(lido_surface.edge_points(start,end))
  for aa,bb in zip(points,points[1:]):m.add([(aa[0],aa[1],water.height(*aa[:2])),(bb[0],bb[1],water.height(*bb[:2])),bb,aa],[(0,1,2,3)])
finish(m,'structure','shore-walls')
# Footbridge underside and edge faces, top remains the separate support part.
m=Mesh('Structure Venetian underside')
for tri in P.triangles(bridge):
 for lifted in BRIDGE.lift_triangle(tri):m.add([(x,y,z-.3)for x,y,z in lifted],[(2,1,0)])
for side in [-1,1]:
 edge=parallel(D['venetian_axis'],side*D['venetian_width_m']/2)
 for a,b in zip(edge,edge[1:]):
  points=list(BRIDGE.edge_points(a,b))
  for aa,bb in zip(points,points[1:]):m.add([(aa[0],aa[1],aa[2]-.3),(bb[0],bb[1],bb[2]-.3),bb,aa],[(0,1,2,3)]if side>0 else[(3,2,1,0)])
finish(m,'structure','shore-walls')
# Low rails preserve bridge outline; ornamental balustrade details deferred.
for side in [-1,1]:
 edge=parallel(D['venetian_axis'],side*(D['venetian_width_m']/2-.05))
 outline=parallel(edge,-.05)+list(reversed(parallel(edge,.05)))
 m=Mesh('Structure Venetian rail envelope '+str(side))
 for tri in P.triangles(P.polygons([outline])):
  for lifted in BRIDGE.lift_triangle(tri):m.add([(x,y,z+1.1)for x,y,z in lifted],[(0,1,2)])
 for a,b in zip(outline,outline[1:]+outline[:1]):
  points=list(BRIDGE.edge_points(a,b))
  for aa,bb in zip(points,points[1:]):m.add([aa,bb,(bb[0],bb[1],bb[2]+1.1),(aa[0],aa[1],aa[2]+1.1)],[(0,1,2,3)])
 finish(m,'structure','shore-walls')
# Continuous coarse sea-wall strip; its shared end exactly matches the prior
# north segment. Caps are unique and vertical faces stand on mainland grade.
edge=D['coast_wall_centres'];outline=parallel(edge,-.16)+list(reversed(parallel(edge,.16)))
wall=P.polygons([outline])
# Terminal interface is mitred to the existing strip at its original start.
m=Mesh('Structure coastal sea wall envelope')
for tri in P.triangles(wall):
 for lifted in PAVEMENT.lift_triangle(tri):m.add([(x,y,z+.8)for x,y,z in lifted],[(0,1,2)])
# Boundary extraction avoids internal fragment caps.
def rings(g):
 out=[]
 def visit(o):
  if P.kind(P.context,o)==3:
   seq=P.seq(P.context,P.exterior(P.context,o));n=C.c_uint();P.size(P.context,seq,C.byref(n));points=[]
   for i in range(n.value-1):
    x,y=C.c_double(),C.c_double();P.x(P.context,seq,i,C.byref(x));P.y(P.context,seq,i,C.byref(y));points.append((x.value,y.value))
   out.append(points)
  else:
   for i in range(P.count(P.context,o)):visit(P.child(P.context,o,i))
 visit(g);return out
for outline in rings(wall):
 for a,b in zip(outline,outline[1:]+outline[:1]):
  points=list(PAVEMENT.edge_points(a,b))
  for aa,bb in zip(points,points[1:]):m.add([aa,bb,(bb[0],bb[1],bb[2]+.8),(aa[0],aa[1],aa[2]+.8)],[(0,1,2,3)])
finish(m,'structure','shore-walls')
P.close();(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
