"""365 Lord Street: survey-scaled facade, pitched roof and deferred rear finishes."""
import json,math,os,sys,re
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,text_object,face_matrix
from southport3d.conform import conform
from components import rect,cuts,ellipse_arch,arc,moulding,beam
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('facades','roof','frontage'):
 C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,c,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough
 return m
stone=material('Red sandstone',(.23,.115,.105));darkstone=material('Weathered sandstone moulding',(.21,.095,.080))
granite=material('Polished red granite',(.30,.135,.12),.30)
# Metric authored mineral texture exports identically to glTF and bake sources.
n=granite.node_tree.nodes;links=granite.node_tree.links
tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/granite.png'));tex.image.pack()
links.new(tex.outputs['Color'],n['Principled BSDF'].inputs['Base Color'])
var=[material('Sandstone ashlar '+str(i),(.215+i*.006,.101+i*.005,.094+i*.004)) for i in range(7)]
white=material('Ivory painted frames',(.80,.80,.72),.5);glass=material('Opaque blue grey glazing',(.073,.12,.14),.24)
gold=material('Gold painted security doors',(.40,.31,.115),.44);goldlight=material('Crown gold',(.65,.49,.18),.4)
roofmat=material('Blue grey slate',(.105,.13,.15));lead=material('Lead roof edges',(.19,.21,.22));rear=material('Provisional rear masonry',(.37,.31,.25));black=material('Recess shadow',(.025,.03,.03));blind=material('Cream upper blinds',(.51,.50,.43))
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
F=T@face_matrix((0,0,0),(0,-1,0))
def finish(m,part='facades',mat=None,frame=None):
 if m.name.startswith('Wall '):m=conform({'wall':m})[0]['wall']
 ob=m.finish(mat if isinstance(mat,list) else [mat or stone],C[part])
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 frame=frame if frame is not None else T;ob['face_frame']=[list(row) for row in frame];ob.data.transform(frame)
 return ob

def box(name,c,size,part='facades',mat=None,frame=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,mat,frame)
def text(name,body,u,z,out,height,width,mat=white):
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
 ob=text_object('Sign '+name,body,(0,0,0),(0,0,1),height,width,font,mat,extrude=.006,collection=C['frontage'],fit_bounds=True)
 local=Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(F@local);ob.matrix_world=Matrix.Identity(4)
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='Lettering')

def wall(poly,holes,name,back=-.40,front=0):
 m=Mesh('Wall '+name)
 for p in cuts(poly,holes):
  m.add([(u,z,front) for u,z in p],[tuple(range(len(p)))])
  m.add([(u,z,back) for u,z in p],[tuple(reversed(range(len(p))))])
 for p in holes:
  for a,b in zip(p,p[1:]+p[:1]):
   if abs(a[1])+abs(b[1])<1e-8:continue # Threshold owns the ground-level closure.
   m.add([(*a,front),(*b,front),(*b,back),(*a,back)],[(0,1,2,3)])
 return m
holes=[]
for j,u in enumerate(D['bays']):
 holes.append(ellipse_arch(u,0 if j==0 else .65,3.88,.70,.755,32))
 for lo,hi in [(7.77,9.77),(10.93,12.93)]:holes.append(rect(u-.60,lo,u+.60,hi))
finish(wall(rect(0,0,W,14.98),holes,'front'),frame=F)
# A003 includes the narrow upper strip alongside the colonnade. Its shallow
# return depth is provisional; the access mouth remains open below it.
box('Passage upper frontage',(-.305,9.14,-.20),(.61,11.68,.40),mat=stone)
box('Passage lower pier',(-.11,1.65,-.20),(.22,3.30,.40),mat=granite)
for zz in (3.70,3.78,6.45,7.03,13.80):
 box('Passage stone band',(-.305,zz,.025),(.61,.045,.05),mat=darkstone)
# Back and sides are explicit skins, stepped to the measured longitudinal profile.
profile=[(0,0),(25.15,0),(25.15,3.0),(19.15,3.0),(19.15,7.22),(13.5,7.22),(13.5,10.7),(6.05,16.0),(0,14.45)]
# The lower rear extension narrows on the alley side, as shown on A002.
for x,reverse in [(0,True),(W,False)]:
 m=Mesh('Wall '+('alley' if x==0 else 'party'))
 # Upper main section; lower ground return steps in independently below.
 pts=[(x,y,z) for y,z in [(0,0),(13.5,0),(13.5,10.7),(6.05,16),(0,14.45)]]
 m.add(pts,[tuple(reversed(range(len(pts)))) if reverse else tuple(range(len(pts)))]);finish(m,mat=rear)
