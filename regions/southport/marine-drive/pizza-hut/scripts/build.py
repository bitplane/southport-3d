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
stone=mat('Buff blockwork',(.47,.41,.31));roof=mat('Grey standing seam roof',(.32,.34,.34));band=mat('Dark ribbed sign band',(.105,.125,.13));fascia=mat('Charcoal fascia',(.075,.09,.095));glass=mat('Dark glazing',(.075,.13,.14));frame=mat('Grey metal frames',(.35,.38,.38));red=mat('Red edges',(.56,.035,.025));wood=mat('Entrance timber',(.32,.20,.11));wooddark=mat('Timber joint',(.16,.095,.045));seammat=mat('Roof rib shadow',(.22,.24,.24));poster=mat('Poster dark backing',(.035,.033,.029));white=mat('Sign lettering',(.9,.88,.82))
# Editable generated texture describes the visible staggered buff block courses.
tex=stone.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/blockwork.png'));tex.image.pack();stone.node_tree.links.new(tex.outputs['Color'],stone.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
def finish(m,part,material):
 ob=m.finish([material],collections[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.transform(T);ob.data.flip_normals();ob.data.update();uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/1.76,v[axes[1]]/.88) if material==stone else (v[axes[0]],v[axes[1]])
 return ob
def quad(name,verts,part,material):
 m=Mesh(name);m.add(verts,[tuple(range(len(verts)))]);return finish(m,part,material)
def box(name,c,size,part,material):
 m=Mesh(name);m.box(c,size);return finish(m,part,material)
W=17.4;D=20.8;H=3.25
# Wall skins own only masonry; glazing and doors occupy real gaps.
def wall_front(name,y,segments):
 for i,(a,b,lo,hi,material) in enumerate(segments):
  yy=y+.12 if name=='front' and material==glass else (y-.10 if name=='rear' and material==frame else y)
  quad('Wall '+name+str(i),[(a,yy,lo),(b,yy,lo),(b,yy,hi),(a,yy,hi)],'walls',material)
wall_front('front',0,[(0,.8,0,H,stone),(.8,4.1,2.8,H,stone),(4.1,10.5,2.8,H,wood),(10.5,13.7,2.8,H,stone),(13.7,W,0,H,stone),(.8,6.2,0,.2,stone),(8.3,13.7,0,.2,stone),(.8,6.2,.2,2.8,glass),(6.2,7.1,0,2.8,wood),(7.1,8.3,2.56,2.8,glass),(8.3,13.7,.2,2.8,glass)])
wall_front('rear',D,[(0,6.3,0,H,stone),(6.3,7.4,2.2,H,stone),(7.4,14.9,0,H,stone),(14.9,16,2.2,H,stone),(16,W,0,H,stone),(6.3,7.4,0,2.2,frame),(14.9,16,0,2.2,frame)])
# Return elevations, including broad street glazing on south-west and service door on opposite side.
for side in (0,W):
 if side==0:
  segments=[(0,.4,0,H,stone),(.4,8.7,2.8,H,stone),(.4,8.7,0,.3,stone),(.4,8.7,.3,2.8,glass),(8.7,10,2.35,H,stone),(8.7,10,0,2.35,glass),(10,17.8,0,H,stone),(17.8,18.65,2.2,H,stone),(17.8,18.65,0,2.2,fascia),(18.65,19,0,H,stone),(19,20.1,2.2,H,stone),(19,20.1,0,2.2,fascia),(20.1,D,0,H,stone)]
 else:segments=[(0,D,0,H,stone)]
 for i,(a,b,lo,hi,m) in enumerate(segments):
  xx=side+.12 if side==0 and m in (glass,fascia) else side
  quad('Wall side '+str(side)+' '+str(i),[(xx,a,lo),(xx,b,lo),(xx,b,hi),(xx,a,hi)],'walls',m)
# Continuous returns connect wall and recessed glazing and door planes.
for x in (.8,13.7):quad('Front jamb '+str(x),[(x,0,.2),(x,.12,.2),(x,.12,2.8),(x,0,2.8)],'joinery',stone)
for z in (.2,2.8):quad('Front reveal '+str(z),[(.8,0,z),(13.7,0,z),(13.7,.12,z),(.8,.12,z)],'joinery',stone)
for y in (.4,8.7):quad('Side jamb '+str(y),[(0,y,.3),(.12,y,.3),(.12,y,2.8),(0,y,2.8)],'joinery',stone)
for z in (.3,2.8):quad('Side reveal '+str(z),[(0,.4,z),(.12,.4,z),(.12,8.7,z),(0,8.7,z)],'joinery',stone)
for a,b in [(8.7,10),(17.8,18.65),(19,20.1)]:
 for y in ((b,) if a==8.7 else (a,b)):quad('Side door jamb '+str(y),[(0,y,0),(.12,y,0),(.12,y,2.2),(0,y,2.2)],'joinery',stone)
quad('Side door jamb 8.7 lower',[(0,8.7,0),(.12,8.7,0),(.12,8.7,.3),(0,8.7,.3)],'joinery',stone)
for a,b in [(6.3,7.4),(14.9,16)]:
 for x in (a,b):quad('Rear door jamb '+str(x),[(x,D,0),(x,D-.10,0),(x,D-.10,2.2),(x,D,2.2)],'joinery',stone)
# Detailed glazed entrance: metal perimeter, single door, transom and threshold.
for x in (.8,3,6.2,7.1,8.3,13.7):box('Frame front vertical '+str(x),(x,-.025,1.5),(.08,.10,2.52),'joinery',frame)
for z in (.2,2.8):box('Frame front horizontal '+str(z),(7.25,-.025,z),(12.9,.10,.08),'joinery',frame)
quad('Entrance door',[(7.1,.12,.2),(8.3,.12,.2),(8.3,.12,2.56),(7.1,.12,2.56)],'joinery',glass)
for x in (7.17,8.23):box('Entrance leaf stile '+str(x),(x,.065,1.36),(.055,.08,2.24),'joinery',frame)
for z in (.28,2.48):box('Entrance leaf rail '+str(z),(7.7,.065,z),(1.06,.08,.055),'joinery',frame)
box('Entrance pull handle',(7.32,-.005,1.15),(.035,.06,.52),'joinery',white)
box('Entrance threshold',(7.7,-.04,.195),(1.20,.24,.045),'joinery',frame)
# Fixed glazing has a shallow horizontal transom and a raised sill.
for x in (1.6,4.5,11.2):
 for lo,hi in ((.29,2.3425),(2.3775,2.69)):box('Frame front intermediate '+str(x)+' '+str(lo),(x,-.025,(lo+hi)/2),(.045,.08,hi-lo),'joinery',frame)
for a,b in [(.8,6.2),(8.3,13.7)]:box('Frame front transom '+str(a),((a+b)/2,-.025,2.36),(b-a,.08,.035),'joinery',frame)
for y in (.4,2.8,5.3,8.7):box('Frame side '+str(y),(-.025,y,1.55),(.10,.08,2.42),'joinery',frame)
for z in (.3,2.8):box('Frame side rail '+str(z),(-.025,4.55,z),(.10,8.3,.075),'joinery',frame)
for y in (8.7,10):box('Road door stile '+str(y),(-.025,y,1.17),(.10,.07,2.25),'joinery',frame)
box('Road door pull',(-.08,9.75,1.05),(.07,.035,.42),'joinery',white)
for y in (17.8,18.65,19,20.1):box('Road service trim '+str(y),(-.025,y,1.1),(.08,.06,2.16),'joinery',frame)
for x in (6.3,7.4,14.9,16):box('Rear service trim '+str(x),(x,D+.025,1.1),(.06,.08,2.16),'joinery',frame)
# Service features and the observed coloured menu bands have their own faces.
box('Front poster backing',(15.55,-.04,1.8),(1.65,.08,.90),'joinery',poster)
box('Rear poster backing',(10.9,D+.04,1.85),(2.05,.08,1.02),'joinery',poster)
box('Rear red menu strip',(10.25,D+.04,2.85),(11.9,.08,.23),'joinery',red)
box('Rear utility cabinet',(1.25,D+.16,.45),(1.0,.32,.90),'joinery',fascia)
box('Rear downpipe',(4.15,D+.07,1.5),(.09,.14,3),'joinery',fascia)
box('Rear wall vent',(2.5,D+.035,2.05),(.16,.07,.16),'joinery',poster)
# Red sloping street-side menu awning, with dark fascia and poster below.
quad('Road red menu awning',[(0,10,2.92),(0,17.7,2.92),(-.32,17.7,2.68),(-.32,10,2.68)],'joinery',red)
quad('Road menu valance',[(-.32,10,2.68),(-.32,17.7,2.68),(-.32,17.7,2.54),(-.32,10,2.54)],'joinery',red)
box('Road poster backing',(-.04,13.8,1.77),(.08,2.4,.95),'joinery',poster)
# Timber planks in the entrance jamb and head: fine grooves over the timber skin.
for x in [6.3,6.48,6.66,6.84,7.02]:box('Fine timber joint '+str(x),(x,-.006,1.38),(.012,.012,2.76),'joinery',wooddark)
for x in [4.3+i*.24 for i in range(26)]:box('Fine timber head joint '+str(x),(x,-.006,3.025),(.012,.012,.43),'joinery',wooddark)
# Entrance sign and hat motif are visible; fine changing promotional text is omitted.
box('Entrance marquee',(7.7,-.07,2.91),(1.42,.14,.48),'joinery',poster)
for x in (7.02,8.38):box('Marquee red vertical '+str(x),(x,-.15,2.91),(.055,.05,.48),'joinery',red)
for z in (2.69,3.13):box('Marquee red horizontal '+str(z),(7.7,-.15,z),(1.30,.05,.055),'joinery',red)
for x in [7.13+i*.18 for i in range(7)]:
 for z in (2.75,3.07):box('Fine marquee bulb '+str(x)+' '+str(z),(x,-.18,z),(.045,.025,.045),'joinery',white)
# The two visible lines on the lit sign are reproduced without inferred wording.
font_marquee=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
curve=bpy.data.curves.new('Entrance marquee lettering','FONT');curve.body='COME ON IN\nTO YOUR';curve.font=font_marquee;curve.size=.125;curve.align_x='CENTER';curve.align_y='CENTER';curve.space_line=1.05;curve.extrude=.002
ob=bpy.data.objects.new('Entrance marquee lettering',curve);collections['joinery'].objects.link(ob);ob.data.materials.append(white)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
m=Matrix(((-1,0,0,7.7),(0,0,-1,-.18),(0,1,0,2.91),(0,0,0,1)));ob.data.transform(T@m);ob.data.flip_normals();ob.select_set(False)
if not ob.data.uv_layers:ob.data.uv_layers.new(name='Metric')
# Red roof-shaped outline on the timber sign jamb, not a guessed full logo.
m=Mesh('Entrance red hat outline');m.tube([(6.18,-.085,2.84),(6.33,-.085,2.92),(6.43,-.085,3.02),(6.66,-.085,3.08),(6.84,-.085,3.02),(7.03,-.085,2.92),(6.18,-.085,2.84)],.018,sides=6);finish(m,'joinery',red)
# Slender silver canopy support against the left-hand entrance return.
box('Canopy silver support',(10.58,-.14,1.70),(.14,.28,3.0),'joinery',frame)
# Low hipped roof, deep overhang and raised, sloping sign band.
outer=[(-.5,-.5,3.45),(W+.5,-.5,3.45),(W+.5,D+.5,3.45),(-.5,D+.5,3.45)]
inner=[(3.4,3.5,4.25),(14,3.5,4.25),(14,17.3,4.25),(3.4,17.3,4.25)]
top=[(4.0,4.1,5.75),(13.4,4.1,5.75),(13.4,16.7,5.75),(4.0,16.7,5.75)]
for i in range(4):
 j=(i+1)%4;quad('Roof lower '+str(i),[outer[i],outer[j],inner[j],inner[i]],'roof',roof);quad('Roof raised '+str(i),[inner[i],inner[j],top[j],top[i]],'roof',band)
# Raised band encloses a low plant deck, visible from above.
inside=[(4.28,4.38,5.75),(13.12,4.38,5.75),(13.12,16.42,5.75),(4.28,16.42,5.75)]
low=[(4.28,4.38,4.55),(13.12,4.38,4.55),(13.12,16.42,4.55),(4.28,16.42,4.55)]
for i in range(4):
 j=(i+1)%4;quad('Roof band cap '+str(i),[top[i],top[j],inside[j],inside[i]],'roof',fascia);quad('Roof inner band '+str(i),[inside[i],inside[j],low[j],low[i]],'roof',fascia)
quad('Roof plant deck',low,'roof',roof)
for i,(x,y,w,d,h) in enumerate([(6,7,1.7,2.1,.75),(10.4,11,2.1,1.6,.85),(7.3,14.3,1.3,1.2,.6)]):box('Roof plant '+str(i),(x,y,4.55+h/2),(w,d,h),'roof',frame)
for i in range(4):
 j=(i+1)%4;a=outer[i];b=outer[j];quad('Fascia '+str(i),[(a[0],a[1],3.12),(b[0],b[1],3.12),b,a],'roof',fascia)
# Standing ribs follow the four actual sloping panels; they stand proud of the sheet.
def mix(a,b,t):return tuple(a[k]*(1-t)+b[k]*t for k in range(3))
def rib_panels(name,lo,hi,count):
 m=Mesh(name)
 for i in range(4):
  j=(i+1)%4
  for n in range(1,count):
   t=n/count;dt=.0010
   v=[mix(lo[i],lo[j],t),mix(lo[i],lo[j],t+dt),mix(hi[i],hi[j],t+dt),mix(hi[i],hi[j],t)]
   m.add([(x,y,z+.014) for x,y,z in v],[(0,1,2,3)])
 finish(m,'roof',seammat)
rib_panels('Fine lower roof standing seams',outer,inner,32)
rib_panels('Fine upper band ribs',inner,top,28)
# Narrow red fascia edge and red upper band trim are visible on each elevation.
for i in range(4):
 j=(i+1)%4;a=outer[i];b=outer[j];mid=((a[0]+b[0])/2-W/2,(a[1]+b[1])/2-D/2);l=math.hypot(*mid);dx,dy=mid[0]/l*.008,mid[1]/l*.008
 quad('Red fascia edge '+str(i),[(a[0]+dx,a[1]+dy,3.39),(b[0]+dx,b[1]+dy,3.39),(b[0]+dx,b[1]+dy,3.43),(a[0]+dx,a[1]+dy,3.43)],'joinery',red)
 a=top[i];b=top[j];quad('Red sign band cap '+str(i),[(a[0],a[1],5.755),(b[0],b[1],5.755),(b[0],b[1],5.79),(a[0],a[1],5.79)],'joinery',red)
# Curved entry canopy, shallow barrel profile.
pts=[]
for i in range(17):
 x=4.1+i*6.4/16;z=3.37+.48*math.sin(math.pi*i/16);pts.append((x,z))
for i,((x,z),(x2,z2)) in enumerate(zip(pts,pts[1:])):
 quad('Canopy '+str(i),[(x,-1.25,z),(x2,-1.25,z2),(x2,.0,z2),(x,0,z)],'roof',roof)
 quad('Canopy fascia '+str(i),[(x,-1.25,z-.20),(x2,-1.25,z2-.20),(x2,-1.25,z2),(x,-1.25,z)],'roof',fascia)
 quad('Canopy timber soffit '+str(i),[(x,-1.25,z-.20),(x,0,z-.20),(x2,0,z2-.20),(x2,-1.25,z2-.20)],'roof',wood)
 quad('Canopy red trim '+str(i),[(x,-1.258,z-.045),(x2,-1.258,z2-.045),(x2,-1.258,z2-.012),(x,-1.258,z-.012)],'joinery',red)
for x in (4.1,10.5):
 z=3.37;quad('Canopy end '+str(x),[(x,-1.25,z-.20),(x,0,z-.20),(x,0,z),(x,-1.25,z)],'roof',fascia)
for x in (4.6,5.6,6.6,7.6,8.6,9.6,10.25):
 z=3.37+.48*math.sin(math.pi*(x-4.1)/6.4)-.205
 box('Fine canopy downlight '+str(x),(x,-.8,z),(.085,.085,.025),'joinery',white)
# Roof-sign lettering follows the inclined front of the raised band. Text is observed.
# The visible script is reconstructed from the 1999 wordmark letter outlines.
# Commons describes the source as PD-textlogo; attribution and trademark are recorded.
word=json.loads((ROOT/'research/wordmark.json').read_text());xmin,ymin,xmax,ymax=word['bounds']
def sign(name,x,y,z):
 def shape(objname,material,outline,offset):
  curve=bpy.data.curves.new(objname,'CURVE');curve.dimensions='2D';curve.fill_mode='BOTH';curve.resolution_u=2;curve.extrude=.012;curve.bevel_depth=outline;curve.bevel_resolution=1
  for group in ('pizza','hut'):
   for letter in word['groups'][group]:
    for path in letter['paths']:
     if len(path)<3:continue
     sp=curve.splines.new('POLY');sp.points.add(len(path)-1)
     for p,(px,py) in zip(sp.points,path):p.co=((px-xmin)*6.2/(xmax-xmin),(py-ymin)*1.0/(ymax-ymin),0,1)
     sp.use_cyclic_u=True
  ob=bpy.data.objects.new(objname,curve);collections['joinery'].objects.link(ob);ob.data.materials.append(material)
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
  m=Matrix(((-1,0,0,x),(0,.371,-.928,y),(0,.928,.371,z),(0,0,0,1))) @ Matrix.Translation((0,0,offset))
  ob.data.transform(T@m);ob.data.flip_normals();ob.select_set(False)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='Metric')
  return ob
 shape(name+' red backing',red,.035,-.045)
 return shape(name,white,0,0)
