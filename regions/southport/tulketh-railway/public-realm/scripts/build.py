"""Owned street canvas, open station platforms and independent railway levels."""
import bpy,bmesh,ctypes as C,json,math,os,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from plan_geometry import Plan
from datum import grade,PAVEMENT
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';P=Plan()
fn=P.lib.GEOSBuffer_r;fn.restype=C.c_void_p;fn.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
def buffer(g,w):return P.own(fn(P.context,g,w,4))
def ribbon(points,width):
 g=P.own(P.read(P.context,P.reader,('LINESTRING ('+','.join(f'{x} {y}'for x,y in points)+')').encode()))
 return buffer(g,width/2)
def union(gs):return P.polygons([t for g in gs for t in P.triangles(g)])
def rect(a,b,c,d):return [(a,c),(b,c),(b,d),(a,d)]
blocks=[b for f in [D['block_plan'],*D['existing_block_plans']]for b in json.loads((REPO/f).read_text())['blocks'] if not b.get('base_z_m')]
study=P.polygons(D['study_polygons']);exclusions=P.polygons(D['existing_ground_exclusions'])
available=P.difference(P.difference(study,exclusions),P.polygons([b['footprint']for b in blocks]))
rail=P.intersection(study,P.polygons(D['rail_reservation']))
# The existing Eastbank cutting already owns its ballast surface. The new
# track strips continue over it, but do not duplicate its ground faces.
old_cut=P.intersection(ribbon([[-390,-605.4],[-334,-602.1],[-280,-598.8]],12),P.polygons([rect(-385,-285,-620,-580)]))
platform=P.intersection(rail,P.polygons([r['polygon']for r in D['platforms']]))
rail_ground=P.difference(P.difference(P.difference(rail,platform),old_cut),P.polygons([b['footprint']for b in blocks]))
available=P.difference(available,rail)
roads=union([ribbon(r['points'],r['width'])for r in D['roads']])
road=P.intersection(available,roads)
paths=P.intersection(available,union([ribbon(r['points'],r['width'])for r in D['paths']]))
foot=P.difference(P.intersection(available,buffer(roads,D['footway_width_m'])),road)
foot=P.difference(union([foot,paths]),road)
remaining=buffer(P.difference(P.difference(available,road),foot),0)
parking=P.intersection(remaining,P.polygons([r['polygon']for r in D['parking']]))
courts=P.difference(remaining,parking)
# Only the photographed Tulketh stretch receives edge restrictions. Paint
# replaces asphalt; it does not float over a second coplanar road face.
yellow_full=union([P.difference(buffer(roads,-a),buffer(roads,-b))for a,b in [(.15,.22),(.33,.40)]])
tulketh=union([ribbon(r['points'],r['width']+1)for r in D['roads']if r['name']=='Tulketh Street'])
yellow=P.intersection(P.intersection(yellow_full,tulketh),road)
mx,my=D['mini_roundabout']['xy'];radius=D['mini_roundabout']['radius_m']
white=P.intersection(road,P.polygons([[(mx+radius*math.cos(i*math.tau/32),my+radius*math.sin(i*math.tau/32))for i in range(32)]]))
asphalt=P.difference(P.difference(road,yellow),white)
colours={'asphalt':(.09,.095,.10),'paving':(.48,.45,.40),'courts':(.34,.33,.31),'parking':(.14,.15,.15),'yellow':(.80,.62,.13),'kerb':(.42,.42,.39),'rail':(.22,.22,.21),'steel':(.15,.17,.18),'platform':(.36,.36,.34),'structure':(.30,.29,.26)}
colours.update({'white':(.82,.81,.75),'green':(.16,.23,.11)})
mats={}
for name,col in colours.items():
 m=bpy.data.materials.new('Tulketh '+name);m.use_nodes=True;m.diffuse_color=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);mats[name]=m
collections={}
for name in [f'section-{i}-{kind}'for i in range(4)for kind in ['ground','rail']]+['rail-ground','platform-ground']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
compiled={}
for i,(lo,hi) in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 cell=P.polygons([rect(-340,55,lo,hi)]);name=f'section-{i}-ground'
 for mat,g in [('asphalt',asphalt),('paving',foot),('parking',parking),('courts',courts),('yellow',yellow),('white',white)]:
  m=Mesh('Ground '+name+' '+mat)
  # Normalise precision-overlay rings before the next overlay; offset roads
  # can otherwise leave a self-touching zero-width edge at a joined buffer.
  for tri in P.triangles(P.intersection(buffer(g,0),cell)):
   for lifted in PAVEMENT.lift_triangle(tri):m.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
  if m.faces:compiled[(name,mat)]=m