# Rear wings have restrained blank masonry until owner photos arrive.
for name,a,b,lo,hi,height in [('middle',0,W,13.5,19.15,7.22),('rear',3.7,W,19.15,25.15,3.0)]:
 m=Mesh('Wall '+name+' wing')
 m.add([(a,lo,0),(a,hi,0),(a,hi,height),(a,lo,height)],[(0,3,2,1)])
 m.add([(b,lo,0),(b,hi,0),(b,hi,height),(b,lo,height)],[(0,1,2,3)])
 m.add([(a,hi,0),(b,hi,0),(b,hi,height),(a,hi,height)],[(3,2,1,0)])
 finish(m,mat=rear)
m=Mesh('Wall rear upper');m.add([(0,13.5,7.22),(W,13.5,7.22),(W,13.5,10.7),(0,13.5,10.7)],[(3,2,1,0)]);finish(m,mat=rear)
# Roof facets meet at one ridge, with a shallow front and a longer steeper rear.
m=Mesh('Roof slate planes');m.add([(0,0,14.45),(W,0,14.45),(W,6.05,16),(0,6.05,16)],[(0,1,2,3)]);m.add([(0,6.05,16),(W,6.05,16),(W,13.5,10.7),(0,13.5,10.7)],[(0,1,2,3)]);finish(m,'roof',roofmat)
for name,a,b,lo,hi,z in [('middle',0,W,13.5,19.15,7.22),('rear',3.7,W,19.15,25.15,3.)]:
 m=Mesh('Roof '+name+' flat');m.add([(a,lo,z),(b,lo,z),(b,hi,z),(a,hi,z)],[(0,1,2,3)]);finish(m,'roof',lead)
# Front masonry already owns the parapet face; only cap/back/end surfaces here.
m=Mesh('Roof front parapet')
m.add([(0,14.98,0),(W,14.98,0),(W,14.98,-.32),(0,14.98,-.32)],[(0,1,2,3)])
m.add([(0,14.28,-.32),(0,14.98,-.32),(W,14.98,-.32),(W,14.28,-.32)],[(0,1,2,3)])
for x in (0,W):m.add([(x,14.45,0),(x,14.98,0),(x,14.98,-.32),(x,14.45+.32*1.55/6.05,-.32)],[(3,2,1,0) if x==W else (0,1,2,3)])
finish(m,'roof',stone,F)
# Simple rear fixtures are deferred; observed slate rooflights retained.
for x,y in [(2.1,9.5),(5.2,9.5)]:
 z=16-(y-6.05)*(5.3/7.45)
 slope=math.atan2(-5.3,7.45);m=Mesh('Rooflight curb');m.box((0,0,0),(.65,.86,.10));rot=Matrix.Translation((x,y,z+.06))@Matrix.Rotation(slope,4,'X');finish(m,'roof',lead,T@rot)
 m=Mesh('Rooflight glass');m.box((0,0,.06),(.51,.70,.035));finish(m,'roof',glass,T@rot)
# Basic opening geometry is present in both massing and detailed review stages.
for i,u in enumerate(D['bays']):
 if i==0:
  m=Mesh('Glazing door fanlight');m.outline(ellipse_arch(u,3.36,3.88,.70,.755),-.32,-.27);finish(m,'frontage',glass,F)
  box('Door backing',(u,1.68,-.34),(1.40,3.36,.12),'frontage',black)
  box('Door closed security leaves',(u,1.38,-.10),(1.32,2.76,.14),'frontage',gold)
 else:
  m=Mesh('Glazing tall '+str(i));m.outline(ellipse_arch(u,.65,3.88,.70,.755),-.32,-.27);finish(m,'frontage',glass,F)
 for j,(lo,hi) in enumerate([(7.77,9.77),(10.93,12.93)]):box('Glazing upper '+str(i)+' '+str(j),(u,(lo+hi)/2,-.23),(1.2,hi-lo,.08),'frontage',glass)
