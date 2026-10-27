"""Hoghton block ground, with shared kerb/paint curves and one floor owner."""
import bpy, bmesh, ctypes as C, json, math, os, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from plan_geometry import Plan
from datum import grade,SURFACE
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'
def rect(a,b,c,d): return [(a,c),(b,c),(b,d),(a,d)]
def ribbon(points,width,offset=0):
 return parallel(points,offset-width/2)+list(reversed(parallel(points,offset+width/2)))
P=Plan()
ERROR=C.CFUNCTYPE(None,C.c_char_p,C.c_void_p)
@ERROR
def geos_error(message,userdata):print('GEOS:',message.decode(),flush=True)
handler=P.lib.GEOSContext_setErrorMessageHandler_r;handler.restype=C.c_void_p;handler.argtypes=[C.c_void_p,ERROR,C.c_void_p];handler(P.context,geos_error,None)
precision=P.lib.GEOSGeom_setPrecision_r;precision.restype=C.c_void_p;precision.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
buffer_fn=P.lib.GEOSBuffer_r;buffer_fn.restype=C.c_void_p;buffer_fn.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
def buffer(g,d):
 raw=P.own(buffer_fn(P.context,g,d,4))
 return P.own(precision(P.context,raw,.000001,0))
# Touching ownership boundaries can return line-only components. Ground uses
# polygonal area only; discard these before the next overlay operation.
intersection=P.intersection
P.intersection=lambda a,b: buffer(intersection(a,b),0)
def union(gs):
 # Union via triangulated polygon collection keeps the tiny GEOS adapter local.
 return P.polygons([t for g in gs for t in P.triangles(g)])
road_full=P.polygons([ribbon(r['points'],r['width']) for r in D['roads']])
road_full=buffer(buffer(road_full,D['junction_radius_m']),-D['junction_radius_m'])
from bank_footprint import bank_cutouts
cutters=list(D['existing_ground_exclusions'])+D['extra_building_cutouts']+bank_cutouts(REPO)
for path in [D['block_plan'],*D['existing_block_plans']]:
 cutters += [b['footprint'] for b in json.loads((REPO/path).read_text())['blocks']]
available=P.difference(P.polygons([D['outer']]),P.polygons(cutters))
parking_full=P.polygons([p['polygon'] for p in D['parking_courts']])
road=P.intersection(union([road_full,parking_full]),available)
foot_full=union([buffer(P.polygons([ribbon(r['points'],r['width'])]),r['footway']) for r in D['roads'] if r['footway']])
foot_full=buffer(buffer(foot_full,D['junction_radius_m']),-D['junction_radius_m'])
foot=P.difference(P.intersection(foot_full,available),road)
remaining=P.difference(P.difference(available,road),foot)
green=P.intersection(remaining,P.polygons([p['polygon'] for p in D['landscaped_reservations']]))
courts=P.difference(remaining,green)
# Paint offsets the continuous road boundary BEFORE ownership/tile clipping.
# Yellow lines are confined to observed junction approaches; parked lengths
# retain white bay edges rather than inventing continuous restrictions.
yellow_full=union([P.difference(buffer(road_full,-a),buffer(road_full,-b)) for a,b in [(.15,.22),(.33,.40)]])
junctions=[(25,-144),(225.734,-158.667),(368.798,-165.949),(518.524,-175.857),(224.285,-59.271),(369.806,-62.329),(528.819,-54.806)]
yellow_masks=[rect(x-15,x+15,y-15,y+15) for x,y in junctions]
yellow=P.intersection(P.intersection(yellow_full,P.polygons(yellow_masks)),road)
white_rows=[]
bus_rows=[]
hoghton=D['roads'][0]
# Dated imagery shows intermittent centre lines and parallel parking edges.
for offset in [-4,0,4]:
 pts=parallel(hoghton['points'],offset)
 for x in np.arange(42,506,3 if offset else 6):
  if any(abs(x-j[0])<12 for j in junctions[:4]):continue
  white_rows += P.triangles(P.intersection(P.polygons([ribbon(pts,.10)]),P.polygons([rect(x,x+(1 if offset else 2),-200,-120)])))
# Junction approach give-way bars on the terminating side streets.
for cx,cy in [(225.7,-151),(368.8,-158),(225.7,-166.5),(368.8,-173.5)]:
 for y in [cy,cy+.45]:
  for x in np.arange(cx-3,cx-.1,.9):white_rows.append(rect(x,x+.6,y,y+.18))
# Longitudinal edge markings on Manchester Road, with rounded junction gaps.
for r in D['roads']:
 if r['name']!='Manchester Road':continue
 pts=r['points']
 for a,b in zip(pts,pts[1:]):
  distance=math.dist(a,b)
  for t in np.arange(0,distance,6):
   if distance<.01:continue
   aa=[a[i]+(b[i]-a[i])*t/distance for i in range(2)];bb=[a[i]+(b[i]-a[i])*min(t+2,distance)/distance for i in range(2)]
   if any(math.dist(aa,j)<12 for j in junctions):continue
   white_rows.append(ribbon([aa,bb],.10))
