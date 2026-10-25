"""3–9 Nevill Street: red brick, unequal window rhythms and the projecting end bay."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from components import rect,cut,arch,ring,profile,leaf
from plan import world,roof_faces,wing_roof
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];E=D['cornice'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
x,y,z=D['origin'];T=Matrix(((.0135,-1,0,x),(1,-.02087,0,y),(0,0,1,z),(0,0,0,1)));F=T@face_matrix((0,0,0),(0,-1,0))
def mat(name,color,rough=.75,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Warm weathered red brick',(.48,.22,.15),texture='brick');slate=mat('Grey slate',(.17,.18,.19),texture='slate')
cream=mat('Painted pale stone',(.72,.69,.60));stone=mat('Weathered sandstone architraves',(.31,.285,.235));clean=mat('Stone arrises',(.52,.49,.41));darkstone=mat('Moulding shadow',(.25,.25,.22));white=mat('Slender ivory sash frames',(.77,.77,.69),.55)
glass=mat('Opaque dark glazing',(.065,.105,.12),.28);frost=mat('Pale frosted glazing',(.29,.40,.39),.52);black=mat('Dark painted iron',(.025,.032,.030),.55)
red=mat('Burgundy shop joinery',(.19,.025,.048),.6);gold=mat('Ochre gold painted lettering',(.67,.43,.16),.6);lead=mat('Lead flashing',(.28,.30,.31));render=mat('Rear cream render',(.53,.52,.44));felt=mat('Weathered membrane',(.22,.24,.24))
def finish(m,part='frontage',material=brick,frame=None,closed=False):
 if not m.faces:return
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric authored surface')
 for p in ob.data.polygons:
  if material==slate:
   across=Vector((p.normal.y,-p.normal.x,0));across=across.normalized() if across.length>.01 else Vector((1,0,0));rise=p.normal.cross(across).normalized()
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   if material==slate:uv.data[li].uv=(v.dot(across)/2.4,v.dot(rise)/2.2)
   elif frame is not None:uv.data[li].uv=(v.x/1.8,v.y/.6)
   else:
    axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2]);uv.data[li].uv=(v[axes[0]]/1.8,v[axes[1]]/.6)
 ob.data.transform(frame if frame is not None else T)
 if closed:ob['closed_shell']=True
 return ob

def box(name,c,size,material=brick,part='frontage',frame=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,material,frame)
def skin(name,a,b,h,holes,frame=F,material=brick,part='frontage',bottom=0):
 m=Mesh('Shell '+name)
 for p in cut(rect(a,bottom,b,h),holes):
  m.add([(u,z,0) for u,z in p],[tuple(range(len(p)))]);m.add([(u,z,-.28) for u,z in p],[tuple(reversed(range(len(p))))])
 for p in holes:
  depth=.80 if name=='street brick' and min(a for a,b in p)>5 and min(b for a,b in p)<.2 else .28
  for A,B in zip(p,p[1:]+p[:1]):m.add([(*A,0),(*B,0),(*B,-depth),(*A,-depth)],[(0,1,2,3)])
 # Adjoining elevations own their outer faces; no end caps overlap the
 # neighbouring wall. Roof slabs and ground close the top/bottom envelope.
 m=conform({'m':m})[0]['m'];return finish(m,part,material,frame)
def polygon(name,p,out,material,part='frontage',frame=F,thickness=.025):
 m=Mesh(name);m.outline(p,out-thickness,out);return finish(m,part,material,frame)

def window(u,bottom,spring,width,rise,frame=F,part='frontage',upper=False):
 rx=width/2;poly=arch(u,bottom,spring,rx,rise)
 ob=polygon('Glazing arched '+str(u),poly,-.16,glass,part,frame)
 ob['window_probe']=[list(frame@Vector((u+.12,bottom+.22,.5))),list((frame.to_3x3()@Vector((0,0,-1))).normalized())]
 trim=Mesh('Architecture sash '+str(u));h=spring-bottom
 for sign in (-1,1):trim.box((u+sign*(rx-.025),bottom+h/2,-.09),(.05,h,.075))
 for z in (bottom+.028,bottom+h*.53):trim.box((u,z,-.075),(width-.09,.055,.08))
 if not upper:
  trim.box((u,bottom+(h+rise)/2,-.075),(.048,h+rise-.07,.08))
  for z in (bottom+h*.26,bottom+h*.78):trim.box((u,z,-.071),(width-.09,.025,.065))
 else:trim.box((u,spring-.03,-.075),(width-.05,.035,.08))
 ring(trim,u,spring,rx-.05,max(.03,rise-.05),.05,-.045,.075)
 finish(trim,part,white,frame)
 if DETAIL:
  m=Mesh('Architecture carved architrave '+str(u));th=.11 if upper else .14
  for sign in (-1,1):
   m.box((u+sign*(rx+th/2),bottom+h/2,.075),(th,h,.15))
   m.box((u+sign*(rx+th+.025),bottom+h/2,.115),(.045,h,.19))
  ring(m,u,spring,rx,rise,th,.16,.17)
  ring(m,u,spring,rx+th+.025,rise+th+.025,.045,.21,.13)
  # Trapezoidal keystone, not an oversized rectangular plug.
  k=.09 if upper else .14;peak=spring+rise
  m.outline([(u-k*.65,peak-.055),(u+k*.65,peak-.055),(u+k,peak+.31),(u-k,peak+.31)],.13,.28)
  m.box((u,bottom-.055,.14),(width+.39,.11,.30));finish(m,part,stone,frame)

# Street wall: six tall first-floor windows; nine smaller windows above, plus
# the canted end bay. Windows are actual holes through both masonry skins.
front_holes=[arch(u,4.3,6.43,.47,.25) for u in D['first_windows']]+[arch(u,8.05,9.47,.365,.20) for u in D['upper_windows']]
front_holes += [arch(1.0,.20,2.45,.48,.49),rect(1.83,.15,3.62,2.7),rect(3.70,0,4.72,2.70),rect(5.18,.17,9.93,2.91),rect(10.30,.17,14.64,2.91)]
skin('street brick',0,D['end_bay_start'],E-.18,front_holes)
# Painted ground-floor masonry follows the same opening boundaries.
for p in cut(rect(0,0,D['end_bay_start'],4.12),front_holes):polygon('Architecture painted base',p,.012,cream,thickness=.012)
for u in D['first_windows']:window(u,4.3,6.43,.94,.25)
for u in D['upper_windows']:window(u,8.05,9.47,.73,.20,upper=True)
# Projecting terminal bay: two slanted cheeks and a flat central face.
bay=D['end_bay_start'];end=[(bay,0),(bay+.26,-.25),(W-.26,-.25),(W,0)]
for k,(A,B) in enumerate(zip(end,end[1:])):
 du,dv=B[0]-A[0],B[1]-A[1];w=math.hypot(du,dv);frame=T@face_matrix((*A,0),(dv,-du,0));mid=w/2
 holes=[arch(mid,4.3,6.43,.46,.25),arch(mid,8.05,9.35,.46,.47),arch(mid,0,2.52,.47,.49)] if k==1 else []
 skin('end bay '+str(k),0,w,E-.18,holes,frame)
 for p in cut(rect(0,0,w,4.12),holes):polygon('Architecture bay painted base',p,.014,cream,frame=frame,thickness=.014)
 if k==1:
  window(mid,4.3,6.43,.92,.25,frame);window(mid,8.05,9.35,.92,.47,frame,upper=True)
  polygon('Architecture end doorway',arch(mid,0,2.52,.47,.49),-.22,black,frame=frame)
  box('Architecture end door',(mid,1.25,-.16),(.77,2.48,.05),frost,frame=frame)
  box('Architecture end door rail',(mid,2.3,-.11),(.82,.18,.07),black,frame=frame)
  if DETAIL:
   m=Mesh('Architecture end door arch');ring(m,mid,2.52,.49,.51,.18,.24,.24)
   for sign in (-1,1):
    for off,width,depth in [(.65,.18,.26),(.81,.09,.34)]:m.box((mid+sign*off,1.32,depth/2),(width,2.64,depth))
   m.box((mid,3.25,.19),(1.65,.16,.38));m.box((mid,3.75,.21),(1.91,.18,.42));finish(m,material=cream,frame=frame)
   orn=Mesh('Fine doorway foliage')
   for sg in (-1,1):
    for j in range(7):leaf(orn,mid+sg*.66,2.45,.30,.45,sg*(.4+j*.18),.075)
   finish(orn,material=cream,frame=frame)
# Small triangular pediment belongs to the terminal bay, not the Empire gable.
cu=(bay+W)/2
polygon('Architecture terminal pediment',[(bay-.02,E-.12),(W+.02,E-.12),(cu,E+.61)],.44,brick)
if DETAIL:
 m=Mesh('Architecture terminal pediment moulding')
 for A,B in [((bay-.08,E-.10),(cu,E+.68)),((cu,E+.68),(W+.08,E-.10))]:
  du,dz=B[0]-A[0],B[1]-A[1];ln=math.hypot(du,dz);ox=-dz/ln*.065;oz=du/ln*.065
  m.outline([(A[0]-ox,A[1]-oz),(B[0]-ox,B[1]-oz),(B[0]+ox,B[1]+oz),(A[0]+ox,A[1]+oz)],.40,.62)
 m.box((cu,E-.06,.45),(W-bay+.16,.12,.44));finish(m,material=cream,frame=F)
 for j in range(5):
  u=bay+.27+j*.34;h=.48*(1-abs(u-cu)/((W-bay)/2));box('Fine pediment dentil',(u,E+.03,.50),(.13,max(.06,h*.5),.18),cream)

# Main wall terminations and rear elevations. Hidden windows are not fabricated.
side0=T@face_matrix((0,L,0),(-1,0,0));side1=T@face_matrix((W,0,0),(1,0,0))
skin('south party wall',0,L,D['roof_eave'],[],side0,brick,'rear');skin('north party wall',0,L,D['roof_eave'],[],side1,brick,'rear')
back=T@face_matrix((W,L,0),(0,1,0));a,b,c,e,h,r=D['rear_wing'];q,Q,v,V,hh,rr=D['low_rear']
# Back wall only where not occupied by the connected rear wings.
for lft,rgt,lo in [(0,a,0),(a,b,h),(0,Q,hh),(b,W,0)]:
 if rgt<=lft:continue
 # Exclude lower rear wing footprint from the main lower wall.
 if lo==0:lft=max(lft,Q)
 holes=[]
 if lo==0:
  for u in (6.4,8.35):
   if not lft<u<rgt:continue
   for zz in (4.65,7.8):holes.append(rect(W-u-.45,zz,W-u+.45,zz+1.5))
 skin('rear main '+str(lft)+' '+str(lo),W-rgt,W-lft,D['roof_eave'],holes,back,brick,'rear',bottom=lo)
 for H in holes:
  x0,z0=H[0];x1,z1=H[2];box('Architecture rear glass',((x0+x1)/2,(z0+z1)/2,-.12),(x1-x0,z1-z0,.035),glass,'rear',back)
  for xx in (x0,x1):box('Architecture rear frame',(xx,(z0+z1)/2,-.05),(.045,z1-z0,.08),white,'rear',back)
  for zz in (z0,(z0+z1)/2,z1):box('Architecture rear rail',((x0+x1)/2,zz,-.04),(x1-x0,.045,.08),white,'rear',back)

for label,spec,colour in [('wing',D['rear_wing'],render),('low',D['low_rear'],brick)]:
 a,b,c,e,h,r=spec
 # Main building owns junction plane; do not add a coincident wall at v=c.
 for name,A,B in [('left',(a,e),(a,c)),('right',(b,c),(b,e)),('end',(b,e),(a,e))]:
  du,dv=B[0]-A[0],B[1]-A[1];ww=math.hypot(du,dv);frame=T@face_matrix((*A,0),(dv,-du,0));holes=[]
  if label=='wing' and name=='left':
   holes=[rect(k*ww/4+.46,z,(k+1)*ww/4-.46,z+1.65) for z in (1.0,4.0,7.0) for k in range(4)]
  elif label=='low' and name=='right':holes=[rect(.65,1.2,1.4,2.7),rect(3.4,1.2,4.15,2.7)]
  skin(label+' '+name,0,ww,h,holes,frame,colour,'rear')
  for hp in holes:
   A0,Z0=hp[0];B0,Z1=hp[2];box('Architecture rear pane',((A0+B0)/2,(Z0+Z1)/2,-.14),(B0-A0,Z1-Z0,.04),glass,'rear',frame)
   for xx in (A0,B0):box('Architecture rear jamb',(xx,(Z0+Z1)/2,-.06),(.06,Z1-Z0,.10),white,'rear',frame)
   for zz in (Z0,(Z0+Z1)/2,Z1):box('Architecture rear transom',((A0+B0)/2,zz,-.05),(B0-A0,.06,.10),white,'rear',frame)
  if name=='end':polygon('Shell '+label+' gable',[(0,h),(ww,h),(ww/2,r)],0,colour,'rear',frame,.28)

# The rear-wing gable rises above the main rear eave at the attachment.
a,b,c,e,h,r=D['rear_wing'];z0=D['roof_eave'];delta=(z0-h)/(r-h)*(b-a)/2
if r>z0:
 frame=T@face_matrix((a,c,0),(0,-1,0));polygon('Shell wing junction gable',[(delta,z0),(b-a-delta,z0),((b-a)/2,r-.001)],0,brick,'rear',frame,.28)

# Closed roof slabs: one exterior owner per surface, no intersecting wedges.
def slab(name,faces,material=slate):
 m=Mesh('Shell roof '+name);edges={}
 for f in faces:
  m.add(f,[tuple(range(len(f)))]);m.add([(x,y,z-.08) for x,y,z in f],[tuple(reversed(range(len(f))))])
  for A,B in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((A,B))),[]).append((A,B))
 for pairs in edges.values():
  if len(pairs)==1:
   A,B=pairs[0];m.add([A,(A[0],A[1],A[2]-.08),(B[0],B[1],B[2]-.08),B],[(0,1,2,3)])
 finish(m,'roof',material,closed=True)
slab('main',[p for name,p in roof_faces(D)])
for name,spec in [('rear wing',D['rear_wing']),('low rear',D['low_rear'])]:slab(name,wing_roof(spec))
# Raised rectangular central roof cover and rear multi-pane rooflight visible
# in aerials. Exact construction is unknown; no guessed dormers or chimney pots.
# Fresh plan and opposing obliques show a mottled dark infill, with only its
# narrow perimeter flashing pale. The former all-lead material made an
# unsupported bright solid bar in every viewing level. Construction remains
# uncertain: use the observed slate-like finish, not invented glazing.
box('Architecture raised roof cover',(W/2,4.45,D['roof_top']+.07),(W-5.8,1.45,.14),slate,'roof',T)
if DETAIL:
 for u in (2.9,W-2.9):box('Fine roof cover curb',(u,4.45,D['roof_top']+.16),(.045,1.51,.05),lead,'roof',T)
 for v in (3.7,5.2):box('Fine roof cover curb',(W/2,v,D['roof_top']+.16),(W-5.8,.045,.05),lead,'roof',T)
 a,b,c,e,h,r=D['rear_wing'];mid=(a+b)/2;u0=a+.35;u1=mid-.15;v0=c+.8;v1=c+2.9
 def sky(u,v,off=0):return (u,v,h+(u-a)*(r-h)/(mid-a)+.12+off)
 m=Mesh('Architecture sloping rooflight');m.add([sky(u0,v0),sky(u1,v0),sky(u1,v1),sky(u0,v1)],[(0,1,2,3)]);finish(m,'roof',glass)
 m=Mesh('Fine rooflight bars')
 for j in range(8):
  v=v0+(v1-v0)*j/7;m.tube([sky(u0,v,.025),sky(u1,v,.025)],.022,sides=6)
 for u in (u0,u1):m.tube([sky(u,v0,.025),sky(u,v1,.025)],.025,sides=6)
 finish(m,'roof',white)

# Ground shopfronts: frosted side windows, recessed side door and two burgundy
# display bays. Appearance is represented from July 2026 Street View.
polygon('Architecture frosted arch',arch(1,.2,2.45,.48,.49),-.11,frost)
box('Architecture frosted display',(2.725,1.425,-.10),(1.79,2.55,.035),frost)
box('Architecture side entrance',(4.21,1.35,-.43),(1.02,2.70,.05),black)
box('Architecture side door glass',(4.21,1.24,-.395),(.78,2.18,.035),frost)
for a,b in [(1.83,3.62),(3.70,4.72)]:
 for u in (a,b):box('Architecture dark window frame',(u,1.42,-.035),(.055,2.57,.075),black)
 box('Architecture dark window head',((a+b)/2,2.7,-.035),(b-a,.055,.075),black)
box('Architecture side doorway reveal',(3.70,1.35,-.25),(.035,2.7,.50),cream)
box('Architecture side doorway reveal',(4.72,1.35,-.25),(.035,2.7,.50),cream)
for a,b in [(5.18,9.93),(10.30,14.64)]:
 ww=b-a;doorw=1.05;dw=ww-doorw;door=a+dw+doorw/2
 box('Architecture display pane',(a+dw/2,1.67,-.42),(dw,2.20,.035),glass)
 box('Architecture red kick panel',(a+dw/2,.44,-.335),(dw,.53,.14),red)
 box('Architecture shop entry',(door,1.49,-.75),(doorw,2.64,.05),red)
 box('Architecture door glazing',(door,1.63,-.70),(doorw-.15,2.05,.035),glass)
 for u in (a,a+dw,b):box('Architecture shop jamb',(u,1.55,-.295),(.08,2.75,.16),red)
 for k in (1,2):box('Architecture shop mullion',(a+dw*k/3,1.67,-.335),(.055,2.2,.09),red)
 for zz in (.70,2.80):box('Architecture shop rail',(a+dw/2,zz,-.305),(dw,.10,.15),red)
 for k in range(3):box('Architecture inset cream kick panel',(a+(k+.5)*dw/3,.43,-.259),(dw/3-.18,.25,.016),cream)
 box('Architecture entrance reveal',(a+dw,1.55,-.53),(.04,2.7,.46),red)
 box('Architecture entrance soffit',(door,2.82,-.52),(doorw,.08,.47),red)
 box('Architecture door handle',(door+.3,1.22,-.635),(.025,.33,.08),gold)
box('Architecture shop fascia',((5.03+14.83)/2,3.46,.045),(14.83-5.03,1.01,.18),cream)

if DETAIL:
 # Continuous horizontal cornices; terminal-bay mitres are generated from the
 # same face line, avoiding overlaid end boxes at the projecting bay.
 line=[(0,0),(bay,0)]+end[1:]
 def course(name,z,pr,material):
  m=Mesh(name)
  # Vertical cross sections translated along the front polyline. Outset is -v;
  # at each corner intersect the neighbouring offset lines (bounded mitre).
  for k,(A,B) in enumerate(zip(line,line[1:])):
   du,dv=B[0]-A[0],B[1]-A[1];ln=math.hypot(du,dv);normal=(dv/ln,-du/ln)
   def vert(i,h,o):
    u,v=line[i]
    if i==0 or i==len(line)-1:return (u+normal[0]*o,v+normal[1]*o,z+h)
    P=line[i-1];N=line[i+1];d0=Vector((u-P[0],v-P[1]));d1=Vector((N[0]-u,N[1]-v));d0.normalize();d1.normalize();n0=Vector((d0.y,-d0.x));n1=Vector((d1.y,-d1.x));s0=n0+n1;off=s0*o/max(.1,s0.dot(n0));return (u+off.x,v+off.y,z+h)
   vv=[vert(i,h,o) for i in (k,k+1) for h,o in pr];n=len(pr)
   fs=[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
   if k==0:fs.append(tuple(reversed(range(n))))
   if k==len(line)-2:fs.append(tuple(n+i for i in range(n)))
   m.add(vv,fs)
  finish(m,material=material,frame=T)
 course('Architecture first cornice',3.96,[(0,.02),(.08,.08),(.08,.13),(.15,.13),(.19,.29),(.28,.29),(.34,.13),(.37,.13),(.37,.02)],cream)
 course('Architecture middle sill band',7.77,[(0,.01),(.08,.11),(.13,.14),(.20,.14),(.23,.04),(.23,.01)],stone)
 course('Architecture upper sill band',9.28,[(0,.01),(.045,.07),(.10,.07),(.10,.01)],darkstone)
 course('Architecture eaves cornice',10.91,[(0,.01),(.08,.12),(.16,.15),(.20,.08),(.30,.08),(.33,.31),(.42,.35),(.51,.40),(.61,.40),(.66,.22),(.69,.22),(.69,.01)],cream)
 # Brick recessed frieze panels and narrow pilasters between upper windows.
 for u in D['upper_windows']:
  box('Fine frieze recess',(u,10.65,.011),(1.12,.21,.025),brick)
  box('Fine frieze top arris',(u,10.78,.028),(1.16,.035,.045),darkstone)
 for u in [(a+b)/2 for a,b in zip(D['upper_windows'],D['upper_windows'][1:])]:
  box('Architecture upper brick pilaster',(u,8.59,.045),(.075,1.19,.09),brick)
  box('Architecture upper pilaster cap',(u,9.17,.07),(.22,.095,.16),stone)
  box('Fine small ventilation grille',(u,8.95,.10),(.15,.105,.025),black)
  for j in range(4):box('Fine grille slot',(u-.055+j*.036,8.95,.115),(.012,.083,.012),stone)
 for u in (5.3,10.1,14.8):
  box('Architecture fascia console',(u,4.01,.13),(.36,.35,.35),cream)
  for j in range(4):box('Fine console flute',(u-.12+j*.08,3.99,.315),(.025,.19,.025),stone)
 for k in range(56):
  u=.12+k*(W-.24)/55;out=.25 if u>bay else 0
  box('Architecture eaves dentil',(u,11.22,.19+out),(.14,.21,.26),cream)
  box('Fine dentil shadow',(u,11.13,.19+out),(.085,.025,.17),stone)
 # Ground pilasters and foliate capitals at the two left bays and ornate door.
 for u in (.20,1.62,4.92):
  box('Architecture painted pilaster',(u,1.93,.06),(.24,3.86,.18),cream)
  for zz in (.18,.48,3.23,3.65):box('Architecture pilaster band',(u,zz,.13),(.37,.10,.30),cream)
  m=Mesh('Fine pilaster foliage')
  for sg in (-1,1):
   for j in range(6):leaf(m,u,3.38,.24,.25,sg*(.15+j*.30),.065)
  finish(m,material=cream,frame=F)
 # Thin sash safety rails appear on the lower halves of the tall windows.
 for u in D['first_windows'][2:]+[cu]:
  out=.31 if u==cu else .12
  box('Fine window guard top',(u,5.08,out),(.91,.025,.025),white)
  for j in range(8):box('Fine window guard spindle',(u-.42+j*.12,4.72,out),(.018,.70,.018),white)
 # Slender drainpipes and air bricks, kept clear of stone opening profiles.
 for u in (14.80,):
  box('Fine rainwater pipe',(u,5.2,.16),(.06,10.4,.07),black)
  for zz in (1,3,5,7,9):box('Fine pipe clip',(u,zz,.14),(.13,.035,.12),black)
 for u,zz in [(5.65,6.9),(9.55,6.9),(12.75,5.25),(8.1,5.3)]:box('Fine air brick',(u,zz,.016),(.25,.12,.035),black)
 fonts={k:bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/'+n) for k,n in [('bold','LiberationSans-Bold.ttf'),('italic','LiberationSerif-Italic.ttf'),('plain','LiberationSans-Regular.ttf')]}
 def letters(body,u,z,w,h,font='bold',material=gold,out=.151):
  ob=text_object('Fine sign '+body,body,(0,0,0),(0,0,1),h,w,fonts[font],material,extrude=.006,collection=C['frontage'],fit_bounds=True)
  M=F@Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='Glyph UV')
 letters('Silcocks',6.65,3.48,2.60,.55,'italic');letters('JACKPOT',10.05,3.46,3.80,.62);letters('Amusements',13.19,3.47,2.25,.40,'italic')
 box('Fine Nevill street plaque',(.47,4.82,.025),(.60,.17,.055),cream)
 letters('NEVILL ST',.47,4.82,.54,.095,'plain',black,.058)
 # Current hanging Occulo sign on the plain left shop bay.
 box('Fine hanging sign bracket',(1.68,2.92,.48),(.055,.055,.85),black)
 box('Fine hanging sign',(1.68,2.64,.66),(.05,.50,.46),red)
 # Observed large display ovals and diagonal cream strips, authored as
 # geometry and lettering. No photograph pixels or unreadable small print.
 for u in (6.95,12.02):
  oval=[(u+1.05*math.cos(t*math.tau/48),1.82+.64*math.sin(t*math.tau/48)) for t in range(48)]
  polygon('Fine display oval',oval,-.385,gold)
  inner=[(u+1.00*math.cos(t*math.tau/48),1.82+.59*math.sin(t*math.tau/48)) for t in range(48)]
  polygon('Fine display oval field',inner,-.369,black,thickness=.012)
  letters('£500 CASH',u,1.96,1.68,.25,'bold',gold,-.35)
  letters('JACKPOT',u,1.65,1.0,.14,'plain',gold,-.35)
  for sign in (-1,1):
   A=(u+sign*.12,.85);B=(u+sign*1.30,1.55);du,dz=B[0]-A[0],B[1]-A[1];ln=math.hypot(du,dz);ox=-dz/ln*.06;oz=du/ln*.06
   polygon('Fine display diagonal',[(A[0]-ox,A[1]-oz),(B[0]-ox,B[1]-oz),(B[0]+ox,B[1]+oz),(A[0]+ox,A[1]+oz)],-.34,cream,thickness=.015)

# Batch by part, material family and role to bound bake traversal cost. Preserve
# window objects and roof shells for meaningful validation rays/manifold checks.
for p in C:
 groups={}
 for ob in list(C[p].objects):
  if ob.type!='MESH' or ob.name.startswith(('Glazing ','Shell ')):continue
  key='Fine' if ob.name.startswith('Fine ') else 'Architecture';groups.setdefault(key,[]).append(ob)
 for kind,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  obs[0].name=kind+' '+p
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.3;sun.rotation_euler=(.4,.6,.4)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/nevill-street-3-9.blend'))