# Four polished Tuscan columns, with ringed tapered shafts rather than flutes.
for k,u in enumerate(D['columns']):
 box('Pedestal '+str(k),(u,.93,.14),(.65,1.86,.51),mat=granite)
 m=Mesh('Pedestal moulding '+str(k))
 for z,profile in [(0,[(0,.43),(.34,.43),(.36,.46),(.40,.46),(.44,.39),(.48,.36),(.52,.36)]),(1.64,[(0,.36),(.04,.40),(.08,.46),(.16,.46),(.19,.39),(.22,.37)])]:
  # Wrap all three exposed sides with a continuous rectangular stepped profile.
  rings=[(z+v,out) for v,out in profile]
  verts=[(u+dx*(.325+(out-.36)*.45),zz,.14+dy*(out-.14)) for zz,out in rings for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
  faces=[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j) for i in range(len(rings)-1) for j in (1,2,3)]
  m.add(verts,[tuple(reversed(face)) for face in faces])
 finish(m,mat=granite,frame=F)
 m=Mesh('Column Tuscan '+str(k));m.lathe((u,-.20),[(1.86,.37),(1.93,.37),(1.99,.33),(2.05,.31),(2.10,.31),(2.15,.285),(2.25,.275),(3.1,.266),(4.25,.235),(4.65,.224),(4.69,.25),(4.76,.25),(4.82,.30),(4.91,.33)],48)
 m.vertices=[(x,z,-y) for x,y,z in m.vertices];ob=finish(m,mat=granite,frame=F)
 for polygon in ob.data.polygons:polygon.use_smooth=True
 box('Column abacus '+str(k),(u,4.95,.20),(.72,.10,.65),mat=granite)
 for zz,rr in [(3.1,.266),(4.25,.235)]:
  m=Mesh('Fine column joint');m.lathe((u,-.20),[(zz-.006,rr+.001),(zz+.006,rr+.001)],48);m.vertices=[(x,z,-y) for x,y,z in m.vertices];finish(m,mat=darkstone,frame=F)
# Full width lower entablature and upper cornice profiles.
for name,z,p in [('lower cornice',6.05,[(0,.04),(.06,.24),(.12,.28),(.18,.31),(.23,.40),(.28,.40),(.32,.19),(.36,.19),(.40,.36),(.45,.36),(.51,.22)]),('fascia top',7.03,[(0,.03),(.06,.16),(.11,.19),(.16,.24),(.20,.24),(.23,.02)]),('roof cornice',13.80,[(0,.02),(.10,.13),(.16,.14),(.22,.25),(.28,.32),(.34,.35),(.40,.35),(.44,.05)])]:
 m=Mesh('Trim '+name);moulding(m,0,W,z,p);finish(m,mat=darkstone,frame=F)