# Noding happens before lifting, so surfaces have identical boundary vertices.
import southport3d.conform as cf
cf.GRID=1/8192;cf.TOLERANCE=.0002
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled);edges=defaultdict(list)
for (name,mat),m in compiled.items():
 for face in m.faces:
  for ia,ib in zip(face,face[1:]+face[:1]):
   a,b=m.vertices[ia],m.vertices[ib];key=tuple(sorted((tuple(round(v,4)for v in a[:2]),tuple(round(v,4)for v in b[:2]))));edges[key].append((name,mat,a,b))
curbs={};road_mats={'asphalt','yellow','white'}
for hits in edges.values():
 if not any(h[1]in road_mats for h in hits) or not any(h[1]not in road_mats for h in hits):continue
 name,_,a,b=next(h for h in hits if h[1]in road_mats);m=curbs.setdefault((name,'kerb'),Mesh('Ground '+name+' kerb'))
 za,zb=grade(*a[:2]),grade(*b[:2]);m.add([(a[0],a[1],za-.12),(b[0],b[1],zb-.12),(b[0],b[1],zb),(a[0],a[1],za)],[(3,2,1,0)])
for (name,mat),m in compiled.items():m.vertices=[(x,y,grade(x,y)-(.12 if mat in road_mats else 0))for x,y,z in m.vertices]
compiled.update(curbs)
def finish(m,mat,collection):
 if not m.faces:return
 ob=m.finish([mats[mat]],collections[collection]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001 if mat in {'steel','rail','green'} else 1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-8],context='FACES_ONLY');bm.normal_update()
 # All non-kerb meshes here are upper surfaces. Narrow switch strips can
 # reverse a near-collinear triangle on float32 conversion; orient after it.
 if mat!='kerb':
  for face in bm.faces:
   if face.normal.z<0:face.normal_flip()
 bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.new(name='Metric canvas')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 return ob
for (name,mat),m in compiled.items():finish(m,mat,name)
contains=P.lib.GEOSCovers_r;contains.restype=C.c_char;contains.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p]
banks={}
for hits in edges.values():
 if len(hits)!=1:continue
 name,mat,a,b=hits[0];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<.001:continue
 x=(a[0]+b[0])/2+dy/length*.003;y=(a[1]+b[1])/2-dx/length*.003
 point=P.own(P.read(P.context,P.reader,f'POINT ({x} {y})'.encode()))
 if contains(P.context,rail,point)!=b'\x01':continue
 m=banks.setdefault(name.replace('-ground','-rail'),Mesh('Structure cutting edge '+name))
 za=grade(*a[:2])-(.12 if mat in road_mats else 0);zb=grade(*b[:2])-(.12 if mat in road_mats else 0)
 m.add([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],zb),(a[0],a[1],za)],[(0,1,2,3)])
for name,m in banks.items():finish(m,'structure',name)
ballast=union([ribbon(r['points'],4.2)for r in D['tracks']])
green=P.intersection(P.difference(rail_ground,ballast),P.polygons([rect(-340,55,-650,-450)]))
rail_ground=P.difference(rail_ground,green)
for name,g,z,mat in [('rail-ground',rail_ground,0,'rail'),('rail-ground',green,0,'green'),('platform-ground',platform,.65,'platform')]:
 m=Mesh('Ground '+name)
 for tri in P.triangles(g):m.add([(x,y,z)for x,y in tri],[(0,1,2)])
 finish(m,mat,name)
platform_sides=Mesh('Structure platform edges')
for row in D['platforms']:
 p=row['polygon']
 if sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(p,p[1:]+p[:1]))<0:p=list(reversed(p))
 for a,b in zip(p,p[1:]+p[:1]):platform_sides.add([(*a,0),(*b,0),(*b,.65),(*a,.65)],[(0,1,2,3)])
finish(platform_sides,'structure','section-3-rail')
# Two narrow steel running surfaces per track. They are unioned at points and
# split by streaming tile, avoiding coplanar rail intersections at the fan.
rail_strips=union([ribbon(parallel(r['points'],side*.7175),.065)for r in D['tracks']for side in [-1,1]])
rail_strips=P.intersection(P.difference(rail_strips,platform),rail)
sf=P.lib.GEOSTopologyPreserveSimplify_r;sf.restype=C.c_void_p;sf.argtypes=[C.c_void_p,C.c_void_p,C.c_double]
# Remove submillimetre offset-curve vertices before tessellation; otherwise
# converting almost-collinear switch triangles to float32 folds tiny slivers.
rail_strips=P.own(sf(P.context,rail_strips,.001))
track_meshes={}
for i,(lo,hi) in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 m=Mesh('Structure running rails '+str(i))
 for tri in P.triangles(P.intersection(rail_strips,P.polygons([rect(-340,55,lo,hi)]))):m.add([(x,y,.09)for x,y in tri],[(0,1,2)])
 track_meshes[f'section-{i}-rail']=m
for name,m in track_meshes.items():finish(m,'steel',name)
P.close();(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
