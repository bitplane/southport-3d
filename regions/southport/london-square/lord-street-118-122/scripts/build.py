"""118–122 Lord Street: observed facade; visually estimated dimensions/rear."""
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
stone=material('Warm grey panel cladding',(.6,.59,.54),'cladding')
pier=material('Green polished stone interpretation',(.3,.35,.29),'pier',.35)
dark=material('Black painted frames',(.025,.032,.035));glass=material('Opaque blue grey glazing',(.07,.115,.145),rough=.30)
metal=material('Painted silver aluminium',(.46,.48,.47),rough=.4)
blue=material('Sam Thai blue bands',(.018,.085,.25));cream=material('Pale sign lettering',(.87,.84,.70));roofmat=material('Weathered flat roof',(.24,.25,.24));rear=material('Rear render estimate',(.42,.41,.37));red=material('Neon border interpretation',(.55,.07,.08))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
italic=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf')
frame=face_matrix((D['x_near'],D['front_y'],D['base_z']),(0,1,0));width=D['x_near']-D['x_far'];height=D['parapet_top']

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

# Continuous facade with actual openings for all six upper lights.
lo=D['upper_sill'];hi=D['upper_head'];ww=1.05
for a,b in [(5.20,lo),(hi,height)]:frontbox('Envelope upper band',width/2,(a+b)/2,width,b-a,.4,-.2)
prev=0
for u in D['upper_centres']:
 left=u-ww/2;right=u+ww/2
 frontbox('Envelope upper pier',(prev+left)/2,(lo+hi)/2,left-prev,hi-lo,.4,-.2);prev=right
frontbox('Envelope upper end',(prev+width)/2,(lo+hi)/2,width-prev,hi-lo,.4,-.2)
window=Mesh('Window upper 0')
window.box((0,0,-.15),(ww,hi-lo,.025),1)
for x in [-ww/2+.045,ww/2-.045,0]:window.box((x,0,-.025),(.065,hi-lo,.12),0)
for z in [-(hi-lo)/2+.04,(hi-lo)/2-.04,.55]:window.box((0,z,-.025),(ww,.065,.12),0)
# Backing fills the full receiver, guarding against missed colour rays.
window.box((0,0,-.175),(ww,hi-lo,.02),0)
proto=None
for i,u in enumerate(D['upper_centres']):
 t=frame@Matrix.Translation((u,(lo+hi)/2,0))
 if proto is None:proto=finish(window,'architecture',[dark,glass],t)
 else:
  ob=proto.copy();ob.data=proto.data;collections['architecture'].objects.link(ob);ob.name='Window upper '+str(i);ob.matrix_world=t
 frontbox('Trim sill',u,lo-.035,ww+.12,.07,.16,.01,dark)
frontbox('Trim facade lower lip',width/2,5.20,width,.11,.3,.02,dark)
frontbox('Trim coping',width/2,height+.055,width+.02,.11,.56,-.18,roofmat)
# Six large-scale panel columns; actual joints are authored texture detail.
# Closed party/rear walls, not an invented finished rear facade.
x0=D['x_far'];x1=D['x_near'];yf=D['front_y'];yb=D['rear_y'];z0=D['base_z'];rl=D['roof_level']
m=Mesh('Envelope rear and party walls')
for x in [x0+.15,x1-.15]:m.box((x,(yf+yb-.4)/2,z0+height/2),(.3,yf-yb-.4,height))
m.box(((x0+x1)/2,yb+.15,z0+height/2),(width,.3,height));finish(m,mats=[rear])
m=Mesh('Roof slab');m.box(((x0+x1)/2,(yf+yb-.4)/2,z0+rl),(width-.6,yf-yb-.4,.22));finish(m,'roof',[roofmat])
m=Mesh('Roof parapet coping')
for x in [x0+.15,x1-.15]:m.box((x,(yf+yb)/2,z0+height+.055),(.45,yf-yb,.11))
m.box(((x0+x1)/2,yb+.15,z0+height+.055),(width,.45,.11));finish(m,'roof',[roofmat])
# Low features visible in aerial; exact service arrangement unverified.
m=Mesh('Roof service approximations')
for x in [-35.4,-41.4,-47.1]:
 m.box((x,-35.5,z0+rl+.19),(1.5,1.25,.28));m.box((x,-35.5,z0+rl+.35),(1.3,1.05,.06))
m.box((-46,-39,z0+rl+.45),(.40,.40,.7));finish(m,'roof',[dark])

# Signs are local XY panels so the standard selected-to-active bake can replace glyphs.
def sign(name,text,u,z,w,h,bg=dark,fg=cream,out=.12,orient=None,script=False):
 m=Mesh('Sign '+name);m.box((0,0,-.02),(w,h,.04),0)
 t=text_object('Temporary lettering',text,(0,0,.015),(0,0,1),h*.65,w*.91,italic if script else font,fg)
 bpy.ops.object.select_all(action='DESELECT');t.select_set(True);bpy.context.view_layer.objects.active=t;bpy.ops.object.convert(target='MESH')
 m.add([tuple(t.matrix_world@v.co) for v in t.data.vertices],[tuple(f.vertices) for f in t.data.polygons],1);bpy.data.objects.remove(t,do_unlink=True)
 return finish(m,'shopfront',[bg,fg],orient if orient is not None else frame@Matrix.Translation((u,z,out)))

