"""Independent section of Cambridge Arcade's pitched glazed roof."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
R=Path(__file__).resolve().parents[1];repo=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(repo/'lib'))
from southport3d.geometry import Mesh
D=json.loads((R/'research/layout.json').read_text());X,Y,Z=D['origin'];W,L=D['building_width'],D['length'];width=D['width'];e=D['eave'];ridge=D['ridge']
def world(p):
 u,v,z=p;t=v/L;q=u/W
 return (X+u+t*(2.189*(1-q)+.498*q),Y+v+(1-t)*2.862*(1-q)+t*(-.016+.694*q),Z+z)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene
c=bpy.data.collections.new('canopy');s.collection.children.link(c)
def material(name,col,alpha=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,alpha);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.6;p.inputs['Alpha'].default_value=alpha
 if alpha<1:m.surface_render_method='DITHERED'
 return m
frame=material('Painted iron and timber',(.35,.33,.29));glass=material('Translucent canopy glass',(.63,.74,.74),.24);iron=material('Decorative iron',(.12,.11,.09)); lantern=material('Warm lantern glazing',(.65,.53,.34))
def finish(m,ma):
 if not m.faces:return
 o=m.finish([ma],c);uv=o.data.uv_layers.new(name='metric')
 for f in o.data.polygons:
  for i in f.loop_indices:
   v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v.y/2,v.z/2)
 for v in o.data.vertices:v.co=world(v.co)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
def beam(m,pts,r=.04):m.tube(pts,r,sides=6)
# Slender roof glazing panes, with air and pedestrian clearance underneath.
m=Mesh('Glazing arcade panes')
for a,b in [(-width,-width/2),(-width/2,0)]:
 za=e if a in (-width,0) else ridge;zb=e if b in (-width,0) else ridge
 m.add([(a,0,za),(b,0,zb),(b,L,zb),(a,L,za)],[(0,1,2,3)])
finish(m,glass)
# Longitudinal gutters and ridge, plus pitched rafters at measured visual rhythm.
m=Mesh('Architecture arcade roof frame')
for x,z in [(-width,e),(-width/2,ridge),(0,e)]:beam(m,[(x,.08,z),(x,L,z)],.055)
n=round(L/D['rib_spacing'])
for i in range(n+1):
 v=max(.08,L*i/n);beam(m,[(-width,v,e),(-width/2,v,ridge),(0,v,e)],.045)
finish(m,frame)
# Ornamental curled spandrel ties occur intermittently; no opaque solid sheet.
m=Mesh('Fine arcade ornamental ties')
for i in range(2,n,4):
 v=L*i/n
 for side in [-1,1]:
  for offset in [.48,.90,1.32]:
   pts=[]
   for j in range(13):
    t=j/12;ang=math.pi*(.2+1.8*t);r=.20*(1-.65*t)
    pts.append((-width/2+side*(offset+r*math.cos(ang)),v,6.90-offset*.25+r*math.sin(ang)))
   beam(m,pts,.015)
  beam(m,[(-width/2,v,6.93),(-width/2+side*1.75,v,6.48)],.019)
finish(m,iron)
# Lanterns suspended from the roof ridge are visible in the 2011 panorama.
# Their metal cages remain open, with warm glazing and separate suspension rods.
m=Mesh('Fine arcade hanging lantern frame');panes=Mesh('Fine arcade hanging lantern panes')
for v in [8.0,20.0,32.0,43.0]:
 cx=-width/2;beam(m,[(cx,v,ridge),(cx,v,6.28)],.018)
 for j in range(6):
  a=math.tau*j/6;b=math.tau*(j+1)/6
  x0,y0=cx+.24*math.cos(a),v+.24*math.sin(a);x1,y1=cx+.24*math.cos(b),v+.24*math.sin(b)
  beam(m,[(x0,y0,5.72),(x0,y0,6.18)],.018);beam(m,[(x0,y0,5.72),(x1,y1,5.72)],.018);beam(m,[(x0,y0,6.18),(x1,y1,6.18)],.018)
  panes.add([(x0,y0,5.72),(x1,y1,5.72),(x1,y1,6.18),(x0,y0,6.18)],[(0,1,2,3)])
 m.lathe((cx,v),[(6.18,.24),(6.30,.10),(6.38,.025)],segments=6)
finish(m,iron);finish(panes,lantern)
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.0;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.render.engine='CYCLES';s.cycles.samples=16
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2;sun.rotation_euler=(.4,-.6,-.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='PERSP';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/canopy.blend'))
