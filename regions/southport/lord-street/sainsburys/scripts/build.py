"""Sainsbury's St George's Place: modern brick frontage and cast-iron canopy."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from components import rect,roundtop,wall,ring,column,bracket
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('frontage','canopy','roof-service'):
 C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
world=Matrix.Translation((*D['origin_site_xy'],D['base_z']))@Matrix.Rotation(math.radians(D['local_rotation_degrees']),4,'Z')
W=D['width'];DEP=D['depth'];MW=D['main_front_width'];PH=D['front_parapet'];LH=D['church_wing_parapet'];RH=D['rear_parapet']

def mat(name,rgb,texture=None,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'));m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Warm red brick',(.25,.072,.035),'brick');slate=mat('Dark grey slate',(.08,.085,.082),'slate')
panel=mat('Pebbled spandrel',(.376,.279,.191),'spandrel');roofmat=mat('Pale flat roof membrane',(.533,.521,.456),'roof')
white=mat('Painted ivory ironwork',(.79,.80,.74),rough=.52);black=mat('Black iron column bases',(.025,.029,.026),rough=.58)
glass=mat('Window blue grey opaque glass',(.22,.30,.31),rough=.32);upperglass=mat('Upper pale glazing',(.52,.59,.58),rough=.38)
orange=mat('Sainsburys orange lettering',(.88,.23,.065));dark=mat('Dark sign backing',(.045,.045,.041));metal=mat('Service steel',(.31,.36,.35),rough=.48)
canopyglass=mat('Canopy translucent glazing',(.60,.68,.65),rough=.31)
sh=canopyglass.node_tree.nodes.get('Principled BSDF');sh.inputs['Alpha'].default_value=.42
canopyglass.surface_render_method='DITHERED'
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')

def finish(m,part='frontage',mats=None,frame=None):
 ob=m.finish(mats or [brick],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric UV')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/2.95,p[axes[1]]/1.92)
 ob.matrix_world=world@(frame or Matrix.Identity(4));return ob

def box(name,p,size,part='frontage',material=None,frame=None):
 m=Mesh(name);m.box(p,size);return finish(m,part,[material or brick],frame)

proto={}
def instance(key,factory,frame,part='frontage',mats=None):
 if key not in proto:
  ob=finish(factory(),part,mats,frame);proto[key]=ob
 else:
  ob=proto[key].copy();ob.data=proto[key].data;C[part].objects.link(ob);ob.matrix_world=world@frame
 return ob

def label(name,body,origin,normal,height,width,material,part='frontage'):
 ob=text_object(name,body,origin,normal,height,width,font,material,extrude=.014,collection=C[part]);ob.matrix_world=world@ob.matrix_world
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
 # Text keeps XY in its local plane for the reduced baked receiver.
 uv=ob.data.uv_layers.new(name='Text UV')
 for f in ob.data.polygons:
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 return ob

# Front runs right-to-left in facade coordinates; retain real shop apertures.
ff=face_matrix((W,0,0),(0,1,0))
centres=[(i+.5)*W/9 for i in range(9)];shopwidth=W/9-.58
holes=[]
for u in centres:holes.append([(x+u,z) for x,z in roundtop(shopwidth,.12,4.08,.92)])
# Nine tall projecting upper bays belong to the larger right-hand block.
upperx=[2.6+i*(MW-5.2)/8 for i in range(9)]
for x in upperx:holes.append([(u+W-x,z) for u,z in roundtop(1.52,5.7,12.75,.76)])
lowx=[MW+5.2+i*1.55 for i in range(4)]
for x in lowx:holes.append([(u+W-x,z) for u,z in roundtop(.88,6.0,9.65,.44)])
poly=[(0,0),(W,0),(W,PH),(W-MW,PH),(W-MW,LH),(0,LH)]
finish(wall('Envelope stepped front lower',rect(0,0,W,LH),holes),frame=ff)
finish(wall('Envelope stepped front upper',rect(W-MW,LH,W,PH),holes),frame=ff)
# Shop glass backed by a muted opaque colour; no invented shop interior.
for i,u in enumerate(centres):
 af=ff@Matrix.Translation((u,0,0))
 instance('shop-ring',lambda:ring('Window shop rounded frame',shopwidth,.12,4.08,.92,.075,.06),af,mats=[white])
 m=Mesh('Window shop glass');m.outline(roundtop(shopwidth-.02,.14,4.06,.91),-.22,-.18)
 instance('shop-glass',lambda:m,af,mats=[glass])
 m=Mesh('Window shop mullions')
 for x in (-shopwidth/6,shopwidth/6):m.box((x,1.99,-.13),(.055,3.72,.10))
 for z in (1.2,2.65):m.box((0,z,-.13),(shopwidth-.04,.055,.10))
 instance('shop-mullions',lambda:m,af,mats=[white])
 # Low-wing main entrance and second accessible glazed door leaf.
 if i in (1,7):
  for x in (-.48,.48):
   box('Door glazed entrance',(x,1.31,-.10),(.92,2.28,.08),material=upperglass,frame=af)
   box('Door entrance rail',(x,1.25,-.045),(.88,.065,.08),material=white,frame=af)
  box('Door entrance transom',(0,2.57,-.035),(2.05,.22,.14),material=white,frame=af)
# Main upper bays: brick cheeks, chamfered corbel feet and two glass zones.
for i,x in enumerate(upperx):
 af=ff@Matrix.Translation((W-x,0,0))
 instance('upper-ring',lambda:ring('Window upper brick surround',1.52,5.7,12.75,.76,.18,.27),af)
 for sign in (-1,1):box('Course upper bay cheek',(sign*.86,9.12,.15),(.18,6.78,.34),frame=af)
 m=Mesh('Window upper glazing');m.outline(roundtop(1.49,5.72,12.72,.745),-.10,-.06)
 instance('upper-glass',lambda:m,af,mats=[upperglass])
 box('Window upper pebble spandrel',(0,9.14,.015),(1.50,3.55,.13),material=panel,frame=af)
 for z in (6.48,7.35,10.93,11.85):box('Window upper dark transom',(0,z,.092),(1.50,.045,.06),material=metal,frame=af)
 # Corbel courses step in toward wall; no floating single surface.
 for k in range(6):
  w=1.72+.16*k/5;dep=.10+.27*k/5
  box('Course projecting bay corbel',(0,5.15+k*.085,dep/2),(w,.082,dep),frame=af)
# Horizontal corbel band stops between projecting windows.
for a,b in zip([.05]+[x+1.02 for x in upperx],[x-1.02 for x in upperx]+[MW-.05]):
 for k in range(5):box('Course upper brick band',((a+b)/2,.035+.025*k,10.6+.095*k),(max(.08,b-a),.07+.05*k,.09))
# Church wing has four simpler tall semicircular-headed upper windows.
for x in lowx:
 af=ff@Matrix.Translation((W-x,0,0));instance('low-ring',lambda:ring('Window church wing brick arch',.88,6.0,9.65,.44,.13,.07),af)
 m=Mesh('Window church wing glazing');m.outline(roundtop(.86,6.02,9.63,.43),-.17,-.13);instance('low-glass',lambda:m,af,mats=[upperglass])
 box('Window church wing transom',(0,8.9,-.075),(.87,.05,.1),material=metal,frame=af)
# Coping caps and shallow lower moulding.
for x0,x1,h in [(0,MW,PH),(MW,W,LH)]:
 box('Course parapet coping',((x0+x1)/2,-.12,h+.06),(x1-x0,.52,.12),material=metal)
box('Course shop fascia',(W/2,.035,4.47),(W,.11,.13))
label('Lettering front high',"Sainsbury's",(5.9,.22,13.5),(0,1,0),.86,8.0,orange)
label('Lettering front entrance',"Sainsbury's",(MW+6.1,.22,5.35),(0,1,0),.64,6.0,orange)
# Outside orange information boards: only verified readable words.
for x,words in [(3.2,'Car park\nnext left'),(MW+2.0,'Food to go\nBakery\nCash machine')]:
 box('Sign orange board',(x,.12,1.55),(1.65,.12,2.5),material=orange)
 box('Sign dark inset',(x,.20,1.33),(1.48,.07,1.76),material=dark)
 label('Lettering board brand',"Sainsbury's",(x,.255,2.58),(0,1,0),.18,1.4,white)
 label('Lettering board information',words,(x,.255,1.5),(0,1,0),.42,1.22,white)

# Side and back walls: no duplicate solid box behind the detailed front.
for name,origin,normal,length in [('north',(W,-DEP,0),(1,0,0),DEP),('south',(0,0,0),(-1,0,0),DEP),('rear',(0,-DEP,0),(0,-1,0),W)]:
 frame=face_matrix(origin,normal);holes=[]
 if name=='north':
  holes=[rect(2.3,.1,3.5,2.45),rect(9.6,.1,11.4,2.45),rect(17.1,.1,20.7,3.05),rect(12.7,5.4,14.4,7.8)]
 if name=='rear':holes=[rect(1.2,.1,4.6,3.5),rect(5.5,.1,8.9,3.5)]
 finish(wall('Envelope '+name,rect(0,0,length,RH),holes),'roof-service',frame=frame)
 box('Course '+name+' parapet',(length/2,RH+.07,-.09),(length,.14,.45),'roof-service',metal,frame)
 # Brick rectangular panel relief at lower storey.
 for u in [1.0+i*4.0 for i in range(int(length/4))]:
  box('Course '+name+' panel pier',(u,2.10,.06),(.22,4.2,.13),'roof-service',brick,frame)
  if u+3.7<length:box('Course '+name+' panel lintel',(u+1.9,4.1,.06),(3.6,.16,.13),'roof-service',brick,frame)
 if name=='north':
  for u in (2.9,10.5):box('Door north service leaf',(u,1.28,-.13),(1.15,2.35,.14),'roof-service',metal,frame)
  box('Door north customer glazing',(18.9,1.57,-.12),(3.55,2.94,.15),'roof-service',glass,frame)
  for u in (17.2,18.9,20.6):box('Door north entry stiles',(u,1.57,-.025),(.08,3.02,.10),'roof-service',white,frame)
  box('Window north service glazing',(13.55,6.6,-.13),(1.67,2.37,.12),'roof-service',upperglass,frame)
  box('Window north service transom',(13.55,6.55,-.02),(1.7,.07,.12),'roof-service',metal,frame)
  box('Vent north grille',(19.2,7.25,.05),(6.6,2.9,.12),'roof-service',metal,frame)
  m=Mesh('Fitting north ventilation slats')
  for z in [5.88+i*.12 for i in range(24)]:m.box((19.2,z,.13),(6.5,.035,.09))
  finish(m,'roof-service',[black],frame)
  # Small white hood over the side entrance beside church hall.
  box('Roof side entrance hood',(18.9,3.35,1.12),(4.6,.12,2.5),'roof-service',white,frame)
  for u in (16.8,21.0):box('Canopy side entrance post',(u,1.6,2.2),(.10,3.2,.10),'roof-service',white,frame)
 if name=='rear':
  for u in (2.9,7.2):
   box('Door loading shutter',(u,1.79,-.10),(3.38,3.38,.12),'roof-service',metal,frame)
   m=Mesh('Fitting shutter slats')
   for z in [.16+i*.13 for i in range(26)]:m.box((u,z,-.02),(3.32,.025,.04))
   finish(m,'roof-service',[black],frame)
  box('Roof loading canopy',(5.0,3.85,.75),(9.7,.28,1.7),'roof-service',metal,frame)
  for u in (1.0,9.6):box('Canopy loading post',(u,1.85,1.3),(.13,3.7,.13),'roof-service',metal,frame)
  for u in (14,19,26):
   box('Vent rear rectangular',(u,3.5,.05),(1.5,.65,.13),'roof-service',metal,frame)
  label('Lettering rear high',"Sainsbury's",(29,-DEP-.16,8.5),(0,-1,0),1.25,11.2,orange,'roof-service')
# Low roof with parapet inset and rectangular access upstand at loading end.
# Carry the membrane below both front roof ranges. The shorter wing ends
# at -10.8 m; stopping the deck at -12.175 left an open slot behind it.
# Concealed overlap is below the hip shells and inside perimeter masonry.
flat_front=-.60;flat_rear=-DEP+.175
box('Roof main flat membrane',(W/2,(flat_front+flat_rear)/2,RH-.32),(W-.45,flat_front-flat_rear,.18),'roof-service',roofmat)
box('Envelope rear access upstand',(13.8,-DEP+.72,RH+.8),(5.0,1.45,2.2),'roof-service',brick)
box('Roof rear access coping',(13.8,-DEP+.72,RH+1.95),(5.15,1.55,.12),'roof-service',metal)
# Two front hipped slate ranges seen in aerial, behind stepped front parapets.
def hiproof(name,x0,x1,y0,y1,eave,ridge):
 hip=min((x1-x0)*.24,(y1-y0)*.45);yc=(y0+y1)/2
 v=[(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave),(x0+hip,yc,ridge),(x1-hip,yc,ridge),
    (x0,y0,eave-.15),(x1,y0,eave-.15),(x1,y1,eave-.15),(x0,y1,eave-.15)]
 f=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4),(6,9,8,7),(0,6,7,1),(1,7,8,2),(2,8,9,3),(3,9,6,0)]
 m=Mesh(name);m.add(v,f);finish(m,'roof-service',[slate])
 # Simple supporting walls below hip, behind facade and continuous to rear roof.
 for yy in (y0,y1):box('Envelope front roof support',((x0+x1)/2,yy,(eave+RH-.5)/2),(x1-x0,.25,max(.15,eave-RH+.5)),'roof-service',brick)
# Upper side walls beneath the front hip eaves.
for xx in (.2,MW-.25):box('Envelope main hip side support',(xx,-6.2,(PH-.45+RH-.5)/2),(.25,11.6,PH-.45-RH+.5),'roof-service',brick)
hiproof('Roof main front hip',.2,MW-.25,-12.0,-.38,PH-.45,PH+2.2)
hiproof('Roof church wing hip',MW+.2,W-.25,-10.8,-.38,LH-.28,LH+2.25)
# Aerial-visible service plant: dimensions and exact count estimated.
for x,y,w,d,h in [(8,-23,5,3,1.3),(20,-30,6,3.6,1.6),(31,-22,4,3,1.0),(28,-42,6,4,1.3),(8,-42,3,3,.8)]:
 box('Plant ventilation cabinet',(x,y,RH-.18+h/2),(w,d,h),'roof-service',metal)
 m=Mesh('Fitting plant grille')
 for xx in [x-w/2+.12+i*.18 for i in range(int((w-.24)/.18))]:m.box((xx,y-d/2-.025,RH-.18+h/2),(.045,.05,h-.15))
 finish(m,'roof-service',[black])

# Continuous white glazed street canopy and local cast-iron columns.
projection=D['canopy_projection'];columnxs=[.25+i*(W-.5)/7 for i in range(8)]
for x in columnxs:
 instance('cast-column',lambda:column('Canopy cast column'),Matrix.Translation((x,projection,0)),'canopy',[black,white])
 af=face_matrix((x,projection,0),(0,1,0));instance('knee-bracket',lambda:bracket('Canopy ornamental knee'),af,'canopy',[white])
for z in (4.34,4.79):box('Canopy front beam',(W/2,projection,z),(W,.095,.08),'canopy',white)
# Open diamond lattice retains light and sky holes even at District.
trellis=Mesh('Canopy diamond trellis')
for i in range(68):
 x=i*W/68;x1=(i+1)*W/68;mid=(x+x1)/2
 trellis.tube([(x,projection,4.35),(x1,projection,4.78)],.023,sides=5)
 trellis.tube([(x,projection,4.78),(x1,projection,4.35)],.023,sides=5)
 trellis.tube([(x,projection,4.35),(x,projection,4.78)],.024,sides=5)
finish(trellis,'canopy',[white])
# Glass roof is divided into narrow panes, with ivory rafters.
for i in range(49):
 x=i*W/48
 m=Mesh('Canopy glazing rafter');m.tube([(x,.05,5.36),(x,projection+.05,4.84)],.031,sides=6);finish(m,'canopy',[white])
 if i<48:
  x1=(i+1)*W/48;m=Mesh('Canopy translucent pane');m.add([(x+.035,.10,5.35),(x1-.035,.10,5.35),(x1-.035,projection,4.85),(x+.035,projection,4.85)],[(0,1,2,3)]);finish(m,'canopy',[canopyglass])
# Side return beams connect to the wall and prevent a floating canopy end.
for x in (.02,W-.02):
 m=Mesh('Canopy end frame');m.tube([(x,0,4.8),(x,projection,4.8),(x,0,5.38),(x,0,4.8)],.045,sides=6);finish(m,'canopy',[white])

# Block-plan registration: the rear wall is skew to the street facade.
def registered(p):
    local=world.inverted()@p
    u=local.x/W; v=-local.y/DEP
    corners=D['registration_corners']
    q=Vector(tuple((1-v)*((1-u)*corners[0][i]+u*corners[1][i])+v*((1-u)*corners[2][i]+u*corners[3][i]) for i in range(2))+(p.z,))
    return q
for ob in [o for col in C.values() for o in col.objects if o.type=='MESH']:
    old=ob.matrix_world.copy(); origin=registered(old.translation)
    # Keep a true orthogonal local facade frame for baked receiving panels.
    u=(registered(old@Vector((1,0,0)))-origin).normalized()
    v=registered(old@Vector((0,1,0)))-origin;v=(v-u*v.dot(u)).normalized()
    n=u.cross(v).normalized()
    new=Matrix(((u.x,v.x,n.x,origin.x),(u.y,v.y,n.y,origin.y),(u.z,v.z,n.z,origin.z),(0,0,0,1)))
    ob.data=ob.data.copy(); inv=new.inverted()
    for v in ob.data.vertices:v.co=inv@registered(old@v.co)
    ob.matrix_world=new;ob.data.update()
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.62,.68,.74,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
light=bpy.data.lights.new('Sun','SUN');light.energy=2.6;ob=bpy.data.objects.new('Sun',light);s.collection.objects.link(ob);ob.rotation_euler=(.6,-.4,-.6)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/sainsburys.blend'))
