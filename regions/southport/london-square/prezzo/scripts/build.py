"""Observed street elevations; rear envelope and dimensions remain estimates."""
import bpy,sys,os,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'));sys.path.insert(0,str(ROOT/'scripts'))
from southport3d.geometry import Mesh,face_matrix,text_object
from components import window,pilaster
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
C={}
for name in ['architecture','roof','shopfront']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);C[name]=c

def material(name,color,texture=None,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
stone=material('Pale weathered stone',(.57,.55,.50),'stone');trim=material('Pale painted sash',(.76,.75,.69));glass=material('Opaque blue grey glazing approximation',(.075,.12,.15),rough=.27);slate=material('Slate roof',(.12,.15,.17),'slate');lead=material('Flat roof weathering',(.17,.18,.18));dark=material('Dark entrance joinery',(.025,.027,.027));white=material('Lettering',(.86,.85,.77));red=material('Terracotta chimney pots',(.34,.12,.075));brick=material('Rear masonry estimate',(.26,.18,.14));base=material('Dark stone plinth',(.20,.21,.20))
mats=[stone,trim,glass,dark,white]

def finish(m,part='architecture',materials=None,matrix=None):
 o=m.finish(materials or [stone],C[part])
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 uv=o.data.uv_layers.new(name='Metric repeat')
 for f in o.data.polygons:
  axes=sorted(range(3),key=lambda i:abs(f.normal[i]))[:2]
  for i in f.loop_indices:
   v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v[axes[0]]/3.6,v[axes[1]]/1.8)
 if matrix is not None:o.matrix_world=matrix
 return o

prototypes={}
def instance(key,mesh,part,matrix,materials=None):
 if key not in prototypes:ob=finish(mesh,part,materials or mats,matrix);prototypes[key]=ob
 else:
  ob=prototypes[key].copy();ob.data=prototypes[key].data;C[part].objects.link(ob);ob.name=mesh.name;ob.matrix_world=matrix
 return ob

z0=D['base_z'];top=15.6
# Local facade X increases to the viewer's right, Y is height, Z points outward.
def elevation(label,a,b,centres):
 normal=Vector((b[1]-a[1],a[0]-b[0],0)).normalized();length=math.dist(a,b);frame=face_matrix((a[0],a[1],z0),normal)
 def fbox(mesh,u,y,w,h,d=.45,out=-.225):mesh.box((u,y,out),(w,h,d))
 shell=Mesh('Envelope '+label)
 levels=[(0,5.3,1.0,4.75,2.45),(5.3,9.0,6.0,8.35,1.28),(9.0,12.4,9.65,11.8,1.28),(12.4,15.6,13.1,14.7,1.28)]
 for floor,(low,high,sill,head,width) in enumerate(levels):
  if label=='London Street' and floor==0:width=3.2
  fbox(shell,length/2,(low+sill)/2,length,sill-low)
  fbox(shell,length/2,(head+high)/2,length,high-head)
  previous=0
  for u in ([2.8,10.0] if label=='London Street' and floor==0 else centres):
   if u-width/2>previous:fbox(shell,(previous+u-width/2)/2,(sill+head)/2,u-width/2-previous,head-sill)
   previous=u+width/2
   style=('shop-london' if label=='London Street' else 'shop') if floor==0 else ['','lower','middle','upper'][floor]
   matrix=frame@Matrix.Translation((u,(sill+head)/2,0))
   instance(style,window(width,head-sill,'detail','Window '+style+' '+label), 'shopfront' if floor==0 else 'architecture',matrix)
   # Stone architraves remain real geometry around the receiving window panels.
   trimmesh=Mesh('Dressings '+label)
   for x in [u-width/2-.105,u+width/2+.105]:fbox(trimmesh,x,(sill+head)/2,.15,head-sill+.25,.12,.025)
   fbox(trimmesh,u,head+.10,width+.36,.16,.20,.06)
   if floor==1:
    fbox(trimmesh,u,head+.26,.24,.35,.22,.11)
   finish(trimmesh,'architecture',[stone],frame)
  if previous<length:fbox(shell,(previous+length)/2,(sill+head)/2,length-previous,head-sill)
 finish(shell,'architecture',[stone],frame)
 # Two principal cornices with stepped profiles.
 corn=Mesh('Cornice '+label)
 for y,h,depth in [(5.20,.12,.35),(5.36,.16,.48),(5.52,.09,.58),(15.10,.13,.30),(15.30,.14,.46),(15.48,.18,.65),(15.65,.12,.76)]:fbox(corn,length/2,y,length+.08,h,depth,depth/2-.10)
 finish(corn,'architecture',[stone],frame)
 fine=Mesh('Dentils '+label)
 for u in [i*.30+.12 for i in range(int(length/.30))]:
  for y in [5.23,15.29]:fbox(fine,u,y,.13,.16,.22,.20)
 finish(fine,'architecture',[stone],frame)
 # Rusticated terminal strips, and the shop's fluted Ionic pilasters.
 quoins=Mesh('Quoins '+label)
 for u in [.25,length-.25]:
  for i in range(24):fbox(quoins,u,5.75+i*.39,.48,.35,.10,.025)
 finish(quoins,'architecture',[stone],frame)
 for u in [0]+[(a+b)/2 for a,b in zip(centres,centres[1:])]+[length]:
  instance('pilaster',pilaster('detail','Pilaster '+label),'shopfront',frame@Matrix.Translation((u,1.05,0)),[stone])
 pl=Mesh('Envelope plinth '+label);fbox(pl,length/2,.45,length,.9,.54,-.21);finish(pl,'architecture',[base],frame)
 return frame,length

