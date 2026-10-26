"""Pizza Hut, Ocean Plaza. 2019 exterior with provisional roof and rear."""
import bpy,bmesh,json,math,os,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]; REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(REPO/'regions/southport/marine-drive/frontage-placeholders/scripts')]
from southport3d.geometry import Mesh
from datum import grade
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
collections={}
for n in ('walls','roof','joinery'):
 c=bpy.data.collections.new(n);s.collection.children.link(c);collections[n]=c
base=grade(-45.6,660.6)-.25
# Entrance is on the north-east parking edge; rotate the composed features
# within the registered footprint, scaling only along its measured axes.
T=Matrix(((.9936,.1128,0,-55.41),(.1128,-.9936,0,669.959),(0,0,1,base),(0,0,0,1))) @ Matrix(((0,-17.4/20.8,0,17.4),(20.8/17.4,0,0,0),(0,0,1,0),(0,0,0,1)))
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
stone=mat('Buff blockwork',(.47,.41,.31));roof=mat('Dark grey standing seam roof',(.12,.15,.16));fascia=mat('Charcoal fascia',(.075,.09,.095));glass=mat('Dark glazing',(.075,.13,.14));frame=mat('Grey metal frames',(.35,.38,.38));red=mat('Red edges',(.56,.035,.025));wood=mat('Entrance timber',(.32,.20,.11));white=mat('Sign lettering',(.9,.88,.82))
def finish(m,part,material):
 ob=m.finish([material],collections[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.transform(T);ob.data.flip_normals();ob.data.update();uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 return ob
def quad(name,verts,part,material):
 m=Mesh(name);m.add(verts,[tuple(range(len(verts)))]);return finish(m,part,material)
def box(name,c,size,part,material):
 m=Mesh(name);m.box(c,size);return finish(m,part,material)
W=17.4;D=20.8;H=3.25
# Wall skins own only masonry; glazing and doors occupy real gaps.
def wall_front(name,y,segments):
 for i,(a,b,lo,hi,material) in enumerate(segments):
  yy=y+.12 if name=='front' and material==glass else y
  quad('Wall '+name+str(i),[(a,yy,lo),(b,yy,lo),(b,yy,hi),(a,yy,hi)],'walls',material)
wall_front('front',0,[(0,.8,0,H,stone),(.8,4.1,2.8,H,stone),(4.1,10.5,2.8,H,wood),(10.5,13.7,2.8,H,stone),(13.7,W,0,H,stone),(.8,6.2,0,.2,stone),(8.3,13.7,0,.2,stone),(.8,6.2,.2,2.8,glass),(6.2,7.1,0,2.8,wood),(7.1,8.3,2.56,2.8,glass),(8.3,13.7,.2,2.8,glass)])
wall_front('rear',D,[(0,6.3,0,H,stone),(6.3,7.4,2.2,H,stone),(7.4,14.9,0,H,stone),(14.9,16,2.2,H,stone),(16,W,0,H,stone),(6.3,7.4,0,2.2,frame),(14.9,16,0,2.2,frame)])
# Return elevations, including broad street glazing on south-west and service door on opposite side.
for side in (0,W):
 if side==0:
  segments=[(0,4,0,H,stone),(4,15.5,2.7,H,stone),(4,15.5,0,.3,stone),(4,15.5,.3,2.7,glass),(15.5,D,0,H,stone)]
 else:segments=[(0,D,0,H,stone)]
 for i,(a,b,lo,hi,m) in enumerate(segments):
  xx=side+.12 if side==0 and m==glass else side
  quad('Wall side '+str(side)+' '+str(i),[(xx,a,lo),(xx,b,lo),(xx,b,hi),(xx,a,hi)],'walls',m)
# Continuous reveals close the wall around recessed glazing.
for x in (.8,13.7):quad('Front jamb '+str(x),[(x,0,.2),(x,.12,.2),(x,.12,2.8),(x,0,2.8)],'joinery',stone)
for z in (.2,2.8):quad('Front reveal '+str(z),[(.8,0,z),(13.7,0,z),(13.7,.12,z),(.8,.12,z)],'joinery',stone)
for y in (4,15.5):quad('Side jamb '+str(y),[(0,y,.3),(.12,y,.3),(.12,y,2.7),(0,y,2.7)],'joinery',stone)
for z in (.3,2.7):quad('Side reveal '+str(z),[(0,4,z),(.12,4,z),(.12,15.5,z),(0,15.5,z)],'joinery',stone)
# Door and window frames are narrow depth-bearing members on the glazing plane.
for x in (.8,3.0,6.2,7.1,8.3,10.5,13.7):box('Frame front vertical '+str(x),(x,-.025,1.5),(.08,.10,2.52),'joinery',frame)
for z in (.2,2.8):box('Frame front horizontal '+str(z),(7.25,-.025,z),(12.9,.10,.08),'joinery',frame)
quad('Entrance door',[(7.1,.12,.2),(8.3,.12,.2),(8.3,.12,2.56),(7.1,.12,2.56)],'joinery',glass)
for y in (4,7,10,13,15.5):box('Frame side '+str(y),(-.025,y,1.5),(.10,.08,2.32),'joinery',frame)
# Low hipped roof, deep overhang and raised, sloping sign band.
outer=[(-.5,-.5,3.45),(W+.5,-.5,3.45),(W+.5,D+.5,3.45),(-.5,D+.5,3.45)]
inner=[(3.4,3.5,4.25),(14,3.5,4.25),(14,17.3,4.25),(3.4,17.3,4.25)]
top=[(4.0,4.1,5.75),(13.4,4.1,5.75),(13.4,16.7,5.75),(4.0,16.7,5.75)]
for i in range(4):
 j=(i+1)%4;quad('Roof lower '+str(i),[outer[i],outer[j],inner[j],inner[i]],'roof',roof);quad('Roof raised '+str(i),[inner[i],inner[j],top[j],top[i]],'roof',roof)
# Raised band encloses a low plant deck, visible from above.
inside=[(4.28,4.38,5.75),(13.12,4.38,5.75),(13.12,16.42,5.75),(4.28,16.42,5.75)]
low=[(4.28,4.38,4.55),(13.12,4.38,4.55),(13.12,16.42,4.55),(4.28,16.42,4.55)]
for i in range(4):
 j=(i+1)%4;quad('Roof band cap '+str(i),[top[i],top[j],inside[j],inside[i]],'roof',fascia);quad('Roof inner band '+str(i),[inside[i],inside[j],low[j],low[i]],'roof',fascia)
quad('Roof plant deck',low,'roof',roof)
for i,(x,y,w,d,h) in enumerate([(6,7,1.7,2.1,.75),(10.4,11,2.1,1.6,.85),(7.3,14.3,1.3,1.2,.6)]):box('Roof plant '+str(i),(x,y,4.55+h/2),(w,d,h),'roof',frame)
for i in range(4):
 j=(i+1)%4;a=outer[i];b=outer[j];quad('Fascia '+str(i),[(a[0],a[1],3.12),(b[0],b[1],3.12),b,a],'roof',fascia)
# Curved entry canopy, shallow barrel profile.
pts=[]
for i in range(17):
 x=4.1+i*6.4/16;z=3.37+.48*math.sin(math.pi*i/16);pts.append((x,z))
for i,((x,z),(x2,z2)) in enumerate(zip(pts,pts[1:])):
 quad('Canopy '+str(i),[(x,-1.25,z),(x2,-1.25,z2),(x2,.0,z2),(x,0,z)],'roof',roof)
 quad('Canopy fascia '+str(i),[(x,-1.25,z-.16),(x2,-1.25,z2-.16),(x2,-1.25,z2),(x,-1.25,z)],'roof',fascia)
# Roof-sign lettering follows the inclined front of the raised band. Text is observed.
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf')
def sign(name,body,x,y,z):
 curve=bpy.data.curves.new(name,'FONT');curve.body=body;curve.font=font;curve.size=1.18;curve.extrude=.015
 ob=bpy.data.objects.new(name,curve);collections['joinery'].objects.link(ob);ob.data.materials.append(white)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
 # local glyph XY maps onto the sloped front of the raised roof
 m=Matrix(((-1,0,0,x),(0,.371,-.928,y),(0,.928,.371,z),(0,0,0,1)))
 ob.data.transform(T@m);ob.data.flip_normals();ob.select_set(False)
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='Metric')
sign('Pizza Hut roof sign','Pizza Hut',12.2,3.50,4.48)
# The same legible wordmark appears on the adjacent road and service sides.
original=bpy.data.objects['Pizza Hut roof sign']
for name,m in [('Pizza Hut side sign',Matrix(((0,1,0,0),(-1,0,0,20),(0,0,1,0),(0,0,0,1)))),('Pizza Hut rear sign',Matrix(((-1,0,0,W),(0,-1,0,D),(0,0,1,0),(0,0,0,1))))]:
 ob=original.copy();ob.data=original.data.copy();ob.name=name;collections['joinery'].objects.link(ob);ob.data.transform(T@m@T.inverted())
# Red trim along the front fascia is a narrow stripe on its face.
quad('Red front edge',[(-.5,-.502,3.39),(W+.5,-.502,3.39),(W+.5,-.502,3.43),(-.5,-.502,3.43)],'joinery',red)
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.5;sun.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/pizza-hut.blend'))
