"""116 Lord Street: BHF facade from photographs, estimated rear/metric scale."""
import bpy,bmesh,sys,os,json,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh,face_matrix,text_object
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
collections={}
for name in ['architecture','roof','shopfront']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c

def material(name,rgb,texture=None,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
stone=material('Off-white cladding',(.73,.72,.67),'cladding')
spandrel=material('Green-grey aggregate panels',(.29,.36,.33),'spandrel')
redtile=material('Red glazed shopfront tiles',(.55,.018,.025),'red-tile',.35)
red=material('BHF sign and frame red',(.60,.012,.022),rough=.4)
cream=material('White lettering and frames',(.89,.88,.84),rough=.45)
dark=material('Polished dark plinth',(.026,.029,.031),rough=.38)
tread=material('Matte dark access tiles',(.026,.029,.031),rough=.88)
glass=material('Opaque grey glazing; no interior',(.11,.155,.18),rough=.26)
metal=material('Painted aluminium hardware',(.45,.47,.46),rough=.36)
grout=material('Dark threshold grout',(.075,.078,.077),rough=.9)
gasket=material('Dark glazing seals',(.025,.030,.028),rough=.7)
roofmat=material('Flat weathered roof',(.25,.26,.25),'roof-felt')
roofbrick=material('Roof parapet brick',(.43,.27,.20),'roof-brick')
roofcap=material('Weathered parapet coping',(.47,.49,.46))
roofpale=material('Weathered pale roof equipment',(.70,.72,.68),rough=.65)
roofrust=material('Weathered rooflight bars',(.43,.19,.10),rough=.85)
rear=material('Unsurveyed rear envelope',(.42,.40,.35))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
frame=face_matrix((D['x_near'],D['front_y'],D['base_z']),(0,1,0))
width=D['x_near']-D['x_far'];height=D['parapet_top']
def finish(mesh,part='architecture',mats=None,transform=None):
 ob=mesh.finish(mats or [stone],collections[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric repeat')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   # Glazed pier tiles are narrow vertical rectangles, not metre-wide courses.
   mat=ob.data.materials[f.material_index]
   sx,sy=(.32,1.2) if mat==redtile else (.88,.30) if mat==roofbrick else (10,10) if mat==roofmat else (3.2,2.4) if mat==stone else (3.2,4.8)
   uv.data[li].uv=(v[axes[0]]/sx,v[axes[1]]/sy)
 if transform is not None:ob.matrix_world=transform
 return ob

def frontbox(name,u,z,w,h,depth=.2,out=0,mat=None,part='architecture'):
 m=Mesh(name);m.box((u,z,out),(w,h,depth));return finish(m,part,[mat or stone],frame)

def sign(name,text,u,z,w,h,bg=dark,fg=cream,out=.12,orient=None,script=False,extrude=.022):
 m=Mesh('Sign '+name);m.box((0,0,-.02),(w,h,.04),0)
 t=text_object('Temporary lettering',text,(0,0,.002 if extrude<=.002 else .015),(0,0,1),h*.60,w*.94,font,fg,extrude=extrude)
 bpy.ops.object.select_all(action='DESELECT');t.select_set(True);bpy.context.view_layer.objects.active=t;bpy.ops.object.convert(target='MESH')
 m.add([tuple(t.matrix_world@v.co) for v in t.data.vertices],[tuple(f.vertices) for f in t.data.polygons],1);bpy.data.objects.remove(t,do_unlink=True)
 return finish(m,'shopfront',[bg,fg],orient if orient is not None else frame@Matrix.Translation((u,z,out)))

# The white surround is an open frame, not a wall hiding the window receivers.
lo=D['upper_bottom'];hi=D['upper_top'];margin=D['upper_margin'];ww=(width-2*margin)/D['upper_bays']
for a,b in [(4.35,lo),(hi,height)]:frontbox('Envelope white band',width/2,(a+b)/2,width,b-a,.45,-.225)
for u in [margin/2,width-margin/2]:frontbox('Envelope white side',u,(hi+lo)/2,margin,hi-lo,.45,-.225)
for z in [lo-.06,hi+.04]:frontbox('Trim window surround',width/2,z,width-2*margin+.20,.12,.16,.035)
frontbox('Trim fascia cornice',width/2,5.48,width,.15,.30,.10)
frontbox('Trim fascia drip',width/2,5.35,width,.055,.23,.14)
frontbox('Trim coping',width/2,height+.065,width,.13,.62,-.15,roofmat)
# One shared module: top and bottom spandrels, asymmetrical casement/transom grid.
window=Mesh('Window grid 00');h=hi-lo;mid=(lo+hi)/2;gb=D['glass_bottom']-mid;gt=D['glass_top']-mid
window.box((0,0,-.19),(ww,h,.035),2)
for a,b in [(-h/2,gb),(gt,h/2)]:window.box((0,(a+b)/2,-.085),(ww,b-a,.12),1)
# Separate left fixed light and right casement have slightly different reveals.
window.box((-ww/4,(gb+gt)/2,-.13),(ww/2,gt-gb,.035),2)
window.box((ww/4,(gb+gt)/2,-.10),(ww/2,gt-gb,.035),2)
for x in [-ww/2+.035,ww/2-.035]:window.box((x,0,.015),(.07,h,.17),0)
window.box((0,(gb+gt)/2,-.015),(.045,gt-gb,.12),0)
for z in [gb,gt]:window.box((0,z,.005),(ww,.07,.14),0)
# Tall left pane with low rail, right opening casement with high transom.
window.box((-ww/4,gb+.34,-.01),(ww/2,.035,.10),0)
window.box((ww/4,gt-.47,-.01),(ww/2,.045,.10),0)
# Thin seals and glazing beads sit in the recess, clear of primary frame faces.
for left,right,bottom,upper in [(-ww/2+.075,0,gb+.035,gb+.34),(-ww/2+.075,0,gb+.34,gt-.035),(0,ww/2-.075,gb+.035,gt-.47),(0,ww/2-.075,gt-.47,gt-.035)]:
 for x in [left+.012,right-.012]:window.box((x,(bottom+upper)/2,-.047),(.020,upper-bottom,.018),3)
 for z in [bottom+.012,upper-.012]:window.box(((left+right)/2,z,-.047),(right-left-.04,.020,.018),3)
# Spandrel retainers frame the textured panels instead of a flat exposed edge.
for a0,b0 in [(-h/2,gb),(gt,h/2)]:
 for z in [a0+.022,b0-.022]:window.box((0,z,-.005),(ww-.14,.035,.040),0)
proto=None
for i in range(D['upper_bays']):
 t=frame@Matrix.Translation((margin+ww*(i+.5),mid,0))
 if proto is None:proto=finish(window,'architecture',[cream,spandrel,glass,gasket],t)
 else:
  ob=proto.copy();ob.data=proto.data;ob.name=f'Window grid {i:02d}';collections['architecture'].objects.link(ob);ob.matrix_world=t
# Roof mass ends at an estimated rear block return; do not invent a rear shop facade.
x0,x1,yf,yb,z0=[D[k] for k in ['x_far','x_near','front_y','rear_y','base_z']];rl=D['roof_level']
m=Mesh('Envelope rear and party walls')
for x in [x0+.15]:m.box((x,(yf+yb-.45)/2,z0+rl/2),(.30,yf-yb-.45,rl))
m.box(((x0+x1)/2,yb+.15,z0+rl/2),(width-.60,.30,rl));finish(m,mats=[rear])
# Roof construction follows observed satellite forms, separately from facade.
from roof_details import build_roof
R=json.loads((ROOT/'research/roof-layout.json').read_text())
build_roof(D,R,finish,[roofmat,roofbrick,roofcap,metal,roofpale,dark,roofrust])
from service_side import build as build_service_side
build_service_side(D,R,finish,roofbrick,roofcap,dark,glass,metal,cream)

# Hand-authored curve interpretation of the visible heart / pulse emblem.
# This is source geometry, not a downloaded logo or photographic texture.
def emblem(name,u,z,size,out,bg):
 m=Mesh('Sign '+name);m.box((0,0,-.022),(size,size,.044),0)
 pts=[]
 for i in range(65):
  t=math.tau*i/64;x=16*math.sin(t)**3;y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
  pts.append((x*size*.022,(y+3)*size*.020+size*.06,.025))
 m.tube(pts,size*.022,1,6)
 pulse=[(-.44*size,-.28*size,.025),(-.30*size,-.28*size,.025),(-.24*size,-.13*size,.025),(-.18*size,-.43*size,.025),(-.10*size,-.25*size,.025),(0,-.36*size,.025),(.12*size,-.24*size,.025),(.19*size,-.40*size,.025),(.26*size,-.18*size,.025),(.32*size,-.28*size,.025),(.44*size,-.28*size,.025)]
 smooth=[]
 for k in range(len(pulse)-1):
  p0=Vector(pulse[max(0,k-1)]);p1=Vector(pulse[k]);p2=Vector(pulse[k+1]);p3=Vector(pulse[min(len(pulse)-1,k+2)])
  for j in range(8):
   t=j/8;smooth.append(tuple(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
 smooth.append(pulse[-1]);m.tube(smooth,size*.018,1,6)
 return finish(m,'shopfront',[bg,cream],frame@Matrix.Translation((u,z,out)))
from frontage import build_frontage
build_frontage(D,finish,frontbox,sign,emblem,frame,[redtile,red,cream,dark,glass,metal,stone,grout,tread],font)
sign('rear collection point','Customer Collection\nPoint',0,0,2.4,.65,red,cream,orient=face_matrix((x1+.08,yb+18.7, z0+5.0),(1,0,0)))
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.70,.75,1);bg.inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/bhf.blend'))
