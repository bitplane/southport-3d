"""116 Lord Street: BHF facade from photographs, estimated rear/metric scale."""
import bpy,bmesh,sys,os,json,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
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
glass=material('Opaque grey glazing; no interior',(.11,.155,.18),rough=.26)
metal=material('Painted aluminium hardware',(.45,.47,.46),rough=.36)
roofmat=material('Flat weathered roof',(.25,.26,.25))
rear=material('Unsurveyed rear envelope',(.42,.40,.35))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
frame=face_matrix((D['x_near'],D['front_y'],D['base_z']),(0,1,0))
width=D['x_near']-D['x_far'];height=D['parapet_top']
def finish(mesh,part='architecture',mats=None,transform=None):
 ob=mesh.finish(mats or [stone],collections[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric repeat')
 for f in ob.data.polygons:
  axes=sorted(range(3),key=lambda i:abs(f.normal[i]))[:2]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   uv.data[li].uv=(v[axes[0]]/3.2,v[axes[1]]/4.8)
 if transform is not None:ob.matrix_world=transform
 return ob

def frontbox(name,u,z,w,h,depth=.2,out=0,mat=None,part='architecture'):
 m=Mesh(name);m.box((u,z,out),(w,h,depth));return finish(m,part,[mat or stone],frame)

def sign(name,text,u,z,w,h,bg=dark,fg=cream,out=.12,orient=None,script=False):
 m=Mesh('Sign '+name);m.box((0,0,-.02),(w,h,.04),0)
 t=text_object('Temporary lettering',text,(0,0,.015),(0,0,1),h*.60,w*.94,font,fg,extrude=.022)
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
window.box((0,(gb+gt)/2,-.12),(ww,gt-gb,.035),2)
for x in [-ww/2+.035,ww/2-.035]:window.box((x,0,.015),(.07,h,.17),0)
window.box((0,(gb+gt)/2,-.015),(.045,gt-gb,.12),0)
for z in [gb,gt]:window.box((0,z,.005),(ww,.07,.14),0)
# Tall left pane with low rail, right opening casement with high transom.
window.box((-ww/4,gb+.34,-.01),(ww/2,.035,.10),0)
window.box((ww/4,gt-.47,-.01),(ww/2,.045,.10),0)
proto=None
for i in range(D['upper_bays']):
 t=frame@Matrix.Translation((margin+ww*(i+.5),mid,0))
 if proto is None:proto=finish(window,'architecture',[cream,spandrel,glass],t)
 else:
  ob=proto.copy();ob.data=proto.data;ob.name=f'Window grid {i:02d}';collections['architecture'].objects.link(ob);ob.matrix_world=t
# Roof mass ends at an estimated rear block return; do not invent a rear shop facade.
x0,x1,yf,yb,z0=[D[k] for k in ['x_far','x_near','front_y','rear_y','base_z']];rl=D['roof_level']
m=Mesh('Envelope rear and party walls')
for x in [x0+.15,x1-.15]:m.box((x,(yf+yb-.45)/2,z0+height/2),(.30,yf-yb-.45,height))
m.box(((x0+x1)/2,yb+.15,z0+height/2),(width,.30,height));finish(m,mats=[rear])
m=Mesh('Roof slab');m.box(((x0+x1)/2,(yf+yb-.45)/2,z0+rl),(width-.6,yf-yb-.45,.20));finish(m,'roof',[roofmat])
m=Mesh('Roof coping')
for x in [x0+.15,x1-.15]:m.box((x,(yf+yb-.45)/2,z0+height+.065),(.42,yf-yb-.45,.13))
m.box(((x0+x1)/2,yb+.15,z0+height+.065),(width,.42,.13));finish(m,'roof',[roofmat])
# Only coarse low raised roof features, visible but unresolved in aerial imagery.
m=Mesh('Roof shallow service estimates')
for x,y,w,d in [(-57,-38,3.0,2.4),(-69,-43,3.2,2.2),(-58,-56,2.8,2.2)]:
 m.box((x,y,z0+rl+.22),(w,d,.30));m.box((x,y,z0+rl+.39),(w-.18,d-.18,.04))
finish(m,'roof',[roofmat])

# Three broad display/entrance zones divided by red tiled structural piers.
a,b=D['entry_left'],D['entry_right'];dep=D['entry_depth'];top=4.35
for u,w in [(.23,.46),(a-.30,.60),(b+.30,.60),(width-.23,.46)]:
 frontbox('Shop red tiled pier',u,top/2,w,top,.50,-.12,redtile,'shopfront')
 frontbox('Shop dark pier plinth',u,.28,w+.025,.56,.53,-.12,dark,'shopfront')
for start,end,count in [(.46,a-.60,3),(b+.60,width-.46,4)]:
 u=(start+end)/2;w=end-start
 frontbox('Shop display plinth',u,.28,w,.56,.30,-.17,dark,'shopfront')
 frontbox('Shop display glazing',u,(top+.56)/2,w,top-.56,.035,-.16,glass,'shopfront')
 for z in [.59,top-.025]:frontbox('Shop display rail',u,z,w,.065,.11,-.065,red,'shopfront')
 for i in range(count+1):frontbox('Shop display mullion',start+w*i/count,(top+.56)/2,.055,top-.56,.11,-.065,red,'shopfront')
# Return glazing and visible soffit around the deep recessed entrance.
for u in [a,b]:
 frontbox('Shop entrance glazed return',u,(top+.56)/2,.045,top-.56,dep,-dep/2,glass,'shopfront')
 for out in [-.06,-dep]:frontbox('Shop return jamb',u,(top+.56)/2,.07,top-.56,.08,out,red,'shopfront')
frontbox('Shop entrance soffit',(a+b)/2,top-.045,b-a,.09,dep+.12,-dep/2,stone,'shopfront')
frontbox('Shop recessed doors',(a+b)/2,1.8,b-a,2.6,.04,-dep,glass,'shopfront')
frontbox('Shop recessed transom',(a+b)/2,3.70,b-a,1.25,.04,-dep,glass,'shopfront')
for i in range(5):frontbox('Shop door jamb',a+(b-a)*i/4,2.42,.065,3.82,.09,-dep+.03,red,'shopfront')
for z in [.52,3.05,top-.02]:frontbox('Shop door rail',(a+b)/2,z,b-a,.10,.10,-dep+.03,red,'shopfront')
# Shallow dark tiled steps lie inside the entrance recess, not on a duplicate street floor.
for z,out,depth in [(.09,-.20,.40),(.25,-.53,.26),(.42,-.93,.54)]:
 frontbox('Shop entrance step',(a+b)/2,z,b-a,.18,depth,out,dark,'shopfront')
# Broad red fascias with individually authored, raised white lettering.
sign('charity name','British Heart Foundation',width*.225,4.92,width*.365,.85,red,cream,out=.08)
sign('furniture name','Furniture & Electrical',width*.745,4.92,width*.425,.85,red,cream,out=.08)
for text,z in [('WELCOME',3.98),('to BHF',3.62),('Southport',3.28)]:
 sign('entrance '+text,text,(a+b)/2,z,2.30,.36,red,cream,out=-dep+.10)
# Hand-authored curve interpretation of the visible heart / pulse emblem.
# This is source geometry, not a downloaded logo or photographic texture.
def emblem(name,u,z,size,out,bg):
 m=Mesh('Sign '+name);m.box((0,0,-.022),(size,size,.044),0)
 pts=[]
 for i in range(65):
  t=math.tau*i/64;x=16*math.sin(t)**3;y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
  pts.append((x*size*.022,(y+3)*size*.020+size*.06,.025))
 m.tube(pts,size*.022,1,6)
 m.tube([(-.44*size,-.28*size,.025),(-.30*size,-.28*size,.025),(-.24*size,-.13*size,.025),(-.18*size,-.43*size,.025),(-.10*size,-.25*size,.025),(0,-.36*size,.025),(.12*size,-.24*size,.025),(.19*size,-.40*size,.025),(.26*size,-.18*size,.025),(.32*size,-.28*size,.025),(.44*size,-.28*size,.025)],size*.018,1,6)
 return finish(m,'shopfront',[bg,cream],frame@Matrix.Translation((u,z,out)))
emblem('central heart',width*.465,4.92,.92,.08,red)
emblem('window heart',width-2.0,2.25,2.10,-.12,glass)
sign('window strapline','FIGHT FOR EVERY HEARTBEAT',width-2.0,1.08,2.70,.17,glass,cream,out=-.11)
# Small exterior hardware is omitted at District.
m=Mesh('Fine handles and soffit lights')
for u in [a+(b-a)*.25+.17,a+(b-a)*.5-.17,a+(b-a)*.5+.17,a+(b-a)*.75-.17]:
 m.tube([(u,1.25,-dep+.12),(u,1.85,-dep+.12)],.018,0,8)
for u in [a+.8,(a+b)/2,b-.8]:m.box((u,top-.10,-.55),(.15,.035,.15),0)
finish(m,'shopfront',[metal],frame)
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.70,.75,1);bg.inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/bhf.blend'))