# Parking court rows use explicit estimated placements; clip every stripe to
# its own court and remove buildings/roads in the common material partition.
for park in D['parking_courts']:
 poly=park['polygon'];xmin=min(p[0] for p in poly);xmax=max(p[0] for p in poly);ymin=min(p[1] for p in poly);ymax=max(p[1] for p in poly)
 rows=[]
 for y in np.arange(ymin+3,ymax-2,2.5):
  rows.append(rect(xmin+1,min(xmin+5.7,xmax-1),y,y+.09))
 for tri in P.triangles(P.intersection(P.polygons(rows),P.polygons([poly]))):white_rows.append(tri)
# The north-side bus-stop box is visible in the dated Church Street panorama.
# Its endpoint positions are estimates; no current regulation is asserted.
for x in np.arange(385,415,2):
 pts=parallel(hoghton['points'],3.5)
 bus_rows+=P.triangles(P.intersection(P.polygons([ribbon(pts,.15)]),P.polygons([rect(x,x+1,-200,-120)])))
yellow=union([yellow,P.intersection(P.polygons(bus_rows),road)])
white=P.difference(P.intersection(P.polygons(white_rows),road),yellow)
asphalt=P.difference(P.difference(road,yellow),white)
materials={'asphalt':(.085,.092,.093),'paving':(.30,.27,.23),'courts':(.36,.35,.33),'green':(.16,.23,.10),'yellow':(.75,.57,.12),'white':(.72,.73,.69),'kerb':(.40,.40,.37)}
mats={}
for name,colour in materials.items():
 m=bpy.data.materials.new('Hoghton '+name);m.use_nodes=True;m.diffuse_color=(*colour,1)
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=.9
 if name=='paving':
  for file,normal in [('paving.png',False),('paving-normal.png',True)]:
   im=bpy.data.images.load(str(ROOT/'textures'/file));im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im
   if normal:
    im.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
   else:m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 mats[name]=m
compiled={};collections={}
for ti,(lo,hi) in enumerate(zip(D['tile_cuts'],D['tile_cuts'][1:])):
 name=f'section-{ti:02d}'
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
 cuts=[lo,hi]
 for a,b in zip(cuts,cuts[1:]):
  for ya,yb in [(D['bounds'][2],-36),(-36,D['bounds'][3])]:
   cell=P.polygons([rect(a,b,ya,yb)])
   for mat,g in [('asphalt',asphalt),('paving',foot),('courts',courts),('green',green),('yellow',yellow),('white',white)]:
    m=compiled.setdefault((name,mat),Mesh('Ground '+name+' '+mat))
    for tri in P.triangles(P.intersection(g,cell)):
     for lifted in SURFACE.lift_triangle(tri):m.add([(x,y,0) for x,y,z in lifted],[(0,1,2)])
P.close()
# Join road, paint, paving and cell boundaries on one plane before grading.
import southport3d.conform as cf
cf.GRID=1e-5;cf.TOLERANCE=2e-5
compiled={k:m for k,m in compiled.items() if m.faces}
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
# Overlay operations can leave distinct endpoints tens of micrometres apart.
# Weld only such coincident endpoints before fanning; rounding a whole coarse
# grid would instead bend long boundaries and introduce overlaps.
nearby=defaultdict(list)
for m in compiled.values():
 for i,v in enumerate(m.vertices):
  key=(math.floor(v[0]/.0001),math.floor(v[1]/.0001));found=None
  for dx in [-1,0,1]:
   for dy in [-1,0,1]:
    for q in nearby[(key[0]+dx,key[1]+dy)]:
     if math.dist(v,q)<.0001:found=q;break
    if found is not None:break
   if found is not None:break
  if found is None:nearby[key].append(v)
  else:m.vertices[i]=found
compiled,report=cf.conform(compiled,preserve_triangles=True,weld_distance=5e-5)
edge_mats=defaultdict(list);road_mats={'asphalt','yellow','white'}
for (name,mat),m in compiled.items():
 for face in m.faces:
  for ia,ib in zip(face,face[1:]+face[:1]):
   a,b=m.vertices[ia],m.vertices[ib];key=tuple(sorted((tuple(round(float(v),4) for v in a[:2]),tuple(round(float(v),4) for v in b[:2]))));edge_mats[key].append((name,mat,a,b))
curbs={}
for hits in edge_mats.values():
 if not any(h[1] in road_mats for h in hits) or not any(h[1] not in road_mats for h in hits):continue
 name,_,a,b=next(h for h in hits if h[1] in road_mats)
 m=curbs.setdefault((name,'kerb'),Mesh('Ground '+name+' kerb'));za,zb=grade(*a[:2]),grade(*b[:2])
 m.add([(a[0],a[1],za-.12),(b[0],b[1],zb-.12),(b[0],b[1],zb),(a[0],a[1],za)],[(0,1,2,3)])
for (name,mat),m in compiled.items():m.vertices=[(x,y,grade(x,y)-(.12 if mat in road_mats else 0)) for x,y,z in m.vertices]
compiled.update(curbs)
for (name,mat),m in compiled.items():
 ob=m.finish([mats[mat]],collections[name]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.new(name='Metric block paving')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/1.2,v.y/1.2)
(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