original=sign('Pizza Hut roof sign',11.8,3.50,4.48)
# The same legible wordmark appears on the adjacent road and service sides.
for name,m in [('Pizza Hut side sign',Matrix(((0,1,0,-.1),(-1,0,0,20),(0,0,1,0),(0,0,0,1)))),('Pizza Hut rear sign',Matrix(((-1,0,0,W),(0,-1,0,D),(0,0,1,0),(0,0,0,1))))]:
 for source in (original,bpy.data.objects['Pizza Hut roof sign red backing']):
  ob=source.copy();ob.data=source.data.copy();ob.name=name+(' red backing' if source!=original else '');collections['joinery'].objects.link(ob);ob.data.transform(T@m@T.inverted())
# Red trim along the front fascia is a narrow stripe on its face.

# Keep the canopy and roof-sign sources in their respective projection groups.
for ob in list(collections['roof'].objects):
 if ob.name.startswith('Canopy '):
  collections['roof'].objects.unlink(ob);collections['joinery'].objects.link(ob)
for ob in list(collections['joinery'].objects):
 if ob.name.startswith(('Pizza Hut ', 'Red fascia edge ', 'Red sign band cap ')):
  collections['joinery'].objects.unlink(ob);collections['roof'].objects.link(ob)

s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.5;sun.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/pizza-hut.blend'))