box('Entablature frieze',(W/2,5.60,.105),(W,1.0,.21),mat=granite)
box('Sign fascia backing',(W/2,6.72,.08),(W,.58,.16),mat=granite)
if DETAIL:
 # Ashlar is segmented around actual apertures; joints are physical shallow grooves.
 m=Mesh('Fine upper ashlar')
 for row in range(17):
  lo=7.25+row*.405;hi=min(13.80,lo+.397)
  if hi<=lo:continue
  for k in range(-1,9):
   a=max(0,k*1.03+(row%2)*.515+.004);b=min(W,k*1.03+(row%2)*.515+1.026)
   if b<=a:continue
   for p in cuts(rect(a,lo,b,hi),[rect(u-.83,z-.10,u+.83,Z+.10) for u in D['bays'] for z,Z in [(7.77,9.77),(10.93,12.93)]]):m.outline(p,.003,.022,(k+row)%7)
 finish(m,mat=var,frame=F)
 # Smooth granite arch voussoirs run out to flat header and column faces.
 for j,u in enumerate(D['bays']):
  m=Mesh('Arch voussoirs '+str(j))
  for k in range(9):
   a=math.pi*k/9+.007;b=math.pi*(k+1)/9-.007
   # Radial joints meet a flat lintel and vertical sides, not a floating ring.
   def edge(t):
    c=math.cos(t);sn=math.sin(t);r=min(1.07/max(abs(c),1e-9),1.14/max(sn,1e-9));return (u+r*c,3.88+r*sn)
   points=[(u+.76*math.cos(a),3.88+.81*math.sin(a)),edge(a)]
   for corner in (math.atan2(1.14,1.07),math.pi-math.atan2(1.14,1.07)):
    if a<corner<b:points.append(edge(corner))
   points.extend([edge(b),(u+.76*math.cos(b),3.88+.81*math.sin(b))])
   m.outline(points,.025,.13)
  finish(m,mat=granite,frame=F)
  m=Mesh('Trim ground arch '+str(j));arc(m,u,3.88,.70,.755,.045,out=.07,depth=.10);finish(m,mat=darkstone,frame=F)
 # Recessed frieze panels and triglyphs.
 for k in range(7):
  u=.17+(W-.34)*k/6
  for dx in (-.055,0,.055):box('Fine triglyph',(u+dx,5.67,.265),(.025,.48,.055),mat=darkstone)
 for z in (5.35,5.99):box('Fine frieze border',(W/2,z,.24),(W,.045,.05),mat=darkstone)
 for k in range(27):
  x=.12+k*(W-.24)/26
  box('Fine lower modillion',(x,6.15,.35),(.11,.11,.14),mat=granite)
  box('Fine roof modillion',(x,13.95,.22),(.10,.16,.19),mat=darkstone)
 # Main sash architraves and slender margin panes.
 for i,u in enumerate(D['bays']):
  for j,(lo,hi) in enumerate([(7.77,9.77),(10.93,12.93)]):
   for sign in (-1,1):
    box('Trim sash jamb',(u+sign*.70,(lo+hi)/2,.065),(.17,hi-lo,.13),mat=darkstone)
    box('Trim sash bead',(u+sign*.61,(lo+hi)/2,.095),(.03,hi-lo,.06),mat=stone)
   for z,h in ((lo-.04,.08),(hi+.07,.14)):box('Trim sash rail',(u,z,.07),(1.58,h,.14),mat=darkstone)
   for zz in (lo-.025,hi+.025):box('Trim inner rail',(u,zz,.125),(1.29,.035,.065),mat=stone)
   for xx in (-.78,.78):box('Trim outer architrave',(u+xx,(lo+hi)/2,.10),(.035,hi-lo+.24,.07),mat=stone)
   box('Trim projecting sill',(u,lo-.14,.17),(1.65,.12,.34),mat=darkstone)
   m=Mesh('Frames upper '+str(i)+' '+str(j))
   for x in (-.565,.565):m.box((u+x,(lo+hi)/2,-.10),(.045,hi-lo-.10,.10))
   for z in (lo+.035,hi-.035,(lo+hi)/2):m.box((u,z,-.08),(1.16,.05,.11))
   for x in (-.39,.39):m.box((u+x,(lo+hi)/2,-.075),(.028,hi-lo-.10,.08))
   for z in (lo+.17,hi-.17):m.box((u,z,-.075),(1.10,.025,.08))
   finish(m,'frontage',white,F)
   # Blinds visible in 2026 street photograph; behind the outer glazing bars.
   if (i,j) in [(0,0),(1,0),(2,0),(2,1)]:
    box('Blind upper '+str(i)+' '+str(j),(u,hi-.35,-.17),(1.08,.60,.035),'frontage',blind)
  box('Trim inset spandrel',(u,10.40,.025),(1.40,.33,.05),mat=stone)
 # Central window pediment and consoles.
 u=D['bays'][1];m=Mesh('Trim central pediment');m.outline([(u-1.04,10.195),(u+1.04,10.195),(u,10.72)],.031,.17)
 m.outline([(u-1.12,10.16),(u,10.82),(u+1.12,10.16),(u+1.02,10.16),(u,10.71),(u-1.02,10.16)],.155,.305)
 m.box((u,10.14,.17),(2.17,.11,.34));finish(m,mat=darkstone,frame=F)
 for sign in (-1,1):
  m=Mesh('Trim pediment console');m.outline([(u+sign*.75-.08,9.76),(u+sign*.75+.08,9.76),(u+sign*.75+.10,10.12),(u+sign*.75-.10,10.12)],.03,.21);finish(m,mat=darkstone,frame=F)
 # Ground windows: no invented grid over the large central panes.
 for i,u in enumerate(D['bays']):
  low=3.36 if i==0 else .65;m=Mesh('Frames ground '+str(i))
  arc(m,u,3.88,.655,.710,.03,out=-.105,depth=.08,steps=32)
  arc(m,u,3.88,.61,.665,.022,out=-.09,depth=.07,steps=32)
  arc(m,u,3.88,.14,.14,.022,out=-.075,depth=.065,steps=20)
  for a in (math.pi/3,2*math.pi/3):beam(m,(u+.16*math.cos(a),3.88+.16*math.sin(a),-.075),(u+.62*math.cos(a),3.88+.67*math.sin(a),-.075),.025,.065)
  for x in (-.665,.665):m.box((u+x,(low+3.88)/2,-.11),(.045,3.88-low,.10))
  for z in (low+.04,3.84,3.72):m.box((u,z,-.095),(1.30,.035,.08))
  if i:
   for x in (-.53,.53):m.box((u+x,2.22,-.09),(.025,3.10,.07))
   for z in (.86,2.59,2.72):m.box((u,z,-.085),(1.29,.028,.08))
  finish(m,'frontage',white,F)
  if i:
   box('Trim ground sill',(u,.56,.12),(1.50,.15,.34),mat=granite)
   for sign in (-1,1):box('Trim window jamb',(u+sign*.75,2.22,.07),(.09,3.14,.14),mat=granite)
 # Closed gold panelled security doors match the April exterior photograph.
 u=D['bays'][0]
 for sign in (-1,1):
  for row in range(4):
   z=.35+row*.65;x=u+sign*.325
   # Raised rails surround a recessed leaf panel; sloping bevels meet both planes.
   m=Mesh('Door panel surround');outer=rect(x-.325,z-.325,x+.325,z+.325);hole=rect(x-.245,z-.255,x+.245,z+.255)
   for poly in cuts(outer,[hole]):m.outline(poly,-.025,.02)
   inner=rect(x-.215,z-.225,x+.215,z+.225)
   for j in range(4):
    k=(j+1)%4;m.add([(*hole[j],.02),(*hole[k],.02),(*inner[k],-.029),(*inner[j],-.029)],[(0,1,2,3)])
   finish(m,'frontage',gold,F)
 box('Door meeting stile',(u,1.38,.007),(.035,2.76,.035),'frontage',goldlight)
 for dx in (-.08,.08):box('Door handle',(u+dx,1.1,.035),(.018,.15,.04),'frontage',goldlight)
 # Full perimeter masonry prevents gaps around the smaller square door below fanlight.
 box('Door head backing',(u,3.06,-.14),(1.40,.60,.28),mat=granite)
 for sign in (-1,1):box('Door jamb backing',(u+sign*.68,1.38,-.19),(.04,2.76,.42),mat=granite)
 box('Door threshold',(u,-.025,-.13),(1.4,.05,.50),mat=granite)
 # Current lettering is authored geometry; no logos/photos copied into textures.
 text('main','COFFEE KING',4.45,6.72,.174,.32,3.95)
 text('door','COFFEE KING',u,3.06,.022,.17,1.31)
 m=Mesh('Sign crown');cx=1.65;z=6.63
 m.outline([(cx-.34,z),(cx+.34,z),(cx+.42,z+.23),(cx+.22,z+.10),(cx+.22,z+.29),(cx+.10,z+.13),(cx,z+.35),(cx-.10,z+.13),(cx-.22,z+.29),(cx-.22,z+.10),(cx-.42,z+.23)],.17,.20)
 for dx,dz in [(-.42,.23),(-.22,.29),(0,.35),(.22,.29),(.42,.23)]:
  ring=[(cx+dx+.045*math.cos(math.tau*i/16),z+dz+.045*math.sin(math.tau*i/16)) for i in range(16)];m.outline(ring,.202,.215)
 finish(m,'frontage',goldlight,F)
 # Street-visible bookshop direction sign; unseen court signage is deferred.
 box('Sign Parkinson backing',(-.31,11.37,.035),(.47,6.15,.05),'frontage',black)
 for x in (-.535,-.085):box('Sign Parkinson border',(x,11.37,.068),(.012,6.05,.015),'frontage',goldlight)
 for z in (8.35,14.39):box('Sign Parkinson border',(-.31,z,.068),(.45,.012,.015),'frontage',goldlight)
 for row,char in enumerate('PARKINSONS'):
  text('Parkinson '+str(row),char,-.31,14.08-row*.36,.07,.27,.075 if char=='I' else .29,white)
 for row,char in enumerate('BOOKS'):
  text('Books '+str(row),char,-.31,10.53-row*.36,.07,.27,.075 if char=='I' else .29,white)
 # Slate courses lie within each pitch, not in the ground plane.
 m=Mesh('Fine slate joints')
 for a,b,za,zb in [(0,6.05,14.45,16),(6.05,13.5,16,10.7)]:
  slope=(zb-za)/(b-a)
  for j in range(1,int((b-a)/.23)):
   y=a+j*.23;z=za+(y-a)*slope+.009
   m.box((W/2,y,z),(W,.008,.010))
 finish(m,'roof',lead)
# Batch repeated construction families after affine transforms/UVs are baked.
# This preserves fine-feature omission rules while avoiding hundreds of tiny
# source objects in Cycles selected-to-active projection. Unique glazing and
# column identifiers remain available to the validator.
families={}
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH':families.setdefault((ob.users_collection[0].name,re.sub(r'\.\d{3}$','',ob.name)),[]).append(ob)
for (part,name),objects in families.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=name
# Repeatable review scene.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.4,-.5);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1200;s.render.resolution_y=1500;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/coffee-king.blend'))