front,flen=elevation('Lord Street',(-12.8,-23.4),(-32,-23.4),[2.05,5.8,9.55,13.3,17.05])
side,slen=elevation('London Street',(-9.6,-39.0),(-9.6,-26.1),[2.35,6.45,10.55])
m=Mesh('Dressings London plaque');m.box((6.45,2.65,.055),(.68,1.05,.12),0);m.box((6.45,2.65,.125),(.44,.76,.03),3);finish(m,'shopfront',mats,side)
# Chamfered entrance corner, with a true arched opening and upper windows.
a=(-9.6,-26.1);b=(-12.8,-23.4);normal=Vector((b[1]-a[1],a[0]-b[0],0)).normalized();L=math.dist(a,b);corner=face_matrix((*a,z0),normal)
m=Mesh('Envelope corner');doorw=1.65;spring=3.35;radius=doorw/2
for lo,hi in [(0,(L-doorw)/2),((L+doorw)/2,L)]:m.box(((lo+hi)/2,2.65,-.225),(hi-lo,5.3,.45))
# Fill above the semicircle with strips; preserve the curved reveal.
for i in range(32):
 x=-radius+doorw*i/32;xx=x+doorw/32;h=spring+math.sqrt(max(0,radius*radius-((x+xx)/2)**2))
 m.box((L/2+(x+xx)/2,(h+5.3)/2,-.225),(doorw/32+.001,5.3-h,.45))
finish(m,'shopfront',[stone],corner)
# Dark recessed door and arched fanlight; details kept as small authored geometry.
m=Mesh('Entrance corner');m.box((L/2,1.7,-.11),(1.58,3.4,.08),3)
pts=[(L/2+radius*math.cos(i*math.pi/32),spring+radius*math.sin(i*math.pi/32),-.06) for i in range(33)]
m.add(pts,[tuple(range(len(pts)))],3)
for x in [-.42,.42]:
 m.box((L/2+x,1.5,-.04),(.58,2.5,.04),2);m.box((L/2+x,1.48,.01),(.035,.25,.06),4)
finish(m,'shopfront',mats,corner)
arch=Mesh('Dressings entrance arch');arch.tube([(L/2+1.0*math.cos(i*math.pi/32),spring+1.0*math.sin(i*math.pi/32),.05) for i in range(33)],.085,0,8);finish(arch,'shopfront',[stone],corner)
# Corner upper wall strips around three real openings.
corner_width=1.45;corner_pier=(L-corner_width)/2
for low,high,sill,head in [(5.3,9,6,8.35),(9,12.4,9.65,11.8),(12.4,15.6,13.1,14.7)]:
 m=Mesh('Envelope corner upper')
 for x in [corner_pier/2,L-corner_pier/2]:m.box((x,(low+high)/2,-.225),(corner_pier,high-low,.45))
 for aa,bb in [(low,sill),(head,high)]:m.box((L/2,(aa+bb)/2,-.225),(corner_width,bb-aa,.45))
 finish(m,'architecture',[stone],corner)
 style='corner-'+str(low);instance(style,window(corner_width,head-sill,'detail','Window corner '+str(low)),'architecture',corner@Matrix.Translation((L/2,(sill+head)/2,0)))
m=Mesh('Quoins chamfer')
for i in range(39):
 y=.23+i*.39
 for x in [.32,L-.32]:m.box((x,y,.015),(.64,.35,.10))
finish(m,'architecture',[stone],corner)
m=Mesh('Cornice corner')
for y,h,d in [(5.2,.12,.35),(5.36,.16,.48),(5.52,.09,.58),(15.3,.14,.46),(15.48,.18,.65),(15.65,.12,.76)]:m.box((L/2,y,d/2-.1),(L+.1,h,d))
# Segmental hood over the first-floor corner window.
m.tube([(L/2+1.13*math.cos(t),8.50+.34*math.sin(t),.17) for t in [i*math.pi/32 for i in range(33)]],.09,0,8)
finish(m,'architecture',[stone],corner)
# Simple party/rear envelopes explicitly not researched as finished elevations.
m=Mesh('Envelope rear estimate');m.box((-20.8,-39.0,z0+7.8),(22.4,.45,15.6));m.box((-32,-31.2,z0+7.8),(.45,15.6,15.6));finish(m,materials=[brick])
# Mansard envelope: calibrated street silhouette, coarse unobserved rear slopes.
poly=D['footprint']
# Parallel inset edges keep the chamfer planar and every eave at the same pitch.
inner=[]
for i,p in enumerate(poly):
 before=Vector(poly[i-1]);here=Vector(p);after=Vector(poly[(i+1)%len(poly)])
 t0=(here-before).normalized();t1=(after-here).normalized()
 n0=Vector((-t0.y,t0.x));n1=Vector((-t1.y,t1.x))
 offset=(n0+n1)*(1.8/(1+n0.dot(n1)))
 inner.append(tuple(here+offset))
