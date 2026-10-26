"""Silcock's Nevill Street exterior; registered Bath wing and low hall."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from components import rect,cut,profile,arch,ring,leaf
from plan import world,roofs
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];DETAIL=D['phase']=='detail';E=D['eave']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
T=Matrix(((0,1,0,D['x']),(-1,0,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
def frame(origin,horizontal,out):
 return T@Matrix(((horizontal[0],0,out[0],origin[0]),(horizontal[1],0,out[1],origin[1]),(0,1,0,0),(0,0,0,1)))
F=frame((0,0),(1,0),(0,-1));BATH=frame((W,0),(0,1),(1,0));BACK=frame((W,L),(-1,0),(0,1))
def mat(name,col,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.8
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Dark weathered frontage brick',(.25,.15,.12),'dark-brick');redbrick=mat('Stanley red brown brick',(.43,.24,.18),'brick');cream=mat('Warm ivory paint',(.65,.52,.32));white=mat('Service wall whitewash',(.72,.71,.66),'white-brick');glass=mat('Dark window glass',(.025,.035,.04));curtain=mat('Pale curtains',(.46,.49,.46));red=mat('Burgundy awnings',(.31,.045,.035));stone=mat('Dark stone sills',(.23,.22,.18));slate=mat('Grey blue slate',(.23,.25,.28),'slate');felt=mat('Service roof felt',(.25,.27,.29));iron=mat('Black pipes',(.05,.045,.035));terra=mat('Red ridge and brick ornament',(.35,.17,.12));metal=mat('Pale service pipe',(.62,.61,.54))
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
 p=rect(u-w/2,z,u+w/2,z+h);panel('Glazing recessed',p,-.17,curtain if (not top or w>4) else glass,part,fr)
 framepaint=terra if top and w>4 else cream
 border('Architecture window casing',p,rect(u-w/2+.065,z+.065,u+w/2-.065,z+h-.065),-.05,framepaint,part,fr)
 cols=2 if small else (6 if top and w>4 else (4 if top else 3))
 for i in range(1,cols):box('Architecture mullion',(u-w/2+w*i/cols,z+h/2,-.035),(.045,h-.13,.045),framepaint,part,fr)
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
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/'+('LiberationSerif-Italic.ttf' if ('Silcocks' in body or 'Ice Cream' in body) else 'LiberationSans-Regular.ttf'))
 ob=text_object('Architecture sign '+body,body,(0,0,0),(0,0,1),h,width,font,ma,extrude=.0015,collection=C['frontage'],fit_bounds=True)
 M=fr@Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
 if M.determinant()<0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 if not ob.data.uv_layers:ob.data.uv_layers.new()

def pointed(u,bottom,spring,rx,rise,n=24):
 p=[(u-rx,bottom),(u+rx,bottom)]
 for j in range(n+1):
  t=math.pi*j/(3*n);p.append((u-rx+2*rx*math.cos(t),spring+rise*math.sin(t)/math.sin(math.pi/3)))
 for j in range(1,n+1):
  t=math.pi*(n-j)/(3*n);p.append((u+rx-2*rx*math.cos(t),spring+rise*math.sin(t)/math.sin(math.pi/3)))
 return p
# Four bays: apertures in continuous skins; glazing and reveals own the openings.
SIDE=frame((0,L),(0,-1),(-1,0));RIGHT=frame((W,0),(0,1),(1,0));REAR=frame((W,L),(-1,0),(0,1))
bay=W/4;upper=[i*bay+bay*.30 for i in range(4)]+[i*bay+bay*.70 for i in range(4)]
upholes=[pointed(u,6.1,9.35,.60,.82,16) for u in upper]
# Shop aperture heads remain rectangular below shallow cusped stone heads.
shop=[rect(i*bay+.58,.05,(i+1)*bay-.58,4.8) for i in range(1,4)]
portal=pointed(bay/2,.0,3.25,1.25,1.55,24)
wall('Corporation front',rect(0,-.45,W,E),upholes+shop+[portal],redbrick)
sideholes=[]
for v in [2.2,5.3,8.8,12.1,16.3]:
 for z in [1.05,6.25]:sideholes.append(rect(v-.62,z,v+.62,z+(3.1 if z>5 else 3.35)))
# Court elevation runs back to front in its own facade frame.
wall('church court',rect(0,-.45,L,E),sideholes,redbrick,'rear',SIDE)
wall('Boots side',rect(0,-.45,L,9.9),ma=redbrick,part='rear',fr=RIGHT)
wall('Boots upper',rect(0,9.9,14.8,E),[rect(10.4,10.1,11.15,10.9)],redbrick,'rear',RIGHT)
wall('rear lower',rect(0,-.45,W,9.9),[rect(W-3.1,6.5,W-1.4,8.3)],redbrick,'rear',REAR)
wall('rear corner upper',rect(W-3.8,9.9,W,E),ma=redbrick,part='rear',fr=REAR)
# Side gables close the analytic roof volumes. Lower rear leaves true stepped outline.
for fr in [SIDE,RIGHT]:
 for a,b,h in [(0,7.6,14.35),(7.6,14.8,13.9)]:
  aa,bb=(L-b,L-a) if fr==SIDE else (a,b)
  wall('side roof gable',[(aa,E),(bb,E),((aa+bb)/2,h)],ma=redbrick,part='roof',fr=fr)
wall('rear corner side gable',[(0,E),(3.5,E),(1.75,12.8)],ma=redbrick,part='roof',fr=SIDE)
for n,p in roofs(D):
 m=Mesh('Shell roof '+n);m.add(p,[tuple(range(len(p)))]);finish(m,'roof',felt if 'terrace' in n else slate)
# Vertical steps around the rear lower roof.
STEP=frame((W,14.8),(-1,0),(0,1));wall('roof step',rect(0,9.9,W-3.8,E),ma=redbrick,part='roof',fr=STEP)
CS=frame((3.8,14.8),(0,1),(1,0));wall('corner step',[(0,9.9),(3.5,9.9),(3.5,E),(1.75,12.8),(0,E)],ma=redbrick,part='roof',fr=CS)
# Two central front dormers; side faces run down onto first pitch.
for i in [1,2]:
 u=(i+.5)*bay;left=u-1.87;right=u+1.87
 dh=[arch(u+off,11.65,12.62,.26,.30,12) for off in [-1.16,-.39,.39,1.16]]
 wall('front dormer',[(left,E),(right,E),(right,13.1),(u,15.0),(left,13.1)],dh,redbrick,'roof',F)
 m=Mesh('Shell dormer roof');m.add([(left,0,13.1),(u,0,15),(u,.3,15),(left,.3,13.1)],[(0,1,2,3)]);m.add([(u,0,15),(right,0,13.1),(right,.3,13.1),(u,.3,15)],[(0,1,2,3)]);finish(m,'roof',slate)
 for x in [left,right]:
  # small dormer side visible above main roof pitch
  fr=frame((x,0),(0,1),(-1,0) if x==left else (1,0))
  wall('dormer side',[(0,E),(.3,E),(.3,13.1),(0,13.1)],ma=redbrick,part='roof',fr=fr)
 if DETAIL:
  for off in [-1.16,-.39,.39,1.16]:
   p=arch(u+off,11.65,12.62,.26,.30,12);panel('Glazing dormer',p,-.15,glass,'roof')
   border('Architecture dormer stone',arch(u+off,11.58,12.62,.33,.39,12),p,.035,cream,'roof')
   for z in [12.0,12.4]:box('Fine dormer bar',(u+off,z,-.04),(.5,.025,.04),cream,'roof')
  for z in [13.15,13.6]:box('Architecture dormer course',(u,z,.07),(3.45,.14,.18),terra,'roof')
  for x,z,x2,z2 in [(left,13.1,u,15),(u,15,right,13.1)]:
   m=Mesh('Architecture dormer coping');m.tube([(x,z,.10),(x2,z2,.10)],.09,sides=4);finish(m,'roof',cream,F)
if DETAIL:
 # Major pilasters and continuous belt courses. No thin wallpaper faces.
 for i in range(5):
  u=i*bay
  for z0,z1,dep,ww in [(-.2,2.0,.35,.52),(2.0,5.55,.26,.43),(5.55,10.75,.22,.36)]:box('Architecture pilaster',(u,(z0+z1)/2,dep/2),(ww,z1-z0,dep),redbrick)
  for z in [2.05,4.5,5.6,7.2,9.3,10.7]:box('Architecture pilaster stone band',(u,z,.16),(.48,.16,.38),cream)
 for z,h,dep in [(5.05,.17,.15),(5.42,.22,.23),(5.76,.12,.18),(10.95,.20,.30),(11.27,.18,.40)]:box('Architecture frontage string',(W/2,z,dep/2),(W,h,dep),terra if z<10 else iron)
 # Upper stained glass lights. Recessed rectangular glass below cusped stone tympanum.
 for u in upper:
  p=pointed(u,6.1,9.35,.60,.82,16);panel('Glazing upper',p,-.18,mat('Warm muted stained glass',(.38,.37,.29)))
  border('Architecture upper stone surround',pointed(u,6.02,9.35,.68,.92,16),p,.035,terra)
  panel('Architecture cusped tympanum',pointed(u,9.35,9.35,.59,.80,16),-.025,cream)
  for dx in [-.55,0,.55]:box('Architecture upper mullion',(u+dx,7.69,-.07),(.055,3.15,.10),iron)
  for z in [6.15,8.95,9.32]:box('Architecture upper transom',(u,z,-.06),(1.16,.055,.10),iron)
  box('Architecture upper sill',(u,6.02,.11),(1.45,.13,.36),cream)
  # Small flat relief scallops and leaded diamonds, geometrically restrained.
  for dx in [-.34,0,.34]:
   m=Mesh('Fine tympanum scallop');ring(m,u+dx,9.52+.2*(dx==0),.14,.14,.035,.015,.025,10);finish(m,'frontage',stone,F)
  for dx in [-.36,-.18,.18,.36]:box('Fine lead upright',(u+dx,7.65,-.025),(.012,2.9,.018),iron)
  for z in [6.45+.28*k for k in range(9)]:box('Fine lead horizontal',(u,z,-.026),(1.05,.012,.018),iron)
  border('Fine brick arch',pointed(u,9.3,9.35,.95,1.19,24),pointed(u,9.3,9.35,.78,1.02,24),.10,terra)
 # Authored amber lancet pattern observed in Fitton2025 stained-glass close-up.
 gold=mat('Amber stained-glass borders',(.49,.32,.09))
 for u in upper:
  for off in [-.4125,-.1375,.1375,.4125]:
   for z in [6.5,7.9]:
    outer=pointed(u+off,z,z+.73,.125,.25,12);inner=pointed(u+off,z+.026,z+.73,.099,.215,12)
    border('Architecture stained lancet',outer,inner,-.020,gold)
  for off in [-.40,-.13,.13,.40]:
   m=Mesh('Fine stained roundel');m.tube([(u+off+.075*math.cos(math.tau*j/20),7.67+.075*math.sin(math.tau*j/20),-.019) for j in range(21)],.012,sides=4);finish(m,'frontage',gold,F)
 # Tall shop openings, subdivided transom glass and closed perforated shutters.
 for i in range(1,4):
  u=(i+.5)*bay;ww=bay-1.16
  panel('Glazing shop',rect(u-ww/2,.05,u+ww/2,4.8),-.18,glass)
  box('Architecture shutter',(u,1.4,-.09),(ww-.08,2.7,.08),iron)
  for j in range(1,6):box('Architecture shop upright',(u-ww/2+ww*j/6,3.65,-.04),(.045,1.65,.065),iron)
  for z in [2.82,3.30,3.75,4.2]:box('Architecture shop transom',(u,z,-.035),(ww,.055,.08),iron)
  box('Architecture shop fascia',(u,4.55,.025),(ww,.50,.15),iron)
  box('Architecture shutter roll',(u,2.75,.07),(ww+.10,.22,.29),iron)
  for z in [.20+.10*j for j in range(25)]:box('Fine shutter slat',(u,z,-.04),(ww-.10,.025,.025),stone)
  for k in range(6):
   m=Mesh('Fine shop head cusp');ring(m,u-ww/2+.25+k*(ww-.5)/5,4.78,.19,.15,.055,.04,.04,12);finish(m,'frontage',cream,F)
 # Gothic left porch: layered pointed outline, deep jambs, carved spandrels.
 u=bay/2
 panel('Glazing porch door',portal,-.20,iron)
 for x in [u-1.35,u+1.35]:box('Architecture porch jamb',(x,1.5,.25),(.45,3.0,.72),cream)
 outer=pointed(u,3.05,3.15,1.75,2.05,32);inner=pointed(u,3.05,3.25,1.25,1.55,32)
 border('Architecture porch arch',outer,inner,.42,cream)
 border('Architecture porch spandrel',rect(u-1.75,3.1,u+1.75,5.25),outer,.31,cream)
 border('Architecture arch inner mould',pointed(u,3.15,3.25,1.36,1.67,32),inner,.49,stone)
 box('Architecture porch cornice',(u,5.27,.35),(3.8,.16,.88),cream)
 for x in [u-1.5,u+1.5]:box('Architecture porch impost',(x,3.12,.32),(.85,.17,.9),cream)
 panel('Glazing porch fanlight',pointed(u,2.6,3.15,1.16,1.4,24),-.15,curtain)
 for x in [u-.95,u,u+.95]:box('Architecture porch door stile',(x,1.3,-.07),(.08,2.55,.13),iron)
 for z in [.25,1.0,2.4]:box('Architecture porch door rail',(u,z,-.065),(1.9,.07,.14),iron)
 box('Architecture Techedia sign board',(u,2.8,.02),(2.0,.34,.10),cream);letters('Techedia',u,2.8,1.8,.26,out=.08,ma=red)
 panel('Architecture porch tablet',[(u-.55,5.35),(u+.55,5.35),(u+.55,5.9),(u,6.35),(u-.55,5.9)],.3,cream)
 box('Architecture school plaque surround',(bay-.55,2.65,.41),(.57,.78,.20),cream)
 box('Architecture school plaque',(bay-.55,2.65,.52),(.43,.62,.035),curtain)
 letters('CHRIST CHURCH',bay-.55,2.83,.38,.052,out=.543,ma=iron)
 letters('HIGHER GRADE SCHOOLS',bay-.55,2.72,.39,.045,out=.543,ma=iron)
 letters('ERECTED 1898',bay-.55,2.60,.36,.055,out=.543,ma=iron)
 # Paired curling foliage masses approximate visible carving rhythm; no invented inscription.
 for side in [-1,1]:
  for j in range(9):
   m=Mesh('Fine porch foliage');leaf(m,u+side*(1.5-.09*j),3.9+.14*j,.32,.36,side*.65,.10);finish(m,'frontage',cream,F)
 for j in range(28):
  x=.3+j*(W-.6)/27
  m=Mesh('Fine terracotta belt rosette');m.box((x,5.62,.16),(.16,.15,.04));finish(m,'frontage',terra,F)
 # Octagonal corner and gable pinnacles are conspicuous in silhouette.
 for x in [0,bay,2*bay,3*bay,W]:
  z=D['pinnacle_cap_base'][round(x/bay)]
  m=Mesh('Architecture octagonal pinnacle');m.lathe((x,0),[(E-.05,.23),(z-.15,.23)],segments=8)
  finish(m,'roof',terra,T)
  cap=Mesh('Architecture pinnacle stone cap');cap.lathe((x,0),[(z-.15,.34),(z+.10,.34),(z+.14,.26),(z+.28,.26),(z+.60,.025)],segments=8);finish(cap,'roof',cream,T)
 # Church court repeated tall windows, stone bands and rainwater stacks.
 for v in [2.2,5.3,8.8,12.1,16.3]:
  for z in [1.05,6.25]:window(v,z,1.24,3.1 if z>5 else 3.35,SIDE,'rear',True)
 for z in [2.05,5.05,5.42,5.76,9.6,10.95]:box('Architecture court string',(L/2,z,.065),(L,.12,.13),cream if z in [2.05,9.6] else terra,'rear',SIDE)
 for v in [0,3.8,7.6,11.4,14.8,L]:box('Architecture court pilaster',(v,5.6,.095),(.32,11.2,.19),redbrick,'rear',SIDE)
 window(10.775,10.1,.75,.8,RIGHT,'rear',True);window(W-2.25,6.5,1.7,1.8,REAR,'rear',True)
 for fr,v in [(F,.3),(F,W-.3),(SIDE,3.9),(SIDE,14.5)]:
  m=Mesh('Fine rainwater pipe');m.tube([(v,.1,.3),(v,10.9,.3)],.045,sides=8);finish(m,'rear',iron,fr)
 # Rooflight on the back slope of the second ridge, as observed in all rear orbits.
 m=Mesh('Architecture long rooflight');m.add([(2.0,12.0,13.40),(14.1,12.0,13.40),(14.1,13.3,12.50),(2.0,13.3,12.50)],[(0,1,2,3)]);finish(m,'roof',curtain)
# Partition coplanar contacts before batching, maintaining one owner per exposed surface.
sys.path.insert(0,str(REPO/'tools'));from surface_owner import partition
for _ in range(3):
 result=partition([o for c in C.values() for o in c.objects if o.type=='MESH'])
 if not result['candidate_pairs']:break
for o in [o for c in C.values() for o in c.objects if o.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-8 or (len(f.verts)==3 and (f.verts[1].co-f.verts[0].co).cross(f.verts[2].co-f.verts[0].co).length<1e-8)];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(o.data);bm.free()
for part,c in C.items():
 groups={}
 for ob in list(c.objects):
  if ob.type=='MESH' and not ob.name.startswith('Shell '):groups.setdefault(ob.name.split('.')[0],[]).append(ob)
 for name,obs in groups.items():
  if len(obs)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=name
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.5;sun.rotation_euler=(.4,-.6,-.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/the-cloisters.blend'))
