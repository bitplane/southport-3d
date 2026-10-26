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
from venetian_ground import Transition,polygon
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
land=P.difference(P.difference(P.difference(study,lake),P.polygons([b['footprint']for b in blocks])), P.polygons(D['lake_islands'][:2]))
# Keep the deck continuous across the islands; only its dry-shore approaches
# replace underlying paving. Island ground remains a separate layer below it.
bridge=P.intersection(study,line(D['venetian_axis'],D['venetian_width_m']))
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
    from venetian_ground import local
    t,o=local(v.x,v.y);uv.data[li].uv=(o/5.2,t)
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
from venetian_ground import local
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
finish(m,'structure','venetian-structure')
# Preliminary structural massing: central arched fascia and discrete piers.
# The island/arch reference constrains silhouette; dimensions remain estimated.
a,b=D['venetian_axis'][0],D['venetian_axis'][-1];length=math.dist(a,b);ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length;vx,vy=-uy,ux
def station(t,o=0):return (a[0]+ux*t+vx*o,a[1]+uy*t+vy*o)
def top(t):return BRIDGE.height(*station(t))-.3
# Shore-side access stair from the bridge to the separate lower lakeside path.
# Location and run are estimates from the 2023 ground view and close 3D image.
t=151;side=-1;start=2.6;run=3.6;n=11
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
m=Mesh('Structure Venetian central arch massing')
# Face edges share the deck underside boundary; no coincident top face.
steps=24
for j in range(steps):
 t0=65+30*j/steps;t1=65+30*(j+1)/steps
 def arch(t):
  q=(t-80)/15;return -0.80+1.05*max(0,1-q*q)
 for side in [-1,1]:
  p0=station(t0,side*2.4);p1=station(t1,side*2.4)
  m.add([(p0[0],p0[1],arch(t0)),(p1[0],p1[1],arch(t1)),(p1[0],p1[1],top(t1)),(p0[0],p0[1],top(t0))],[(0,1,2,3)] if side>0 else [(3,2,1,0)])
 # underside of the arch vault
 l0=station(t0,-2.4);r0=station(t0,2.4);l1=station(t1,-2.4);r1=station(t1,2.4)
 m.add([(l0[0],l0[1],arch(t0)),(l1[0],l1[1],arch(t1)),(r1[0],r1[1],arch(t1)),(r0[0],r0[1],arch(t0))],[(3,2,1,0)])
finish(m,'structure','venetian-structure')
# Preliminary paired piers under flatter spans, grounded at the common lake
# level. Their positions are proportional estimates from side photographs.
m=Mesh('Structure Venetian flat span piers')
for t in (13,25,37,122,135,148):
 for side in (-1,1):
  z0=water.height(*station(t));z1=top(t);half=.24;off=side*2.05
  verts=[]
  for z in (z0,z1):
   for dt,do in ((-half,-half),(half,-half),(half,half),(-half,half)):
    x,y=station(t+dt,off+do);verts.append((x,y,z))
  m.add(verts,[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
finish(m,'structure','venetian-structure')
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
piers=[5+10*i for i in range(16)]+[80]
rails=Mesh('Structure Venetian open handrails and base rails')
def railbeam(t0,t1,o,zlo,zhi,width):
 z0=BRIDGE.height(*station(t0,o));z1=BRIDGE.height(*station(t1,o));verts=[]
 for zz0,zz1 in ((zlo,zlo),(zhi,zhi)):
  for tt,oo,zz in ((t0,o-width/2,z0+zz0),(t1,o-width/2,z1+zz1),(t1,o+width/2,z1+zz1),(t0,o+width/2,z0+zz0)):
   x,y=station(tt,oo);verts.append((x,y,zz))
 rails.add(verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
for side in (-1,1):
 # Short pieces follow deliberate deck-profile breaks. Pier and gate gaps are
 # cut before creating rails, so there are no hidden solid parapet duplicates.
 cuts=sorted(set([0,160,150.3,151.7]+list(range(0,161,2))+[p+d for p in piers for d in (-.24,.24) if 0<p+d<160]+[65,70,75,80,85,90,95,100,125,145,155]))
 for a0,a1 in zip(cuts,cuts[1:]):
  mid=(a0+a1)/2
  if a1-a0<1e-5 or any(abs(mid-p)<.24 for p in piers) or (side==-1 and 150.3<mid<151.7):continue
  railbeam(a0,a1,side*2.48,.05,.16,.16);railbeam(a0,a1,side*2.48,.92,1.04,.20)
finish(rails,'cream','venetian-structure')
prototypes=panel_prototype();post_mesh=prototypes['pier'];column_mesh=prototypes['column']
pier_mesh=Mesh('Structure Venetian panelled piers');lamps=Mesh('Structure Venetian green lamp columns')
for side in (-1,1):
 for t in piers:
  if t>160:continue
  z=BRIDGE.height(*station(t,side*2.48))
  for source,target in ((post_mesh,pier_mesh),(column_mesh,lamps)):
   vv=[]
   for x,y,h in source.vertices:
    xx,yy=station(t+x,side*2.48+y);vv.append((xx,yy,z+h))
   target.add(vv,source.faces)
finish(pier_mesh,'cream','venetian-structure');finish(lamps,'gate-green','venetian-structure')
# The single side-mounted globe follows the clearly visible 2023 foreground
# lamp; other head states are unresolved and are not inferred from that one.
globes=Mesh('Structure Venetian observed globe');t=155;side=-1;x,y=station(t,side*2.72);z=BRIDGE.height(*station(t,side*2.48))+2.57
profile=[(z-.16,.005),(z-.14,.08),(z-.10,.13),(z,.16),(z+.10,.13),(z+.14,.08),(z+.16,.005)]
globes.lathe((x,y),profile,segments=16);finish(globes,'globe','venetian-structure')
# One observed green side gate at the Princes Park shore (2023 photograph).
# Its 1.4m location and stair connection are estimates from the loaded 3D view.
gate=Mesh('Structure Venetian shore side gate')
def gatebeam(t0,z0,t1,z1,w=.035):
 dx=t1-t0;dz=z1-z0;ln=math.hypot(dx,dz);nx=-dz/ln*w/2;nz=dx/ln*w/2
 corners=[(t0+nx,z0+nz),(t1+nx,z1+nz),(t1-nx,z1-nz),(t0-nx,z0-nz)]
 verts=[]
 for off in (-2.59,-2.53):
  for tt,zz in corners:
   x,y=station(tt,off);verts.append((x,y,zz))
 gate.add(verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
z=BRIDGE.height(*station(151,-2.56))
for t0,z0,t1,z1 in [(150.34,z+.05,151.66,z+.05),(150.34,z+1.02,151.66,z+1.02),(150.34,z+.05,150.34,z+1.02),(151.66,z+.05,151.66,z+1.02),(150.4,z+.12,151.6,z+.95),(150.4,z+.95,151.6,z+.12)]:gatebeam(t0,z0,t1,z1)
for k in range(1,6):
 tt=150.34+k*1.32/6;gatebeam(tt,z+.08,tt,z+.99,.022)
# Small hinge knuckles and latch make the single leaf legible at close range.
for zz in (.22,.80):
 x,y=station(150.35,-2.56);gate.lathe((x,y),[(z+zz,.027),(z+zz+.09,.027)],segments=12)
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
 stairbeam(tt,-2.65,zupper+.82,-6.15,zlower+.82)
 for f in (.06,.35,.65,.96):
  oo=-2.6-3.6*f;zz=zupper+(zlower-zupper)*f;stairbeam(tt,oo,zz,oo,zz+.82,.025)
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
