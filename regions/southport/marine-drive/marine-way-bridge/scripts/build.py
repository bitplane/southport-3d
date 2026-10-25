"""Photo-researched Marine Way Bridge; pavement belongs to Marine public realm."""
import bpy,bmesh,os,sys,math
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from shapes import Faces,transform
from southport3d.geometry import Mesh
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';cols={}
for part in ['pylons','deck','fittings']:
 c=bpy.data.collections.new(part);s.collection.children.link(c);cols[part]=c
colours={'concrete':(.37,.37,.33),'cap':(.53,.56,.55),'blue':(.045,.105,.17),'dark':(.025,.035,.045),'grey':(.12,.14,.15),'white':(.78,.79,.76),'lamp':(.60,.61,.50)};mats={}
for key,col in colours.items():
 m=bpy.data.materials.new('Bridge '+key);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.8 if key=='concrete'else .5;mats[key]=m
 if key=='concrete':
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures/concrete.png'));m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
f=Faces();f.pylons();f.deck();f.stays();f.rails();f.lamps();groups={}
for row in f.items:
 category=row['name'].split()[0];key=(row['part'],row['material'],category);mesh=groups.setdefault(key,Mesh('Bridge '+row['part']+' '+category+' '+row['material']));mesh.add([transform(p)for p in row['vertices']],[tuple(range(len(row['vertices'])))])
for(part,mat,cat),mesh in groups.items():
 ob=mesh.finish([mats[mat]],cols[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=axis]
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/3.8,v[axes[1]]/4.0)
 for p in ob.data.polygons:p.use_smooth=cat in ['leg','cap','fore','back','sleeve','collar','socket','east','lamp']
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.8,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.4;l.rotation_euler=(.5,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/marine-way-bridge.blend'))
