"""Embassy exterior. True recesses, authored hip, separate service range."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from components import rect,cut,profile
from plan import world,outline,roof
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];E=D['eave'];R=D['ridge'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
T=Matrix(((.00646,1,0,D['x']),(1,-.00625,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
# This local frame is reflected in site XY: reverse winding after transform.
F=T@face_matrix((W,0,0),(0,-1,0));SIDE=T@face_matrix((0,0,0),(-1,0,0));BACK=T@face_matrix((0,L,0),(0,1,0));PARTY=T@face_matrix((W,L,0),(1,0,0))
# face_matrix x-axis follows cross(up, normal): front +u, side -v.
# Explicit face frames: horizontal x, vertical y, outward z.
def frame(origin,horizontal,out):
 return T@Matrix(((horizontal[0],0,out[0],origin[0]),(horizontal[1],0,out[1],origin[1]),(0,1,0,0),(0,0,0,1)))
F=frame((0,0),(1,0),(0,-1));SIDE=frame((0,0),(0,-1),(-1,0));BACK=frame((W,L),(-1,0),(0,1));PARTY=frame((W,L),(0,-1),(1,0))
a,b=D['chamfer_u'],D['chamfer_v'];cw=math.hypot(a,b);CH=frame((0,b),(a/cw,-b/cw),(-b/cw,-a/cw))
def mat(name,col,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.8
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Dark weathered frontage brick',(.25,.15,.12),'dark-brick');redbrick=mat('Stanley red brown brick',(.43,.24,.18),'brick');cream=mat('Warm ivory paint',(.77,.74,.64));white=mat('Service wall whitewash',(.72,.71,.66),'white-brick');glass=mat('Dark window glass',(.11,.17,.18));curtain=mat('Pale curtains',(.46,.49,.46));red=mat('Burgundy awnings',(.31,.045,.035));stone=mat('Dark stone sills',(.23,.22,.18));slate=mat('Grey blue slate',(.23,.25,.28),'slate');felt=mat('Service roof felt',(.25,.27,.29));iron=mat('Black pipes',(.05,.045,.035));terra=mat('Red ridge and brick ornament',(.35,.17,.12));metal=mat('Pale service pipe',(.62,.61,.54))
def finish(m,part='frontage',material=brick,fr=None):
 if not m.faces:return
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();uv=ob.data.uv_layers.new(name='Metric surface')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/1.8,v[axes[1]]/.6)
 M=fr if fr is not None else T;ob.data.transform(M)
 if M.determinant()<0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 ob.data.update();return ob

def box(name,c,size,ma=cream,part='frontage',fr=None):
 m=Mesh(name);m.box(c,size);return finish(m,part,ma,F if fr is None else fr)
def panel(name,p,out,ma,part='frontage',fr=None):
 m=Mesh(name);m.add([(*v,out) for v in p],[tuple(range(len(p)))]);return finish(m,part,ma,F if fr is None else fr)
def wall(name,poly,holes=(),ma=brick,part='frontage',fr=None):
 m=Mesh('Shell '+name)
 for q in cut(poly,holes):m.add([(*v,0) for v in q],[tuple(range(len(q)))]);m.add([(*v,-.22) for v in q],[tuple(reversed(range(len(q))))])
 for q in holes:
  for A,B in zip(q,q[1:]+q[:1]):m.add([(*A,0),(*B,0),(*B,-.22),(*A,-.22)],[(0,1,2,3)])
 return finish(conform({'m':m})[0]['m'],part,ma,F if fr is None else fr)
def border(name,p,inner,out,ma=cream,part='frontage',fr=None):
 for i,q in enumerate(cut(p,[inner])):panel(name+' '+str(i),q,out,ma,part,fr)
def window(u,z,w,h,fr=F,part='frontage',small=False,top=False):
 p=rect(u-w/2,z,u+w/2,z+h);panel('Glazing recessed',p,-.17,curtain if not top else glass,part,fr)
 border('Architecture window casing',p,rect(u-w/2+.065,z+.065,u+w/2-.065,z+h-.065),-.05,cream,part,fr)
 cols=2 if small else (4 if top else 3)
 for i in range(1,cols):box('Architecture mullion',(u-w/2+w*i/cols,z+h/2,-.035),(.045,h-.13,.045),cream,part,fr)
 if not top:box('Architecture sash rail',(u,z+h*.63,-.02),(w-.13,.065,.05),cream,part,fr)
 box('Architecture sill',(u,z-.06,.08),(w+.12,.12,.32),stone,part,fr)
 if DETAIL:
  if not top:
   for i in range(1,cols*2):
    if i%2:box('Fine glazing upright',(u-w/2+w*i/(cols*2),z+h/2,-.095),(.018,h-.15,.025),cream,part,fr)
   for j in (.20,.42,.79):box('Fine glazing horizontal',(u,z+h*j,-.09),(w-.13,.018,.025),cream,part,fr)
  # Soldier arch as individual tapered brick segments; observed shallow camber.
  n=max(5,int(w/.15))
  for j in range(n):
   x=u-w/2+(j+.5)*w/n;zz=z+h+.11+.08*(1-((x-u)/(w/2))**2)
   box('Fine soldier brick',(x,zz,.045),(w/n-.012,.20,.10),terra,part,fr)

def letters(body,u,z,width,h,fr=F,out=.212,ma=cream):
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
 ob=text_object('Architecture sign '+body,body,(0,0,0),(0,0,1),h,width,font,ma,extrude=.0015,collection=C['frontage'],fit_bounds=True)
 M=fr@Matrix.Translation((u,z,out))@Matrix.Diagonal((-1,1,1,1))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
 if M.determinant()<0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 if not ob.data.uv_layers:ob.data.uv_layers.new()

frontcentres=[4.35,8.9];frontwindows=[rect(u-1.35,z,u+1.35,z+h) for u in frontcentres for z,h in [(4.45,2.25),(7.8,1.65)]]
chwin=[rect(.42,z,cw-.42,z+h) for z,h in [(4.45,2.25),(7.8,1.65)]]
sidecentres=[-5.2,-8.6,-11.8,-14.7];sideholes=[rect(u-w/2,z,u+w/2,z+h) for u,w in zip(sidecentres,[2.2,1.65,1.65,1.4]) for z,h in [(4.45,2.25),(7.8,1.65)]]
wall('front upper',rect(a,3.6,W,E),frontwindows)
wall('chamfer upper',rect(0,3.6,cw,E),chwin,fr=CH)
wall('Stanley upper',rect(-L,3.6,-b,E),sideholes,redbrick,'rear',SIDE)
wall('party',rect(0,0,L,E),ma=redbrick,part='rear',fr=PARTY)
# Rear gable is one continuous surface, service range attaches below it.
wall('rear gable',[(0,D['rear_height']),(W,D['rear_height']),(W,E),(W/2,R),(0,E)],ma=redbrick,part='rear',fr=BACK)
# Ground openings, an actual chamfer doorway and long Stanley shop window.
shops=[rect(a+.18,.27,6.5,2.88),rect(6.72,.27,W-.22,2.88)]
wall('front shop',rect(a,-.18,W,3.6),shops,cream)
for p in shops:
 panel('Glazing shop',p,-.18,glass);border('Architecture shop frame',p,[(x+(.065 if x<(p[0][0]+p[1][0])/2 else -.065),y+(.065 if y<1.5 else -.065)) for x,y in p],-.03)
 for x in [p[0][0]+(p[1][0]-p[0][0])*.30,p[0][0]+(p[1][0]-p[0][0])*.68]:box('Architecture shop upright',(x,1.57,-.015),(.06,2.53,.07))
wall('chamfer doorway',rect(0,-.18,cw,3.6),[rect(.35,.03,cw-.35,2.70)],cream,fr=CH)
panel('Glazing entrance',rect(.35,.03,cw-.35,2.70),-.20,glass,fr=CH)
border('Architecture entrance frame',rect(.35,.03,cw-.35,2.70),rect(.43,.11,cw-.43,2.62),-.05,fr=CH)
box('Architecture entrance crossrail',(cw/2,1.18,-.02),(cw-.86,.12,.08),fr=CH)
sideground=[rect(-6.3,.35,-b-.2,2.88)]+[rect(u-.64,.75,u+.64,2.55) for u in [-8.6,-11.8,-14.7]]
wall('Stanley ground',rect(-L,-.18,-b,3.6),sideground,white,'rear',SIDE)
for i,p in enumerate(sideground):panel('Glazing Stanley shop' if i==0 else 'Architecture blocked opening',p,-.13,glass if i==0 else cream,'rear',SIDE)
# Independent service continuation, stepped down at outer rear with no fictitious court windows.
service=[(L,27.0,11.6,9.4),(27.0,32.8,11.6,6.1),(32.8,35.9,5.55,4.0)]
for k,(va,vb,ww,h) in enumerate(service):
 holes=[]
 if k==0:holes=[rect(u-.62,z,u+.62,z+hh) for u in (-19.2,-22.3,-25.4) for z,hh in ((4.1,2.1),(7.1,1.45))]+[rect(-24.9,.05,-23.8,2.7),rect(-22.8,1.35,-18.4,2.85)]
 if k==1:holes=[rect(-31.4,.05,-30.2,2.65),rect(-30.0,3.7,-28.2,5.35)]
 wall('service Stanley '+str(k),rect(-vb,-.18,-va,h),holes,white if k>0 else redbrick,'rear',SIDE)
 if k==0:
  # Painted lower storey ends exactly at the brick change, no duplicate facade.
  for q in cut(rect(-vb,-.18,-va,3.6),holes):panel('Architecture service whitewash',q,.008,white,'rear',SIDE)
  for u in (-19.2,-22.3,-25.4):
   for z,hh in ((4.1,2.1),(7.1,1.45)):window(u,z,1.24,hh,SIDE,'rear',True,z>7)
  window(-20.6,1.35,4.4,1.5,SIDE,'rear',False,True)
  panel('Architecture service door',rect(-24.9,.05,-23.8,2.7),-.13,cream,'rear',SIDE)
 if k==1:
  window(-29.1,3.7,1.8,1.65,SIDE,'rear',True)
  panel('Architecture rear service door',rect(-31.4,.05,-30.2,2.65),-.13,cream,'rear',SIDE)
 m=Mesh('Shell service roof '+str(k));m.add([(0,va,h),(ww,va,h),(ww,vb,h),(0,vb,h)],[(0,1,2,3)]);finish(m,'roof',felt)
 sf=frame((ww,vb),(0,-1),(1,0));wall('service court '+str(k),rect(0,-.18,vb-va,h),ma=redbrick,part='rear',fr=sf)
 bf=frame((ww,vb),(-1,0),(0,1));wall('service end '+str(k),rect(0,-.18,ww,h),ma=redbrick,part='rear',fr=bf)
 for uu in (0,ww):box('Architecture service parapet',((uu), (va+vb)/2,h+.16),(.20,vb-va,.32),redbrick,'roof',T)
for name,p in roof(D):
 m=Mesh('Shell roof '+name);m.add(p,[tuple(range(len(p)))]);ob=finish(m,'roof',slate)
 # Metric slate courses parallel to the ridge/eaves, not world diagonal projection.
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=T.inverted()@ob.data.vertices[ob.data.loops[li].vertex_index].co
   ob.data.uv_layers.active.data[li].uv=((v.y if name in ('party','stanley') else v.x)/1.8, v.z/1.2)
if DETAIL:
 for u in frontcentres:
  window(u,4.45,2.7,2.25);window(u,7.8,2.7,1.65,top=True)
 for z,h in [(4.45,2.25),(7.8,1.65)]:window(cw/2,z,cw-.84,h,CH,small=True,top=z>7)
 for u,w in zip(sidecentres,[2.2,1.65,1.65,1.4]):
  window(u,4.45,w,2.25,SIDE,'rear',True);window(u,7.8,w,1.65,SIDE,'rear',True,True)
 # Recessed decorative diamond brick panels sit between floors only on principal bays.
 for fr,centres,width in [(F,frontcentres,2.7),(CH,[cw/2],cw-.84),(SIDE,[-5.2],2.2)]:
  for u in centres:
   panel('Architecture diamond backing',rect(u-width/2,7.05,u+width/2,7.66),.035,stone,fr=fr)
   for j in range(int(width/.48)):
    x=u-width/2+.25+j*.48
    for ang in (-.75,.75):
     m=Mesh('Architecture diamond brickwork');dx=.29*math.cos(ang);dz=.29*math.sin(ang)
     m.tube([(x-dx,7.35-dz,.09),(x+dx,7.35+dz,.09)],.055,sides=4);finish(m,material=terra,fr=fr)
   for zz in (7.0,7.70):box('Architecture brick string',(u,zz,.065),(width+.24,.095,.14),stone,fr=fr)
 # Shallow pilasters and eaves are restrained; broad brick walls remain their own surface.
 for fr,positions,hh in [(F,[a+.15,6.55,W-.12],E),(CH,[.12,cw-.12],E)]:
  for x in positions:box('Architecture brick pilaster',(x,(3.65+hh)/2,.055),(.20,hh-3.65,.11),brick,fr=fr)
 for fr,start,end in [(F,a,W),(CH,0,cw),(SIDE,-L,-b)]:
  box('Architecture eaves',((start+end)/2,E+.04,.12),(end-start,.22,.40),cream,'roof',fr)
  box('Architecture gutter',((start+end)/2,E+.19,.25),(end-start,.075,.12),cream,'roof',fr)
 for fr,start,end,label in [(F,a,W,'Silcocks  EMBASSY RESTAURANT'),(CH,0,cw,'Silcocks'),(SIDE,-6.5,-b,'EMBASSY RESTAURANT')]:
  box('Architecture fascia',((start+end)/2,3.34,.10),(end-start,.46,.20),red,fr=fr)
  for zz in (3.02,3.65):box('Architecture shop cornice',((start+end)/2,zz,.14),(end-start,.16,.32),cream,fr=fr)
  letters(label,(start+end)/2,3.33,end-start-.24,.28,fr)
  # Open-bottom awning: actual sloped cover, vertical valance and end triangles.
  m=Mesh('Architecture red awning');m.add([(start,2.99,.27),(end,2.99,.27),(end,2.55,1.0),(start,2.55,1.0)],[(0,1,2,3)]);m.add([(start,2.55,1),(end,2.55,1),(end,2.38,1),(start,2.38,1)],[(0,1,2,3)]);m.add([(start,2.99,.27),(start,2.55,1),(start,2.38,1),(start,2.38,.27)],[(0,1,2,3)]);m.add([(end,2.38,.27),(end,2.38,1),(end,2.55,1),(end,2.99,.27)],[(0,1,2,3)]);finish(m,material=red,fr=fr)
  letters('EMBASSY' if fr==CH else ('FISH & CHIPS    TAKE AWAY' if fr==F else 'EAT IN OR TAKE AWAY'),(start+end)/2,2.47,end-start-.30,.17,fr,out=1.012)
 letters('ENTRANCE',cw/2,2.78,cw-.65,.16,CH,out=.04,ma=stone)
 letters('RESTAURANT',cw/2,1.18,cw-.9,.12,CH,out=.035,ma=stone)
 # Visible Stanley pipes; irregular branches represented only where photographed.
 for u in [-6.8,-10.5,-15.4,-20.6]:
  m=Mesh('Fine Stanley drain');m.tube([(u,.18,.13),(u,6.9,.13),(u+.25,7.15,.15),(u+.25,9.7,.15)],.045,sides=8);finish(m,'rear',metal,SIDE)
 for u in [a+.25,6.58,W-.15]:
  m=Mesh('Fine front rainwater');m.tube([(u,3.75,.16),(u,E,.16)],.035,sides=8);finish(m,material=iron,fr=F)
 m=Mesh('Architecture ridge tiles');m.tube([(W/2,4.8,R+.04),(W/2,L,R+.04)],.10,sides=6);finish(m,'roof',terra)
 for end in [(a,0,E),(W,0,E),(0,b,E)]:
  m=Mesh('Architecture hip tiles');m.tube([end,(W/2,4.8,R+.04)],.08,sides=6);finish(m,'roof',terra)
# Partition contacts in cornices and repeated trim before batching.
if DETAIL:
 sys.path.insert(0,str(REPO/'tools'))
 from surface_owner import partition
 for _ in range(3):
  result=partition([o for group in C.values() for o in group.objects if o.type=='MESH'])
  if not result['candidate_pairs']:break
# Consolidate identical feature categories before baking; mesh count need not scale
# with individual glazing bars and relief bricks. Preserve shell names for audits.
for part,collection in C.items():
 groups={}
 for ob in list(collection.objects):
  if ob.type=='MESH' and not ob.name.startswith('Shell '):groups.setdefault(ob.name.split('.')[0],[]).append(ob)
 for name,obs in groups.items():
  if len(obs)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=name
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.5;sun.rotation_euler=(.4,.6,.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/embassy-restaurant.blend'))
