"""Silcock's Nevill Street exterior; registered Bath wing and low hall."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from components import rect,cut,profile
from plan import world,roofs
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];DETAIL=D['phase']=='detail';H=D['hall_width'];E=D['bath_eave']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
T=Matrix(((.00646,1,0,D['x']),(1,-.00625,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
def frame(origin,horizontal,out):
 return T@Matrix(((horizontal[0],0,out[0],origin[0]),(horizontal[1],0,out[1],origin[1]),(0,1,0,0),(0,0,0,1)))
F=frame((0,0),(1,0),(0,-1));BATH=frame((W,0),(0,1),(1,0));BACK=frame((H,L),(-1,0),(0,1))
def mat(name,col,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.8
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Dark weathered frontage brick',(.25,.15,.12),'dark-brick');redbrick=mat('Stanley red brown brick',(.43,.24,.18),'brick');cream=mat('Warm ivory paint',(.77,.74,.64));white=mat('Service wall whitewash',(.72,.71,.66),'white-brick');glass=mat('Dark window glass',(.025,.035,.04));curtain=mat('Pale curtains',(.46,.49,.46));red=mat('Burgundy awnings',(.31,.045,.035));stone=mat('Dark stone sills',(.23,.22,.18));slate=mat('Grey blue slate',(.23,.25,.28),'slate');felt=mat('Service roof felt',(.25,.27,.29));iron=mat('Black pipes',(.05,.045,.035));terra=mat('Red ridge and brick ornament',(.35,.17,.12));metal=mat('Pale service pipe',(.62,.61,.54))
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
 M=fr@Matrix.Translation((u,z,out))@Matrix.Diagonal((-1,1,1,1))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
 if M.determinant()<0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 if not ob.data.uv_layers:ob.data.uv_layers.new()

# Four ribbon-window bays and real recessed shop apertures: no invented arcade interior.
centres=[H*(i+.5)/4 for i in range(4)];bay=H/4
holes=[rect(u-bay/2+.22,4.75,u+bay/2-.22,6.25) for u in centres]
shop=[rect(u-bay/2+.24,.0,u+bay/2-.24,3.45) for u in centres]
wall('hall front',rect(0,-.60,H,D['hall_eave']),holes+shop,redbrick)
wall('Bath Nevill front',rect(H,-.60,W,E),[rect(H+.4,0,W-.4,3.35),rect(W-3.65,4.45,W-1.25,6.65),rect(W-3.65,8.16,W-1.25,10.66),rect(H+.6,4.65,H+1.6,6.6),rect(H+.6,8.2,H+1.6,10.15)],redbrick)
wall('Bath front gable',[(H,E),(W,E),((H+W)/2,D['bath_ridge'])],ma=redbrick)
# Bath elevation sequence observed in the oblique street panorama.
bath_centres=[2.2,5.1,7.75,11.5,15.9,19.8,23.5,26.2,30.1,33.7];oriels=[2.2,11.5,23.5]
bathholes=[]
for v in bath_centres:
 for z in [4.65,8.2]:bathholes.append(rect(v-.62,z,v+.62,z+1.95))
wall('Bath upper',rect(0,3.7,L,E),bathholes,redbrick,'rear',BATH)
# White closed frontage is observed: three broad filled/shuttered panels, lower brick at rear.
wall('Bath ground',rect(0,-.6,L,3.7),ma=cream,part='rear',fr=BATH)
for va,vb in [(5.7,13),(13.3,21),(21.3,29)]:
 panel('Architecture closed Bath panel',rect(va,.1,vb,3.25),.018,white,'rear',BATH)
 for z in [.9,1.7,2.5]:box('Fine shutter joint',((va+vb)/2,z,.025),(vb-va,.015,.018),stone,'rear',BATH)
# Private court envelope: observed masses only; no speculative window rows.
CF=frame((H,L),(0,-1),(-1,0));RF=frame((H,23.2),(-1,0),(0,1));END=frame((W,L),(-1,0),(0,1))
wall('Bath court exposed',rect(0,7.1,L,E),ma=redbrick,part='rear',fr=CF)
wall('Bath court lower',rect(0,-.60,L-23.2,7.1),ma=redbrick,part='rear',fr=CF)
wall('Bath rear end',[(0,-.6),(W-H,-.6),(W-H,E),((W-H)/2,D['bath_ridge']),(0,E)],ma=redbrick,part='rear',fr=END)
wall('hall rear',rect(0,-.6,H,7.1),ma=redbrick,part='rear',fr=RF)
# Party shell kept solely within this footprint; Embassy's separate surface abuts it.
PF=frame((0,0),(0,1),(-1,0));wall('hall party lower',rect(0,-.6,23.2,7.1),ma=redbrick,part='rear',fr=PF)
wall('hall party upper',[(0,7.1),(9,7.1),(9,7.65),(4.5,9),(0,7.65)],ma=redbrick,part='rear',fr=PF)
for n,p in roofs(D):
 m=Mesh('Shell roof '+n);m.add(p,[tuple(range(len(p)))]);ob=finish(m,'roof',cream if 'pale' in n else (felt if 'felt' in n else slate))
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=T.inverted()@ob.data.vertices[ob.data.loops[li].vertex_index].co
   ob.data.uv_layers.active.data[li].uv=((v.y if 'Bath' in n else v.x)/1.8,(v.x if 'Bath' in n else v.y)/1.2)
# Vertical roof step from pitch to felt, behind hall ridge.
RS=frame((H,9),(-1,0),(0,1));wall('hall roof step',rect(0,7.1,H,7.65),ma=redbrick,part='roof',fr=RS)
if DETAIL:
 for i,u in enumerate(centres):
  window(u,4.75,bay-.44,1.5,top=True)
  p=shop[i];panel('Glazing arcade dark setback',p,-.20,glass)
  for x in [p[0][0],p[1][0]]:box('Architecture shop upright',(x,1.7,-.04),(.09,3.4,.10),cream)
  box('Architecture brick pier',(i*bay+.10,5.9375,.07),(.20,3.425,.14),redbrick)
  for z in [4.25,4.43]:box('Architecture pale tube',(u,z,.18),(bay-.50,.06,.08),cream)
 # Three arcade piers, creamy broad fascia with separately legible tenant lettering.
 box('Architecture main fascia',(H/2,3.75,.16),(H,.95,.32),cream)
 letters('Ice Cream Parlour  Coffee Shop',H*4.9/22.3,3.74,H*9.5/22.3,.50,out=.33,ma=red)
 letters('Silcocks',H*20.05/22.3,3.74,H*4.1/22.3,.60,out=.33,ma=red)
 letters('AMUSEMENTS',H*15.2/22.3,3.74,H*5.6/22.3,.55,out=.33,ma=mat('Blue arcade letters',(.025,.10,.55)))
 panel('Architecture Flavours badge',[(H*.47,3.5),(H*.53,3.5),(H*.55,4.0),(H*.5,4.15),(H*.45,4.0)],.35,cream)
 letters('FLAVOURS',H*.5,3.89,1.8,.25,out=.37,ma=red)
 for u in [0,H/4,H/2,3*H/4,H]:box('Architecture cream shop pier',(u,1.65,.13),(.26,3.3,.26),cream)
 for u in [W-3.65+(2.4/2)]:
  window(u,4.45,2.4,2.15,top=False);window(u,8.2,2.4,2.45,top=False)
 for z in [4.65,8.2]:window(H+1.1,z,1.0,1.95,small=True)
 panel('Glazing corner entrance',rect(H+.4,0,W-.4,3.35),-.2,glass)
 box('Architecture corner fascia',((H+W)/2,3.7,.24),(W-H,1.0,.48),cream)
 letters('Silcocks AMUSEMENTS',(H+W)/2,3.7,W-H-.5,.43,out=.49,ma=stone)
 box('Architecture Bath entrance fascia',(2.5,3.7,.16),(5.0,1.0,.32),cream,'rear',BATH)
 letters('Silcocks AMUSEMENTS',2.5,3.7,4.7,.35,BATH,out=.33,ma=stone)
 panel('Glazing Bath entrance',rect(.55,.0,4.75,3.15),.025,glass,'rear',BATH)
 panel('Architecture Bath service door',rect(31.8,.0,33.3,2.65),.025,cream,'rear',BATH)
 for z in [.5,1.3,2.15]:box('Architecture service door panel',(32.55,z,.042),(1.15,.6,.02),white,'rear',BATH)
 for u in [H+.22,W-.22]:box('Architecture corner shop pier',(u,1.55,.22),(.44,3.1,.44),cream)
 # Shallow two-storey polygonal white oriels. Their window faces own the openings.
 def oriel(v,fr,part='rear',width=2.3):
  m=Mesh('Architecture oriel side returns')
  for sign in [-1,1]:
   x=v+sign*width/2;xb=x+sign*.15
   q=[(xb,4.35,0),(x,4.35,.42),(x,10.76,.42),(xb,10.76,0)]
   if sign<0:q.reverse()
   m.add(q,[(0,1,2,3)])
  finish(m,part,cream,fr)
  for z,h in [(4.48,2.2),(8.16,2.5)]:
   panel('Glazing oriel',rect(v-width/2+.13,z+.10,v+width/2-.13,z+h-.1),.42,curtain,part,fr)
   for x in [v-width/2,v-width/2+.13,v-width/6,v+width/6,v+width/2-.13,v+width/2]:box('Architecture oriel upright',(x,z+h/2,.43),(.07,h,.09),cream,part,fr)
   for zz in [z,z+h,z+h*.55]:box('Architecture oriel rail',(v,zz,.44),(width,.08,.10),cream,part,fr)
  box('Architecture oriel apron',(v,7.45,.36),(width,1.25,.18),cream,part,fr)
  for z in [4.35,10.76]:box('Architecture oriel cornice',(v,z,.27),(width+.18,.16,.6),cream,part,fr)
 for v in bath_centres:
  if v in oriels:oriel(v,BATH)
  else:
   for z in [4.65,8.2]:window(v,z,1.24,1.95,BATH,'rear',True)
 oriel(W-2.45,F,'frontage',2.4)
 # Bath and corner classical cornice, brick parapet ends, shallow pediment profiles.
 for fr,lo,hi in [(F,H,W),(BATH,0,L)]:
  for z,hh,dd in [(E-.2,.18,.22),(E+.02,.22,.42),(E+.20,.12,.58)]:box('Architecture classical cornice',((lo+hi)/2,z,dd/2),(hi-lo,hh,dd),stone,'roof',fr)
  for x in [lo+.4+i*.6 for i in range(int((hi-lo-.8)/.6))]:box('Fine cornice dentil',(x,E-.34,.16),(.17,.20,.25),stone,'roof',fr)
 for fr,v in [(F,W-2.45),(BATH,2.2),(BATH,33.7)]:
  p=[(v-2,11.75),(v+2,11.75),(v,12.55)];panel('Architecture pediment field',p,.28,stone,'roof',fr)
  for x1,z1,x2,z2 in [(v-2.15,11.75,v,12.65),(v,12.65,v+2.15,11.75)]:
   m=Mesh('Architecture pediment rake');m.tube([(x1,z1,.4),(x2,z2,.4)],.11,sides=4);finish(m,'roof',stone,fr)
  for side in [-1,1]:box('Architecture corner pilaster',(v+side*1.65,9.7,.10),(.23,2.1,.20),stone,'frontage' if fr==F else 'rear',fr)
 for v in [6.3,13.3,21.0,29.5,35.6]:
  m=Mesh('Fine Bath rainwater');m.tube([(v,.1,.14),(v,11.35,.14)],.045,sides=8);finish(m,'rear',cream,BATH)
 for fr,lo,hi,z in [(F,0,H,7.65),(BATH,0,L,11.6)]:box('Architecture gutter',((lo+hi)/2,z,.12),(hi-lo,.12,.22),iron,'roof',fr)
 # Short chimney blocks visibly interrupt Bath roof at either end.
 for v in [1.6,L-1.4]:box('Architecture Bath chimney',((H+W)/2,v,13.1),(1.1,.65,1.1),redbrick,'roof',T)
 # Scoped ownership partition before repeated geometry is batched.
 sys.path.insert(0,str(REPO/'tools'));from surface_owner import partition
 for _ in range(3):
  result=partition([o for c in C.values() for o in c.objects if o.type=='MESH'])
  if not result['candidate_pairs']:break
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
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.5;sun.rotation_euler=(.4,.6,.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/nevill-street-amusements.blend'))