m=Mesh('Roof mansard')
for i,a in enumerate(poly):
 j=(i+1)%len(poly);b=poly[j];aa=inner[i];bb=inner[j]
 m.add([(a[0],a[1],z0+15.7),(b[0],b[1],z0+15.7),(bb[0],bb[1],z0+18.3),(aa[0],aa[1],z0+18.3)],[(0,1,2,3)])
m.add([(x,y,z0+18.3) for x,y in inner],[tuple(range(len(inner)))],1)
roof=finish(m,'roof',[slate,lead])
# Per-face eave/slope coordinates, independent of triangulation or world axes.
# The old dominant-axis projection turned courses vertically on the chamfer.
for f in roof.data.polygons:
 if f.material_index:continue
 tangent=Vector((-f.normal.y,f.normal.x,0)).normalized()
 for li in f.loop_indices:
  v=roof.data.vertices[roof.data.loops[li].vertex_index].co
  roof.data.uv_layers.active.data[li].uv=(v.dot(tangent)/2.4,(v.z-z0-15.7)*math.hypot(1.8,2.6)/2.6/2.4)
# Dormer cheeks, frames and flat lead caps; front and London counts corroborated.
for label,frame,centres in [('Lord',front,[2.05,5.8,9.55,13.3,17.05]),('London',side,[2.35,6.45,10.55]),('corner',corner,[L/2])]:
 for u in centres:
  t=frame@Matrix.Translation((u,17.0,-.76));m=Mesh('Roof dormer '+label)
  for xx in [-.75,.75]:m.box((xx,0,-.32),(.15,1.25,.68))
  for yy in [-.575,.575]:m.box((0,yy,-.32),(1.65,.10,.68))
  m.box((0,0,-.65),(1.65,1.25,.03));m.box((0,.68,-.28),(1.88,.13,.88));finish(m,'roof',[stone],t)
  instance('dormer',window(1.35,.9,'detail','Window dormer '+label),'roof',t@Matrix.Translation((0,0,.04)))
# Chimneys and terracotta pot groups; rear service structure is an estimated envelope.
m=Mesh('Roof service enclosure');m.box((-24,-34,z0+19.1),(4.2,3.5,1.6));finish(m,'roof',[brick])
instance('dormer',Mesh('Window rear service estimate'),'roof',face_matrix((-24,-32.10,z0+19.15),(0,1,0)))
for spec in D['chimneys']:
 x,y=spec['centre'];length=spec['length'];width=spec['width']
 matrix=Matrix.Translation((x,y,z0))@Matrix.Rotation(math.radians(spec['yaw_degrees']),4,'Z')
 m=Mesh('Roof chimney '+spec['id'])
 m.box((0,0,18.55),(length,width,2.7))
 m.box((0,0,19.91),(length+.18,width+.18,.16))
 finish(m,'roof',[stone],matrix)
 # Dark weathered coping and hollow, collared terracotta pots.
 m=Mesh('Roof coping '+spec['id']);m.box((0,0,20.005),(length+.22,width+.22,.07));finish(m,'roof',[lead],matrix)
 if spec['pots']:
  m=Mesh('Pots '+spec['id']);count=spec['pots']
  for j in range(count):
   u=(j-(count-1)/2)*(length-.30)/(count-1)
   m.lathe((u,0),[(20.04,.12),(20.14,.12),(20.16,.10),(21.12,.095),(21.15,.115),(21.22,.115),(21.22,.075),(20.96,.075)],12)
  finish(m,'roof',[red],matrix)
# One authored text prototype, projected onto a panel at distant LOD.
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
t=text_object('Temporary lettering','PREZZO',(0,0,.035),(0,0,1),.20,1.1,font,white)
bpy.context.view_layer.objects.active=t;t.select_set(True);bpy.ops.object.convert(target='MESH')
m=Mesh('Sign PREZZO');m.box((0,0,0),(1.35,.31,.025),3)
m.add([tuple(t.matrix_world@v.co) for v in t.data.vertices],[tuple(f.vertices) for f in t.data.polygons],4);bpy.data.objects.remove(t,do_unlink=True)
instance('sign',m,'shopfront',corner@Matrix.Translation((L/2,3.75,.08)))
for frame,us in [(front,[2.05,9.55,17.05]),(side,[2.8,10.0])]:
 for u in us:instance('sign',Mesh('Sign PREZZO transom'),'shopfront',frame@Matrix.Translation((u,4.40,.10)))
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.70,.75,1);bg.inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;o=bpy.data.objects.new('Sun',sun);scene.collection.objects.link(o);o.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.location=(18,5,25);cam.rotation_euler=(Vector((-20,-30,10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=36
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/prezzo.blend'))
