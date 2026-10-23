"""118–122 Lord Street: observed facade; visually estimated dimensions/rear."""
import bpy,bmesh,sys,os,json,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
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
  axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(f.normal[j]))]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   uv.data[li].uv=(v[axes[0]]/(.88 if mats and any(m.name=='Observed orange rear brick' for m in mats) else .65 if mats and pier in mats else 3.2),v[axes[1]]/(.30 if mats and any(m.name=='Observed orange rear brick' for m in mats) else .65 if mats and pier in mats else 4.8))
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
# Butt-ended rails avoid coplanar overlapping frame faces.
for x in [-ww/2+.0325,ww/2-.0325,0]:window.box((x,0,-.055),(.065,hi-lo,.10),0)
for z in [-(hi-lo)/2+.0325,(hi-lo)/2-.0325,.55]:
 for x in [-ww/4,ww/4]:window.box((x,z,-.055),(ww/2-.065,.065,.10),0)
# Slim inset glazing beads and hinged casement edges, inside the coarse frame.
for x in [-ww/2+.085,-.055,.055,ww/2-.085]:window.box((x,0,-.09),(.018,hi-lo-.14,.025),0)
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
for x in [x0+.15,x1-.15]:m.box((x,(yf+yb-.1)/2,z0+height/2),(.3,yf-yb-.7,height))
finish(m,mats=[rear])
# Keep the slab behind the rear wall's inner face. Its former rear edge lay
# exactly on the external wall plane, producing a flickering strip from Glebe.
roof_back=yb+.31;roof_front=yf-.4
m=Mesh('Roof slab');m.box(((x0+x1)/2,(roof_front+roof_back)/2,z0+rl),(width-.6,roof_front-roof_back,.22));finish(m,'roof',[roofmat])
m=Mesh('Roof parapet coping')
# Butt side coping into the front/rear strips; overlapping top faces caused black flicker.
for x in [x0+.15,x1-.15]:m.box((x,(yf-.46+yb+.375)/2,z0+height+.055),(.45,yf-.46-yb-.375,.11))
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

# Each shop has a different joinery layout; do not share a generic door/window grid.
from frontage import build_frontages
build_frontages(D,frontbox,finish,sign,frame,dict(stone=stone,pier=pier,dark=dark,
 glass=glass,metal=metal,blue=blue,cream=cream,red=red),material)
# Projecting signs, two independently baked faces with an opaque thin core.
for u,title,bg,fg in [(5.6,'Sam Thai',dark,cream),(11.45,'Mamma Mia',blue,cream)]:
 origin=frame@Vector((u,4.25,.55))
 for side in [-1,1]:
  orient=face_matrix((origin.x+side*.045,origin.y,origin.z),(side,0,0))
  sign('projecting '+title+' '+str(side),'Mamma\nMia' if title=='Mamma Mia' else title,0,0,.80 if title=='Mamma Mia' else .95,.70 if title=='Mamma Mia' else .52,bg,fg,orient=orient,script=title=='Mamma Mia')
 m=Mesh('Fixture sign bracket');m.box((u,4.61,.45),(.055,.055,.9));finish(m,'shopfront',[dark],frame)
# ATM is a tall wall-mounted housing with hood, recessed controls and lower bin.
au=width-.24
frontbox('Fixture ATM tiled backing',au,1.55,.60,3.10,.12,.01,dark,'shopfront')
frontbox('Fixture ATM',au,1.12,.49,1.72,.22,.15,metal,'shopfront')
frontbox('Fixture ATM control recess',au,1.35,.39,.86,.035,.273,dark,'shopfront')
frontbox('Fixture ATM screen',au,1.60,.28,.23,.02,.296,glass,'shopfront')
frontbox('Fixture ATM lower bin',au,.49,.35,.38,.035,.274,dark,'shopfront')
m=Mesh('Fine ATM controls')
m.box((au,1.08,.31),(.27,.11,.025))
m.box((au,1.36,.31),(.25,.025,.04))
for xx in [-.17,.17]:
 for zz in [1.53,1.60,1.67]:m.box((au+xx,zz,.315),(.024,.023,.02))
for xx in [-.075,0,.075]:
 for zz in [1.05,1.09,1.13]:m.box((au+xx,zz,.332),(.045,.020,.01))
hood=[(au-.27,1.99,.03),(au+.27,1.99,.03),(au+.27,1.91,.34),(au-.27,1.91,.34)]
m.add(hood+[(x,y-.015,z) for x,y,z in hood],
      [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
finish(m,'shopfront',[metal],frame)
from service_rear import build as build_service_rear
service_brick=material('Observed orange rear brick',(.43,.25,.16),'service-brick')
white=material('White uPVC window frames',(.82,.82,.80),rough=.5)
build_service_rear(D,finish,service_brick,dark,glass,metal,cream,roofmat,white)

for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.70,.75,1);bg.inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/terrace.blend'))
