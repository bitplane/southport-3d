"""Stanley/Bath block ground, with shared kerb/paint curves and one floor owner."""
import bpy, bmesh, ctypes as C, json, math, os, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from plan_geometry import Plan
from datum import grade
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'
def rect(a,b,c,d): return [(a,c),(b,c),(b,d),(a,d)]
def ribbon(points,width,offset=0):
 return parallel(points,offset-width/2)+list(reversed(parallel(points,offset+width/2)))
P=Plan(); buffer_fn=P.lib.GEOSBuffer_r;buffer_fn.restype=C.c_void_p;buffer_fn.argtypes=[C.c_void_p,C.c_void_p,C.c_double,C.c_int]
def buffer(g,d): return P.own(buffer_fn(P.context,g,d,4))
def union(gs):
 # Union via triangulated polygon collection keeps the tiny GEOS adapter local.
 return P.polygons([t for g in gs for t in P.triangles(g)])
road_full=P.polygons([ribbon(r['points'],r['width']) for r in D['roads']])
road_full=buffer(buffer(road_full,D['junction_radius_m']),-D['junction_radius_m'])
cutters=list(D['existing_ground_exclusions'])
for path in [D['block_plan'],*D['existing_block_plans']]:
 cutters += [b['footprint'] for b in json.loads((REPO/path).read_text())['blocks']]
available=P.difference(P.polygons([rect(*D['bounds'])]),P.polygons(cutters))
road=P.intersection(road_full,available)
foot=P.difference(P.intersection(buffer(road_full,D['footway_width_m']),available),road)
remaining=P.difference(P.difference(available,road),foot)
green=P.intersection(remaining,P.polygons([p['polygon'] for p in D['landscaped_reservations']]))
courts=P.difference(remaining,green)
# Stripes are inward offsets of the SAME continuous road union. Clipping comes
# after offsetting, so neither the ownership boundary nor a junction gets a cap.
yellow_full=union([P.difference(buffer(road_full,-a),buffer(road_full,-b)) for a,b in [(.15,.22),(.33,.40)]])
# July2026 views show paired edge restrictions. Keep them in the continuous
# street union, clipped only after the same kerb offsets as neighbouring roads.
# Service aisles do not receive invented markings.
# Neighbouring Lord ground is an unmarked canvas. Keep its handover clear;
# Bath/Stanley paired lines continue from the existing street parts. Other
# restrictions are deferred until a continuous dated survey.
yellow_mask=P.polygons([rect(200,374,93.5,103.5),rect(200,374,157.5,170)])
yellow=P.intersection(P.intersection(yellow_full,yellow_mask),road)
white=P.polygons([])
asphalt=P.difference(road,yellow)
materials={'asphalt':(.085,.092,.093),'paving':(.30,.27,.23),'courts':(.36,.35,.33),'green':(.16,.23,.10),'yellow':(.75,.57,.12),'white':(.72,.73,.69),'kerb':(.40,.40,.37)}
mats={}
for name,colour in materials.items():
 m=bpy.data.materials.new('Stanley '+name);m.use_nodes=True;m.diffuse_color=(*colour,1)
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=.9
 if name=='paving':
  for file,normal in [('paving.png',False),('paving-normal.png',True)]:
   im=bpy.data.images.load(str(ROOT/'textures'/file));im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im
   if normal:
    im.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
   else:m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 mats[name]=m
compiled={};collections={}
for name,lo,hi in zip(D['part_names'],D['tile_cuts'],D['tile_cuts'][1:]):
 c=bpy.data.collections.new(name+'-ground');s.collection.children.link(c);collections[name]=c
 cuts=[lo,hi]
 for a,b in zip(cuts,cuts[1:]):
  cell=P.polygons([rect(a,b,D['bounds'][2],D['bounds'][3])])
  for mat,g in [('asphalt',asphalt),('paving',foot),('courts',courts),('green',green),('yellow',yellow),('white',white)]:
   m=compiled.setdefault((name,mat),Mesh('Ground '+name+' '+mat))
   for tri in P.triangles(P.intersection(g,cell)):m.add([(x,y,0) for x,y in tri],[(0,1,2)])
P.close()
# Join road, paint, paving and cell boundaries on one plane before grading.
import southport3d.conform as cf
cf.GRID=1e-5;cf.TOLERANCE=2e-5
compiled={k:m for k,m in compiled.items() if m.faces}
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled)
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
