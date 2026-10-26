import bpy,os,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(REPO/'lib'))
from southport3d.geometry import Mesh
from southport3d.elevation import Elevations
D=json.loads((ROOT/'research/layout.json').read_text());near=Elevations(REPO/'regions/southport/elevation/marine-lake-south.json').surface('south-mainland')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';m=bpy.data.materials.new('Low tide sand');m.diffuse_color=(.54,.48,.36,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
for i,(x0,x1) in enumerate([(-600,-400),(-400,-200),(-200,-100)]):
 for j,(y0,y1) in enumerate([(930,1100),(1100,1500)]):
  name=f'sand-{i}-{j}';c=bpy.data.collections.new(name);s.collection.children.link(c);mesh=Mesh(name)
  xs=sorted({x0,x1,*[x for b in range(-600,0,100)for x in [b,b+70]if x0<x<x1]})
  def z(x,y):return near.height(x,y) if y==930 else D['intermediate_height_m'] if y==1100 else D['far_height_m']
  for x,X in zip(xs,xs[1:]):mesh.add([(x,y0,z(x,y0)),(X,y0,z(X,y0)),(X,y1,z(X,y1)),(x,y1,z(x,y1))],[(0,1,2),(0,2,3)])
  ob=mesh.finish([m],c);uv=ob.data.uv_layers.new(name='Metric')
  for li,loop in enumerate(ob.data.loops):v=ob.data.vertices[loop.vertex_index].co;uv.data[li].uv=(v.x/20,v.y/20)
s.render.engine='CYCLES';s.cycles.samples=8;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.8,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.3;l.rotation_euler=(.5,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.location=(-300,700,700);c.rotation_euler=(Vector((-300,1200,-1))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=800;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/foreshore.blend'))