for shop in D['shops']:
 a=shop['u0'];b=shop['u1'];w=b-a;u=(a+b)/2;name=shop['id'];sam=name=='sam-thai';mamma=name=='mamma-mia'
 # Street piers and recessed opaque glazing; no fake interior photographs.
 for pos in [a-.075,b+.075]:frontbox('Shop polished pier '+name,pos,2.6,.15,5.2,.32,-.12,pier,'shopfront')
 frontbox('Shop transom '+name,u,4.25,w,1.75,.03,-.18,glass,'shopfront')
 groundtop=3.30;doorw=1.06;doorx=b-doorw/2-.08
 frontbox('Shop display '+name,(a+doorx-doorw/2)/2,1.95,doorx-doorw/2-a,2.7,.025,-.17,glass,'shopfront')
 frontbox('Shop stallriser '+name,(a+doorx-doorw/2)/2,.36,doorx-doorw/2-a,.70,.10,-.12,blue if sam else dark,'shopfront')
 # Recess door by .28 m, with visible reveals/threshold retained at District.
 frontbox('Shop recessed door '+name,doorx,1.55,doorw,3.10,.07,-.40,glass,'shopfront')
 for px in [doorx-doorw/2,doorx+doorw/2]:frontbox('Shop door reveal '+name,px,1.55,.065,3.10,.42,-.22,dark,'shopfront')
 frontbox('Shop threshold '+name,doorx,.035,doorw,.07,.50,-.22,dark,'shopfront')
 divs=[a+.04,a+w*.38,doorx-doorw/2,b-.03]
 if name=='bugle-tap':divs=[a+.04,a+w*.24,a+w*.48,doorx-doorw/2,b-.03]
 for px in divs:frontbox('Shop mullion '+name,px,2.6,.055,5.2,.09,-.07,metal if sam else dark,'shopfront')
 for z in [.72,3.30,5.05]:frontbox('Shop rail '+name,u,z,w,.07,.10,-.06,metal if sam else dark,'shopfront')
 # Unambiguous names from references; tiny unreadable menu notices omitted.
 if sam:
  frontbox('Shop fascia stone',u,4.85,w,.66,.20,0,pier,'shopfront')
  sign(name+' fascia','Sam Thai',u,4.85,w*.70,.53,pier,blue)
  for px in [a+w*.19,a+w*.57]:sign(name+' window','Sam Thai',px,3.10,w*.36,.33,blue,cream,out=.025)
 elif mamma:
  sign(name+' high','Mamma Mia',u,4.24,w*.87,.72,dark,cream,out=-.045,script=True)
  sign(name+' small','PIZZERIA',u,4.73,w*.40,.20,dark,cream,out=-.04)
  m=Mesh('Trim neon border');m.tube([(-w*.43,-.53,0),(w*.43,-.53,0),(w*.43,.53,0),(-w*.43,.53,0),(-w*.43,-.53,0)],.018,0,6);finish(m,'shopfront',[red],frame@Matrix.Translation((u,4.32,-.02)))
 else:
  sign(name+' fascia','THE BUGLE TAP',u,3.16,w,.58,dark,cream,out=.34)
  sign(name+' subtitle','CASK AND CRAFT ALES',u,2.82,w*.53,.15,dark,cream,out=.34)
 if not sam:
  m=Mesh('Awning '+name);depth=.85 if mamma else .28
  m.add([(a,3.62,0),(b,3.62,0),(b,3.28,depth),(a,3.28,depth)],[(0,1,2,3),(3,2,1,0)])
  m.box((u,3.20,depth),(w,.16,.035));finish(m,'shopfront',[dark],frame)
  if mamma:sign(name+' awning','Mamma Mia',u,3.20,w*.65,.15,dark,cream,out=depth+.025,script=True)
 # Handles and fascia lamps vanish only at District.
 m=Mesh('Fine hardware '+name)
 m.tube([(doorx+.32,1.15,-.33),(doorx+.32,1.65,-.33)],.016,0,8)
 for px in [a+.4,b-.4]:m.box((px,4.98,.22),(.30,.07,.16))
 finish(m,'shopfront',[metal],frame)
# Projecting signs, two independently baked faces with an opaque thin core.
for u,title,bg,fg in [(5.6,'Sam Thai',dark,cream),(11.45,'Mamma Mia',blue,cream)]:
 origin=frame@Vector((u,4.25,.55))
 for side in [-1,1]:
  orient=face_matrix((origin.x+side*.045,origin.y,origin.z),(side,0,0))
  sign('projecting '+title+' '+str(side),title,0,0,.95,.52,bg,fg,orient=orient,script=title=='Mamma Mia')
 m=Mesh('Fixture sign bracket');m.box((u,4.61,.45),(.055,.055,.9));finish(m,'shopfront',[dark],frame)
# Small right-hand ATM shell observed beside Bugle, screen/text simplified.
frontbox('Fixture ATM',width-.22,1.14,.47,1.10,.24,.08,metal,'shopfront')
frontbox('Fixture ATM screen',width-.22,1.29,.30,.25,.025,.215,dark,'shopfront')
frontbox('Fixture ATM lower',width-.22,.96,.32,.09,.025,.215,dark,'shopfront')
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.70,.75,1);bg.inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/terrace.blend'))
