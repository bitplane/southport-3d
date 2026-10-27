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
from venetian_ground import Transition,polygon,at,local,L,WIDTH,HALF_WIDTH,RAIL_OFFSET,PIERS,RAIL_START,RAIL_END,assert_frame,GREEN_SECTIONS,GREEN_STANDARDS,green_at
assert_frame(BRIDGE)
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
# The cafe's measured wall/drum footprint replaces its old OSM roof outline
# for ground clipping; its canopy and entrance apron remain open to the ground.
ground_blocks=[b['footprint'] for b in blocks if b.get('replace_with')!='southport.marine-lake-south.heritage-centre']
land=P.difference(P.difference(P.difference(study,lake),P.polygons(ground_blocks+[D['heritage_centre_ground_cutout']])), P.polygons(D['lake_islands'][:2]))
# The entry apron is open to the sky under the shallow cafe canopy; the
# source footprint includes that projection, so restore only this bounded area.
apron=P.intersection(study,P.polygons([D['heritage_centre_apron']]))
land=union([land,apron])
# Keep the deck continuous across the islands; only its dry-shore approaches
# replace underlying paving. Island ground remains a separate layer below it.
bridge=P.intersection(study,P.polygons([polygon(0,L,-HALF_WIDTH,HALF_WIDTH)]))
lower_underpass=P.polygons([polygon(146,157,-3,3)])
land=P.difference(land,P.difference(P.difference(bridge,lake_outer),lower_underpass))
landing_zone=P.polygons([polygon(-35,25,-20,20)]);lower_zone=P.polygons([polygon(138,164,-26,26)])
landing_surface=Transition(PAVEMENT,BRIDGE,'landing');lower_surface=Transition(PAVEMENT,BRIDGE,'lower')
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
paths=union([line(r['points'],r['width'])for r in D['paths']if not r['bridge']]+[apron])
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
colours={'asphalt':(.085,.09,.095),'paving':(.54,.52,.47),'courts':(.35,.34,.31),'green':(.19,.27,.12),'parking':(.18,.19,.19),'yellow':(.8,.62,.13),'white':(.8,.8,.76),'kerb':(.43,.43,.4),'structure':(.35,.36,.34),'sand':(.54,.48,.36),'water':(.08,.23,.29),'deck':(.48,.44,.38),'cream':(.78,.76,.64),'rock':(.34,.31,.25),'shrub':(.18,.29,.12),'globe':(.88,.87,.78),'socket':(.035,.045,.035),'gate-green':(.025,.19,.085)}
mats={}
for name,col in colours.items():
 m=bpy.data.materials.new('Southlake '+name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.9;mats[name]=m
tex=mats['deck'].node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/venetian-deck.png'));mats['deck'].node_tree.links.new(tex.outputs['Color'],mats['deck'].node_tree.nodes['Principled BSDF'].inputs['Base Color'])
collections={}
for name in [*[f'cell-{i:02d}-ground'for i in range(24)],'venetian-ground','venetian-lower-ground','venetian-structure','lake-water','shore-walls']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
compiled={};surfaces={};road_mats={'asphalt','yellow','white','parking'}
for ix,(lo,hi)in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 for iy,(bottom,top)in enumerate(zip(D['row_cuts'],D['row_cuts'][1:])):
  name=f'cell-{ix*4+iy:02d}-ground';cell=P.polygons([rect(lo,hi,bottom,top)])
  for mat,g in [('asphalt',asphalt),('paving',foot),('courts',courts),('green',green),('sand',sand),('parking',parking),('yellow',yellow),('white',white)]:
   rest=P.intersection(g,cell)
   active_regions=[('landing',landing_zone,landing_surface),('lower',lower_zone,lower_surface)]
   for region,zone,surface in [*active_regions,('main',None,PAVEMENT)]:
    part=P.intersection(rest,zone)if zone else rest
    if zone:rest=P.difference(rest,zone)
    m=Mesh('Ground '+name+' '+region+' '+mat)
    for tri in P.triangles(part):
     for lifted in surface.lift_triangle(tri):m.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
    if m.faces:
     target='venetian-lower-ground' if region=='lower' else name
     key=(target,region+'-'+name if region=='lower' else region,mat)
     compiled[key]=m;surfaces[key]=surface
# The Venetian bridge is a separate walkable surface above nonwalkable water.
bridge_mesh=Mesh('Ground Venetian bridge top')
for tri in P.triangles(bridge):
 for lifted in BRIDGE.lift_triangle(tri):bridge_mesh.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
if bridge_mesh.faces:compiled[('venetian-ground','bridge','deck')]=bridge_mesh;surfaces[('venetian-ground','bridge','deck')]=BRIDGE
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
 ob=m.finish([mats[mat]],collections[collection]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY')
 # Conforming can reverse thin triangles. Ground must face up: reversed slivers
 # rendered as black holes, especially around the newly bounded shore surfaces.
 if m.name.startswith('Ground ') and 'boundary' not in m.name:
  for face in bm.faces:
   face.normal_update()
   if face.normal.z < -1e-8:face.normal_flip()
 bm.to_mesh(ob.data);bm.free()
 # Terrain triangles share vertices and smooth normals. Flat per-face normals
 # made the exporter duplicate nearly every corner, tripling transfer size.
 # Keep vertical kerbs/retaining faces in their separate hard-edged objects.
 if (m.name.startswith('Ground ')and 'boundary'not in m.name and not any(part in m.name for part in (' landing ',' lower ','Venetian'))) or m.name.startswith('Fitting Venetian'):
  for face in ob.data.polygons:face.use_smooth=True
 uv=ob.data.uv_layers.new(name='Metric surface')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   if m.name=='Ground Venetian bridge top':
    t,o=local(v.x,v.y);uv.data[li].uv=(o/WIDTH,t)
   else:uv.data[li].uv=(v.x,v.y)
 return ob
for(name,region,mat),m in compiled.items():finish(m,mat,name)
for(target,mat),m in verticals.items():finish(m,mat,target)
# Separately bounded island crowns and banks. The rough mainland grid is based
# on roads, and extrapolating it across the lake buried the bridge. The toe is
# at the shared lake datum; an inset crown gives a simple editable broad slope.
water=SURFACES.surface('south-water')
def distance_to_ring(p, ring):
 def segment(a,b):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
  return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
 return min(segment(a,b) for a,b in zip(ring,ring[1:]+ring[:1]))
for ix,ring in enumerate(D['lake_islands'][:2]):
 outer=P.polygons([ring]);inner=buffer(outer,-.8);crown=buffer(outer,-3.0)
 zones=[('rock',P.difference(outer,inner)),('green',P.difference(inner,crown)),('green',crown)]
 zwater=water.height(*ring[0]);zcrown=zwater+1.55
 for zone_index,(mat,zone) in enumerate(zones):
  m=Mesh('Ground island '+str(ix+1)+' '+str(zone_index)+' '+mat)
  for tri in P.triangles(zone):
   m.add([(x,y,zwater+(zcrown-zwater)*min(1,distance_to_ring((x,y),ring)/3))for x,y in tri],[(0,1,2)])
  if m.faces:finish(m,mat,'cell-13-ground')
# Low, irregular planted masses are inferred from the 2023 and 2025 views;
# their individual positions are estimates, not surveyed trees.
rng=np.random.default_rng(2157);bushes=Mesh('Structure Venetian island planting')
def in_ring(x,y,ring):
 hit=False
 for (x1,y1),(x2,y2) in zip(ring,ring[1:]+ring[:1]):
  if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:hit=not hit
 return hit
for ring in D['lake_islands'][:2]:
 lo=np.min(ring,axis=0);hi=np.max(ring,axis=0);count=0
 for attempt in range(1000):
  x,y=rng.uniform(lo,hi);t,o=local(x,y)
  if abs(o)<4 or not in_ring(x,y,ring) or distance_to_ring((x,y),ring)<4.2:continue
  r=float(rng.uniform(.5,1.15));h=float(rng.uniform(.45,.9));z=water.height(x,y)+1.55
  bushes.lathe((x,y),[(z,.04),(z+h*.25,r*.8),(z+h*.55,r),(z+h*.82,r*.65),(z+h,.03)],segments=8)
  count+=1
  if count==9:break
if bushes.faces:finish(bushes,'shrub','venetian-structure')
m=Mesh('Structure southlake water')
for tri in P.triangles(P.intersection(study,lake)):
 for lifted in water.lift_triangle(tri):m.add(lifted,[(0,1,2)])
finish(m,'water','lake-water')
# Waterline facade is unique: the lido owns its top and this strip its exposed
# vertical edge. No fabricated cap is laid over the walkable paving.
# The exposed shore wall must follow the bounded bridge landing grade. Using
# the unmodified rough mainland here sent the wall above the deck at the join.
lido_surface=landing_surface;m=Mesh('Structure formal water edge')
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
# The shaded soffit and the cream side fascia have separate surface owners;
# the walkable deck remains in its own support part.
m=Mesh('Structure Venetian underside')
for tri in P.triangles(bridge):
 for lifted in BRIDGE.lift_triangle(tri):m.add([(x,y,z-.3)for x,y,z in lifted],[(2,1,0)])
finish(m,'structure','venetian-structure')
m=Mesh('Structure Venetian deck fascia')
for side in [-1,1]:
 edge=[at(0,side*HALF_WIDTH),at(L,side*HALF_WIDTH)]
 for a,b in zip(edge,edge[1:]):
  points=list(BRIDGE.edge_points(a,b))
  for aa,bb in zip(points,points[1:]):m.add([(aa[0],aa[1],aa[2]-.3),(bb[0],bb[1],bb[2]-.3),bb,aa],[(3,2,1,0)]if side>0 else[(0,1,2,3)])
finish(m,'cream','venetian-structure')
# Photographed arch and pier silhouettes; dimensions remain estimates.
station=at
def top(t):return BRIDGE.height(*station(t))-.3
# Shore-side access stair from the bridge to the separate lower lakeside path.
# Location and run are estimates from the 2023 ground view and close 3D image.
t=151;side=-1;start=HALF_WIDTH;run=3.6;n=11
zupper=BRIDGE.height(*station(t,side*start));zlower=lower_surface.height(*station(t,side*(start+run)))
m=Mesh('Ground Venetian lower access steps')
for j in range(n):
 o0=side*(start+run*j/n);o1=side*(start+run*(j+1)/n);z0=zupper+(zlower-zupper)*j/n;z1=zupper+(zlower-zupper)*(j+1)/n
 pa=station(t-.65,o0);pb=station(t+.65,o0);pc=station(t+.65,o1);pd=station(t-.65,o1)
 m.add([(pa[0],pa[1],z0),(pb[0],pb[1],z0),(pc[0],pc[1],z0),(pd[0],pd[1],z0)],[(3,2,1,0)])
 m.add([(pd[0],pd[1],z0),(pc[0],pc[1],z0),(pc[0],pc[1],z1),(pd[0],pd[1],z1)],[(0,1,2,3)])
finish(m,'paving','venetian-lower-ground')
# The tunnel ends meet the transition surface; the lower route stays open
# across the bridge. Exposed ends have a simple estimated abutment face.
m=Mesh('Structure Venetian shore tunnel abutments')
for end in (146,157):
 for side in range(10):
  o0=-2.5+side*.5;o1=o0+.5;p0=station(end,o0);p1=station(end,o1)
  lo0=lower_surface.height(*p0);lo1=lower_surface.height(*p1);hi=top(end)
  m.add([(p0[0],p0[1],lo0),(p1[0],p1[1],lo1),(p1[0],p1[1],hi),(p0[0],p0[1],hi)],[(0,1,2,3)] if end==146 else [(3,2,1,0)])
finish(m,'structure','venetian-structure')
# The bridge's exposed spandrels are pierced near the springings in the Sefton
# close view. Each outer and inner face has real openings and four returns;
# the grey curved intrados remains a separate surface beneath the deck.
def arch(t):
 q=(t-80)/15
 return -2.10+2.35*max(0,1-q*q)
# The opening nearest the crown tapers to a triangular tip, unlike the two
# taller apertures nearest the abutment. Direction indicates the tip station.
openings=[(65.9,66.7,0),(67.1,67.9,0),(68.3,69.3,1),
          (90.7,91.7,-1),(92.1,92.9,0),(93.3,94.1,0)]
cuts=sorted({65.,95.,*[65+j*.625 for j in range(49)],*[v for lo,hi,_ in openings for v in (lo,hi)],*[v for v in BRIDGE.stations if 65<v<95]})
spandrel=Mesh('Structure Venetian pierced arch spandrels')
vault=Mesh('Structure Venetian curved arch soffit')
def opening_floor(t,lo,hi,tip):
 low=arch(t)+.15;high=top(t)-.15
 f=(t-lo)/(hi-lo) if tip>0 else (hi-t)/(hi-lo) if tip<0 else 0
 return low+f*(high-low)
def arch_face(t0,t1,low0,low1,high0,high1,offset,reverse):
 p0=station(t0,offset);p1=station(t1,offset)
 spandrel.add([(p0[0],p0[1],low0),(p1[0],p1[1],low1),(p1[0],p1[1],high1),(p0[0],p0[1],high0)],[(3,2,1,0)] if reverse else [(0,1,2,3)])
for t0,t1 in zip(cuts,cuts[1:]):
 mid=(t0+t1)/2;opening=next((o for o in openings if o[0]<mid<o[1]),None)
 for side in (-1,1):
  for offset,reverse in ((side*2.4,side>0),(side*2.2,side<0)):
   if opening:
    arch_face(t0,t1,arch(t0),arch(t1),opening_floor(t0,*opening),opening_floor(t1,*opening),offset,reverse)
    arch_face(t0,t1,top(t0)-.15,top(t1)-.15,top(t0),top(t1),offset,reverse)
   else:arch_face(t0,t1,arch(t0),arch(t1),top(t0),top(t1),offset,reverse)
 l0=station(t0,-2.4);r0=station(t0,2.4);l1=station(t1,-2.4);r1=station(t1,2.4)
 vault.add([(l0[0],l0[1],arch(t0)),(l1[0],l1[1],arch(t1)),(r1[0],r1[1],arch(t1)),(r0[0],r0[1],arch(t0))],[(3,2,1,0)])
for side in (-1,1):
 for lo,hi,tip in openings:
  points=[t for t in cuts if lo<=t<=hi]
  rim=[(t,opening_floor(t,lo,hi,tip)) for t in points]+[(t,top(t)-.15) for t in reversed(points)]
  for a,b in zip(rim,rim[1:]+rim[:1]):
   if math.dist(a,b)<1e-8:continue
   outer0=station(a[0],side*2.4);outer1=station(b[0],side*2.4)
   inner0=station(a[0],side*2.2);inner1=station(b[0],side*2.2)
   spandrel.add([(outer0[0],outer0[1],a[1]),(outer1[0],outer1[1],b[1]),(inner1[0],inner1[1],b[1]),(inner0[0],inner0[1],a[1])],[(3,2,1,0)] if side>0 else [(0,1,2,3)])
finish(spandrel,'cream','venetian-structure');finish(vault,'structure','venetian-structure')
# The flat-span piers flare into shallow curved haunches under the deck rather
# than stopping as simple square columns. Their station positions are estimates.
m=Mesh('Structure Venetian flat span piers')
for t in (13,25,37,122,135,148):
 for side in (-1,1):
  z0=water.height(*station(t));off=side*2.05
  # A quarter-ellipse blends a .48 m stem into a 4.8 m head over .70 m;
  # this is about .40 of the estimated 12 m pier spacing. The local deck
  # profile drives every top point, including the gently graded approach.
  right=[];left=[]
  for j in range(13):
   theta=(math.pi/2)*j/12;dt=.24+2.16*(1-math.cos(theta));drop=.70*(1-math.sin(theta))
   right.append((dt,top(t+dt)-drop));left.append((-dt,top(t-dt)-drop))
  outline=[(-.24,z0),(.24,z0),*right,*reversed(left)]
  verts=[]
  for o in (off-.24,off+.24):
   for dt,z in outline:
    x,y=station(t+dt,o);verts.append((x,y,z))
  n=len(outline);faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
  faces.extend((i+n,(i+1)%n+n,(i+1)%n,i) for i in range(n))
  m.add(verts,faces)
finish(m,'cream','venetian-structure')
# The close side reference shows a row of small moulding blocks below the
# coping. These repeated details share one mesh and are omitted at District.
dentils=Mesh('Structure Venetian fascia dentils')
for side in (-1,1):
 for t in np.arange(13.25,149.5,.48):
  if green_at(t):continue
  z=BRIDGE.height(*station(t))
  vertices=[]
  for o in (side*HALF_WIDTH,side*(HALF_WIDTH+.045)):
   for dt,h in ((-.05,-.26),(.05,-.26),(.05,-.17),(-.05,-.17)):
    x,y=station(t+dt,o);vertices.append((x,y,z+h))
  dentils.add(vertices,[(0,1,2,3),(7,6,5,4),(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3)] if side>0 else [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
finish(dentils,'cream','venetian-structure')
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
# Open timber balustrade: separate shaped rails, turned spindles and panelled
# piers. The same station profile drives deck, handrail and the coarser LoDs.
from venetian_fittings import make_balusters,panel_prototype
balusters=make_balusters('detail',BRIDGE);finish(balusters,'cream','venetian-structure')
piers=PIERS
rails=Mesh('Structure Venetian open handrails and base rails')
def railbeam(target,t0,t1,o,zlo,zhi,width):
 z0=BRIDGE.height(*station(t0,o));z1=BRIDGE.height(*station(t1,o));verts=[]
 for zz0,zz1 in ((zlo,zlo),(zhi,zhi)):
  for tt,oo,zz in ((t0,o-width/2,z0+zz0),(t1,o-width/2,z1+zz1),(t1,o+width/2,z1+zz1),(t0,o+width/2,z0+zz0)):
   x,y=station(tt,oo);verts.append((x,y,zz))
 # The deck owns the contact surface below a base rail; avoid a duplicate
 # downward face where the rail enters a pier or an island lamp footing.
 faces=[(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 if zlo!=0:faces.insert(0,(3,2,1,0))
 target.add(verts,faces)
for side in (-1,1):
 # Short pieces follow deliberate deck-profile breaks. Pier and gate gaps are
 # cut before creating rails, so there are no hidden solid parapet duplicates.
 cuts=sorted(set([RAIL_START,RAIL_END,150.3,151.7]+[float(q) for q in range(0,int(L)+1,2) if RAIL_START<q<RAIL_END]+[p+d for p in piers for d in (-.19,.19) if RAIL_START<p+d<RAIL_END]+[8,45,60,65,70,75,80,85,90,95,100,125,145,155]+[x for span in GREEN_SECTIONS for x in span]))
 for a0,a1 in zip(cuts,cuts[1:]):
  mid=(a0+a1)/2
  if a1-a0<1e-5 or any(abs(mid-p)<.19 for p in piers) or green_at(mid) or (side==-1 and 150.3<mid<151.7):continue
  railbeam(rails,a0,a1,side*RAIL_OFFSET,0,.16,.16);railbeam(rails,a0,a1,side*RAIL_OFFSET,.92,1.04,.20)
finish(rails,'cream','venetian-structure')
# Low, open green metal island railings seen in the oblique photograph.
# All repeated pickets are collected in one mesh for efficient export.
greenrails=Mesh('Structure Venetian island metal railings')
for side in (-1,1):
 for lo,hi in GREEN_SECTIONS:
  cuts=sorted({lo,hi,*[q for q in BRIDGE.stations if lo<q<hi]})
  for a0,a1 in zip(cuts,cuts[1:]):
   railbeam(greenrails,a0,a1,side*RAIL_OFFSET,0,.055,.055)
   railbeam(greenrails,a0,a1,side*RAIL_OFFSET,.95,1.0,.055)
  count=math.floor((hi-lo)/.22)
  for i in range(1,count):
   tt=lo+(hi-lo)*i/count
   if any(abs(tt-p)<.20 for p in GREEN_STANDARDS):continue
   railbeam(greenrails,tt-.014,tt+.014,side*RAIL_OFFSET,.055,.95,.028)
finish(greenrails,'gate-green','venetian-structure')
prototypes=panel_prototype();post_mesh=prototypes['pier'];column_mesh=prototypes['column']
pier_mesh=Mesh('Structure Venetian panelled piers');lamps=Mesh('Structure Venetian green lamp columns')
for side in (-1,1):
 for t in piers:
  z=BRIDGE.height(*station(t,side*RAIL_OFFSET))
  for source,target in ((post_mesh,pier_mesh),(column_mesh,lamps)):
   vv=[]
   for x,y,h in source.vertices:
    xx,yy=station(t+x,side*RAIL_OFFSET+y)
    # Split base follows the profile, while mouldings and columns stay upright.
    base=BRIDGE.height(xx,yy) if source is post_mesh and abs(h)<1e-9 else z
    vv.append((xx,yy,base+h))
   target.add(vv,source.faces)
for side in (-1,1):
 for t in GREEN_STANDARDS:
  z=BRIDGE.height(*station(t,side*RAIL_OFFSET));vv=[]
  for x,y,h in column_mesh.vertices:
   xx,yy=station(t+x,side*RAIL_OFFSET+y);vv.append((xx,yy,z+(h-1.07)*2.65/1.58))
  lamps.add(vv,column_mesh.faces)
finish(pier_mesh,'cream','venetian-structure');finish(lamps,'gate-green','venetian-structure')
# The side-mounted globe follows the clearly visible 2023 foreground lamp.
globes=Mesh('Structure Venetian observed globe');t=155;side=-1;x,y=station(t,side*(RAIL_OFFSET+.24));z=BRIDGE.height(*station(t,side*RAIL_OFFSET))+2.57
profile=[(z-.16,.005),(z-.14,.08),(z-.10,.13),(z,.16),(z+.10,.13),(z+.14,.08),(z+.16,.005)]
globes.lathe((x,y),profile,segments=16)
# The published oblique shows several centred globes and bare standards. These
# approximate stations cover only the clearly visible first-island approach.
for side,stations in ((1,(25,35,45,55,65)),(-1,(25,45,55,65))):
 for t in stations:
  x,y=station(t,side*RAIL_OFFSET);z=BRIDGE.height(x,y)+2.80
  globes.lathe((x,y),[(z-.16,.005),(z-.14,.08),(z-.10,.13),(z,.16),(z+.10,.13),(z+.14,.08),(z+.16,.005)],segments=16)
finish(globes,'globe','venetian-structure')
socket=Mesh('Structure Venetian observed globe socket')
p0=station(155,-RAIL_OFFSET);p1=station(155,-RAIL_OFFSET-.12);z=BRIDGE.height(*p0)+2.57
socket.tube([(p0[0],p0[1],z),(p1[0],p1[1],z)],.045,sides=8)
finish(socket,'socket','venetian-structure')
# One observed green side gate at the Princes Park shore (2023 photograph).
# Its 1.4m location and stair connection are estimates from the loaded 3D view.
gate=Mesh('Structure Venetian shore side gate')
def gatebeam(t0,z0,t1,z1,w=.035):
 dx=t1-t0;dz=z1-z0;ln=math.hypot(dx,dz);nx=-dz/ln*w/2;nz=dx/ln*w/2
 corners=[(t0+nx,z0+nz),(t1+nx,z1+nz),(t1-nx,z1-nz),(t0-nx,z0-nz)]
 verts=[]
 for off in (-RAIL_OFFSET-.03,-RAIL_OFFSET+.03):
  for tt,zz in corners:
   x,y=station(tt,off);verts.append((x,y,zz))
 gate.add(verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
z=BRIDGE.height(*station(151,-RAIL_OFFSET))
for t0,z0,t1,z1 in [(150.34,z+.05,151.66,z+.05),(150.34,z+1.02,151.66,z+1.02),(150.34,z+.05,150.34,z+1.02),(151.66,z+.05,151.66,z+1.02),(150.4,z+.12,151.6,z+.95),(150.4,z+.95,151.6,z+.12)]:gatebeam(t0,z0,t1,z1)
for k in range(1,6):
 tt=150.34+k*1.32/6;gatebeam(tt,z+.08,tt,z+.99,.022)
# Small hinge knuckles and latch make the single leaf legible at close range.
for zz in (.22,.80):
 x,y=station(150.35,-RAIL_OFFSET);gate.lathe((x,y),[(z+zz,.027),(z+zz+.09,.027)],segments=12)
gatebeam(151.55,z+.53,151.70,z+.53,.025)
finish(gate,'gate-green','venetian-structure')
# Estimated green side handrails descend with the access steps; support posts
# stand beside, rather than on, the treads.
rail=Mesh('Structure Venetian lower access handrails')
def stairbeam(tt,o0,z0,o1,z1,w=.035):
 do=o1-o0;dz=z1-z0;ln=math.hypot(do,dz);no=-dz/ln*w/2;nz=do/ln*w/2
 corners=[(o0+no,z0+nz),(o1+no,z1+nz),(o1-no,z1-nz),(o0-no,z0-nz)];verts=[]
 for dt in (-w/2,w/2):
  for oo,zz in corners:
   x,y=station(tt+dt,oo);verts.append((x,y,zz))
 rail.add(verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
for tt in (150.3,151.7):
 stairbeam(tt,-HALF_WIDTH-.05,zupper+.82,-HALF_WIDTH-3.55,zlower+.82)
 for f in (.06,.35,.65,.96):
  oo=-HALF_WIDTH-3.6*f;zz=zupper+(zlower-zupper)*f;stairbeam(tt,oo,zz,oo,zz+.82,.025)
finish(rail,'gate-green','venetian-structure')
# Continuous coarse sea-wall strip; its shared end exactly matches the prior
# north segment. Caps are unique and vertical faces stand on mainland grade.
edge=D['coast_wall_centres'];outline=parallel(edge,-.16)+list(reversed(parallel(edge,.16)))
wall=P.polygons([outline])
# Terminal interface is mitred to the existing strip at its original start.
m=Mesh('Structure coastal sea wall envelope')
for tri in P.triangles(wall):
 for lifted in PAVEMENT.lift_triangle(tri):m.add([(x,y,z+.8)for x,y,z in lifted],[(0,1,2)])
# Boundary extraction avoids internal fragment caps.
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
