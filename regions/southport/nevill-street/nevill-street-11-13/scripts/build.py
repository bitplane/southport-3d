"""Present-day Neville Buildings: measured composition, authored ornament."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from components import rect,cut,arch,ring,profile,leaf
from plan import world,front_line,footprint,roof_faces,gable_profile,roof_height,hood_faces,hood_cheeks
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];E=D['cornice'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
x,y,z=D['origin'];T=Matrix(((.0135,-1,0,x),(1,-.02087,0,y),(0,0,1,z),(0,0,0,1)));F=T@face_matrix((0,0,0),(0,-1,0))
def mat(name,color,rough=.75,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Muted red Victorian brick',(.40,.18,.14),texture='brick');tile=mat('Weathered red clay roof',(.30,.17,.14),texture='slate');stone=mat('Warm pale sandstone',(.63,.57,.44));clean=mat('Stone projecting arris',(.71,.66,.54));shade=mat('Weathered stone recess',(.42,.37,.29));white=mat('Fine cream sash frames',(.73,.72,.64),.55);glass=mat('Dark blue grey glazing',(.075,.13,.16),.3);iron=mat('Black painted wrought iron',(.025,.032,.032),.58);red=mat('Burgundy shop lettering',(.27,.035,.035));timber=mat('Dark shop joinery',(.105,.063,.049));granite=mat('Pink grey shop granite',(.44,.36,.33),texture='granite');gold=mat('Pale gold fascia',(.70,.57,.31));banner=mat('Buffet cream sign',(.73,.75,.65));green=mat('Buffet green lettering',(.05,.24,.18));lead=mat('Rooflight zinc',(.31,.35,.36));frost=mat('Rooflight glazing',(.22,.34,.38));render=mat('Pale weathered rear masonry',(.55,.42,.32))
def finish(m,part='frontage',material=brick,frame=None,closed=False):
 if not m.faces:return
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Authored metric surface')
 for p in ob.data.polygons:
  across=Vector((p.normal.y,-p.normal.x,0));across=across.normalized() if across.length>.01 else Vector((1,0,0));rise=p.normal.cross(across).normalized()
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   if material==tile:uv.data[li].uv=(v.dot(across)/1.8,v.dot(rise)/1.8)
   elif frame is not None:uv.data[li].uv=(v.x/1.8,v.y/.6)
   else:
    axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2]);uv.data[li].uv=(v[axes[0]]/1.8,v[axes[1]]/.6)
 ob.data.transform(frame if frame is not None else T)
 if closed:ob['closed_shell']=True
 return ob

def box(name,c,size,material=stone,part='frontage',frame=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,material,frame)
def poly(name,p,out,material,part='frontage',frame=F,thickness=.03):
 m=Mesh(name);m.outline(p,out-thickness,out);return finish(m,part,material,frame)
def skin(name,a,b,lo,hi,holes,frame=F,material=brick,part='frontage',depth=.28):
 m=Mesh('Shell '+name)
 for p in cut(rect(a,lo,b,hi),holes):
  m.add([(u,z,0) for u,z in p],[tuple(range(len(p)))]);m.add([(u,z,-depth) for u,z in p],[tuple(reversed(range(len(p))))])
 for p in holes:
  for A,B in zip(p,p[1:]+p[:1]):m.add([(*A,0),(*B,0),(*B,-depth),(*A,-depth)],[(0,1,2,3)])
 return finish(conform({'wall':m})[0]['wall'],part,material,frame)
def flat_ring(name,outer,inner,back,out,material=stone,part='frontage',frame=F,open_x=()):
 m=Mesh(name)
 for p in cut(outer,[inner]):
  m.add([(*v,out) for v in p],[tuple(range(len(p)))]);m.add([(*v,back) for v in p],[tuple(reversed(range(len(p))))])
 for loop in (outer,list(reversed(inner))):
  for A,B in zip(loop,loop[1:]+loop[:1]):
   if abs(A[0]-B[0])<1e-8 and any(abs(A[0]-x)<1e-8 for x in open_x):continue
   m.add([(*A,back),(*B,back),(*B,out),(*A,out)],[(0,1,2,3)])
 return finish(conform({'ring':m})[0]['ring'],part,material,frame)
def sash(u,z,w,h,frame=F,part='frontage',rows=4,cols=3):
 poly('Glazing sash',rect(u-w/2,z,u+w/2,z+h),-.17,glass,part,frame)
 # Single carved frame surface with pane holes: no overlapping rail/jamb boxes.
 outer=rect(u-w/2,z,u+w/2,z+h);holes=[];bw=.045
 for i in range(cols):
  a=u-w/2+bw+i*(w-2*bw)/cols;b=u-w/2+bw+(i+1)*(w-2*bw)/cols
  for j in range(rows):
   q=z+bw+j*(h-2*bw)/rows;r=z+bw+(j+1)*(h-2*bw)/rows
   holes.append(rect(a+.010,q+.012,b-.010,r-.012))
 m=Mesh('Architecture sash joinery')
 for p in cut(outer,holes):m.add([(*v,-.07) for v in p],[tuple(range(len(p)))])
 finish(m,part,white,frame)
 ob=bpy.data.objects.get('Glazing sash')
 # Every pane remains backed only by its recessed glazing, never the masonry.
 if DETAIL and part=='frontage':
  limits=(-100,100)
  if frame==F and part=='frontage' and abs(z-4.35)<.001:
   windows=D['first_windows'];idx=next(i for i,p in enumerate(windows) if abs(p[0]-u)<.001)
   limits=((windows[idx-1][0]+windows[idx-1][1]/2+u-w/2)/2 if idx else .03,(u+w/2+windows[idx+1][0]-windows[idx+1][1]/2)/2 if idx<len(windows)-1 else W-D['corner_radius'])
  def bound(a,b,c,d):return rect(max(a,limits[0]),b,min(c,limits[1]),d)
  flat_ring('Architecture stepped architrave' ,bound(u-w/2-.12,z-.11,u+w/2+.12,z+h+.12),outer,.012,.115,stone,part,frame,open_x=limits)
  flat_ring('Fine architrave arris',bound(u-w/2-.17,z-.15,u+w/2+.17,z+h+.17),bound(u-w/2-.12,z-.11,u+w/2+.12,z+h+.12),.015,.145,clean,part,frame,open_x=limits)
  a=max(u-w/2-.20,limits[0]);b=min(u+w/2+.20,limits[1]);box('Architecture projecting sill',((a+b)/2,z-.12,.16),(b-a,.11,.34),stone,part,frame)

def course(name,line,z,pr,material=stone,part='frontage'):
 m=Mesh(name);n=len(pr)
 for k,(A,B) in enumerate(zip(line,line[1:])):
  du,dv=B[0]-A[0],B[1]-A[1];ln=math.hypot(du,dv);normal=Vector((dv/ln,-du/ln))
  def vertex(i,h,o):
   u,v=line[i]
   if i==0 or i==len(line)-1:return (u+normal.x*o,v+normal.y*o,z+h)
   P=line[i-1];N=line[i+1];d0=Vector((u-P[0],v-P[1])).normalized();d1=Vector((N[0]-u,N[1]-v)).normalized();n0=Vector((d0.y,-d0.x));n1=Vector((d1.y,-d1.x));off=(n0+n1)*o/max(.1,(n0+n1).dot(n0));return(u+off.x,v+off.y,z+h)
  v=[vertex(i,h,o) for i in (k,k+1) for h,o in pr];f=[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
  if k==0:f.append(tuple(reversed(range(n))))
  if k==len(line)-2:f.append(tuple(n+i for i in range(n)))
  m.add(v,f)
 return finish(m,part,material,T)

line=front_line(D);flat=W-D['corner_radius'];front_holes=[rect(u-w/2,4.35,u+w/2,6.93) for u,w in D['first_windows']]+[rect(u-.53,8.18,u+.53,10.61) for u in D['upper_windows']]
# Ground front granite is the actual wall material; no overlay over brick.
ground_holes=[rect(.28,.90,1.25,2.78),rect(1.42,.90,2.38,2.78),rect(2.55,.90,3.48,2.78),rect(3.68,.04,4.86,2.45),rect(5.12,.90,6.08,2.78),rect(6.25,.90,7.22,2.78),rect(7.39,.90,8.62,2.78)]
skin('ground granite',0,flat,0,3.26,ground_holes,material=granite)
skin('front red brick',0,flat,3.26,E,front_holes)
for u,w in D['first_windows']:sash(u,4.35,w,2.58,cols=2 if w<.7 else 3)
for u in D['upper_windows']:sash(u,8.18,1.06,2.43)
# Rounded corner wall, segment ownership avoids overlaid cylinder and box faces.
for k,(A,B) in enumerate(zip(line[1:],line[2:])):
 du,dv=B[0]-A[0],B[1]-A[1];ww=math.hypot(du,dv);frame=T@face_matrix((*A,0),(dv,-du,0));holes=[]
 if k in (2,3,4,5):holes=[rect(0,z,ww,z+h) for z,h in [(4.35,2.58),(8.18,2.43)]]
 # Joined radial reveal vertices: adjacent chord faces must not extrude
 # overlapping square reveals around one continuous curved opening.
 m=Mesh('Shell curved corner '+str(k));cc=W-D['corner_radius'];rr=D['corner_radius']
 def cv(u,z,back=False):
  t=u/ww;px=A[0]+t*(B[0]-A[0]);py=A[1]+t*(B[1]-A[1])
  if back:px=cc+(px-cc)*(rr-.28)/rr;py=rr+(py-rr)*(rr-.28)/rr
  return(px,py,z)
 for pp in cut(rect(0,3.26,ww,12.55),holes):
  m.add([cv(u,z) for u,z in pp],[tuple(range(len(pp)))]);m.add([cv(u,z,True) for u,z in pp],[tuple(reversed(range(len(pp))))])
 for hp in holes:
  for aa,bb in zip(hp,hp[1:]+hp[:1]):
   vertical=abs(aa[0]-bb[0])<1e-8
   if vertical and not ((k==2 and aa[0]<.001) or (k==5 and aa[0]>ww-.001)):continue
   m.add([cv(*aa),cv(*bb),cv(*bb,True),cv(*aa,True)],[(0,1,2,3)])
 finish(conform({'corner':m})[0]['corner'])
 gh=[rect(0,.90,ww,3.19)] if 1<=k<=6 else [];m=Mesh('Shell curved shop '+str(k))
 for pp in cut(rect(0,0,ww,3.26),gh):
  m.add([cv(u,z) for u,z in pp],[tuple(range(len(pp)))]);m.add([cv(u,z,True) for u,z in pp],[tuple(reversed(range(len(pp))))])
 for hp in gh:
  for aa,bb in zip(hp,hp[1:]+hp[:1]):
   vertical=abs(aa[0]-bb[0])<1e-8
   if vertical and not ((k==1 and aa[0]<.001) or (k==6 and aa[0]>ww-.001)):continue
   m.add([cv(*aa),cv(*bb),cv(*bb,True),cv(*aa,True)],[(0,1,2,3)])
 finish(conform({'wall':m})[0]['wall'],material=granite)
 if gh:
  def gp(u,z,depth):
   xx,yy,_=cv(u,z);f=(rr-depth)/rr;return(cc+(xx-cc)*f,rr+(yy-rr)*f,z)
  m=Mesh('Glazing corner shop');m.add([gp(0,.90,.16),gp(ww,.90,.16),gp(ww,3.19,.16),gp(0,3.19,.16)],[(0,1,2,3)]);finish(m,material=glass)
  m=Mesh('Architecture curved shop joinery');aa=.04 if k==1 else 0;bb=ww-.04 if k==6 else ww
  for zz in (.94,2.78,3.15):m.add([gp(aa,zz-.035,.065),gp(bb,zz-.035,.065),gp(bb,zz+.035,.065),gp(aa,zz+.035,.065)],[(0,1,2,3)])
  if k in (1,6):
   a,b=(0,.04) if k==1 else (ww-.04,ww)
   m.add([gp(a,.90,.065),gp(b,.90,.065),gp(b,3.19,.065),gp(a,3.19,.065)],[(0,1,2,3)])
  finish(m,material=timber)
 for z,h in [(4.35,2.58),(8.18,2.43)]:
  if k in (2,3,4,5):
   def surf(u,z,depth):
    t=u/ww;px=A[0]+t*(B[0]-A[0]);py=A[1]+t*(B[1]-A[1]);factor=(rr-depth)/rr
    return(cc+(px-cc)*factor,rr+(py-rr)*factor,z)
   m=Mesh('Glazing curved sash');m.add([surf(0,z,.16),surf(ww,z,.16),surf(ww,z+h,.16),surf(0,z+h,.16)],[(0,1,2,3)]);finish(m,material=glass)
   m=Mesh('Architecture curved sash frame');j0=.04 if k==2 else 0;j1=ww-.04 if k==5 else ww
   for zz in (z+.03,z+h*.25,z+h*.5,z+h*.75,z+h-.03):m.add([surf(j0,zz-.018,.07),surf(j1,zz-.018,.07),surf(j1,zz+.018,.07),surf(j0,zz+.018,.07)],[(0,1,2,3)])
   if k in (2,5):
    aa,bb=(0,.04) if k==2 else (ww-.04,ww)
    m.add([surf(aa,z,.07),surf(bb,z,.07),surf(bb,z+h,.07),surf(aa,z+h,.07)],[(0,1,2,3)])
   finish(m,material=white)
 if DETAIL:
  for z,h in [(4.35,2.58),(8.18,2.43)]:
   if k in (2,3,4,5):
    for zz in (z-.09,z+h+.09):
     m=Mesh('Architecture curved stone window band')
     def bp(t,h,o):
      xx=A[0]+t*(B[0]-A[0]);yy=A[1]+t*(B[1]-A[1]);f=(rr+o)/rr;return(cc+(xx-cc)*f,rr+(yy-rr)*f,h)
     vv=[bp(t,zz+hh,o) for t in (0,1) for hh,o in [(-.08,0),(-.08,.14),(.08,.14),(.08,0)]]
     fs=[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]
     if k==2:fs.append((3,2,1,0))
     if k==5:fs.append((4,5,6,7))
     m.add(vv,fs);finish(m,material=stone)
   if k in (1,6):box('Architecture curved window jamb',(ww/2,z+h/2,.05),(ww,h+.30,.13),stone,frame=frame)
# Visible passage side has no claimed ground survey. Rear upper openings are
# estimated from 3D: two groups of paired windows; hidden doors omitted.
side=T@face_matrix((W,D['corner_radius'],0),(1,0,0));sidew=L-D['corner_radius'];sideholes=[]
for zz in (4.7,8.0):
 for u in (6.7,8.1):sideholes.append(rect(u-.43,zz,u+.43,zz+1.45))
skin('passage side',0,sidew,0,D['roof_eave'],sideholes,side,brick,'rear')
for zz in (4.7,8.0):
 for u in (6.7,8.1):sash(u,zz,.86,1.45,side,'rear',rows=2,cols=2)
back=T@face_matrix((W,L,0),(0,1,0));rearholes=[]
for zz in (4.7,8.55):
 for u in (1.05,2.35,6.15,7.45):rearholes.append(rect(u-.42,zz,u+.42,zz+1.40))
skin('rear brick',0,W,0,D['roof_eave'],rearholes,back,render,'rear')
for zz in (4.7,8.55):
 for u in (1.05,2.35,6.15,7.45):sash(u,zz,.84,1.40,back,'rear',rows=2,cols=2)
party=T@face_matrix((0,L,0),(-1,0,0));skin('shared south party',0,L,0,D['roof_eave'],[],party,brick,'rear',depth=.24)
# Main roof: continuously joined closed slab. Gable intersects only below its
# solid brick silhouette, not as coplanar plates on top of the roof.
def slab(name,faces,material=tile):
 m=Mesh('Shell roof '+name);edges={}
 for f in faces:
  m.add(f,[tuple(range(len(f)))]);m.add([(x,y,z-.07) for x,y,z in f],[tuple(reversed(range(len(f))))])
  for A,B in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((A,B))),[]).append((A,B))
 for pairs in edges.values():
  if len(pairs)==1:
   A,B=pairs[0];m.add([A,(A[0],A[1],A[2]-.07),(B[0],B[1],B[2]-.07),B],[(0,1,2,3)])
 return finish(m,'roof',material,closed=True)
slab('main hip',[p for _,p in roof_faces(D)])
# Central brick gable is a real shallow volume; small flanking dormers separate.
c=D['gable_centre'];gp=gable_profile(D);opening=rect(c-.47,12.67,c+.47,13.15);m=Mesh('Architecture central front gable')
for pp in cut(gp,[opening]):m.add([(*q,.035) for q in pp],[tuple(range(len(pp)))])
m.add([(*q,-.315) for q in gp],[tuple(reversed(range(len(gp))))])
for A,B in zip(gp,gp[1:]+gp[:1]):m.add([(*A,-.315),(*B,-.315),(*B,.035),(*A,.035)],[(0,1,2,3)])
for A,B in zip(opening,opening[1:]+opening[:1]):m.add([(*A,.035),(*B,.035),(*B,-.20),(*A,-.20)],[(0,1,2,3)])
finish(m,'roof',brick,F)
slab('central gable hood',[points for _,points in hood_faces(D)])
for name,points in hood_cheeks(D,underside=True):
 m=Mesh('Architecture '+name);m.add(points,[tuple(range(len(points)))]);finish(m,'roof',brick)
for u in (1.25,7.35):
 p=[(u-.48,12.03),(u+.48,12.03),(u+.48,12.88),(u,13.18),(u-.48,12.88)]
 poly('Architecture small dormer',p,.025,stone,'roof',F,.80)
 # Dark glazing sits in a visible projected frame; detail gable recessed below.
 box('Architecture dormer glazing',(u,12.47,.045),(.65,.48,.025),glass,'roof')
 for q in (-1,1):box('Architecture dormer sash',(u+q*.31,12.47,.08),(.045,.48,.04),white,'roof')
 for zz in (12.25,12.47,12.70):box('Architecture dormer rail',(u,zz,.08),(.575,.035,.04),white,'roof')
# Large opening in the main front gable is represented as a recessed panel in
# detail phase; the massing retains its height for the first comparison.
box('Architecture high gable window',(c,12.91,-.145),(.94,.48,.035),glass,'roof')
flat_ring('Architecture gable window frame',rect(c-.57,12.60,c+.57,13.22),rect(c-.47,12.67,c+.47,13.15),.07,.16,stone,'roof')
for zz in (12.79125,13.02875):box('Architecture gable sash',(c,zz,-.065),(.035,.2025,.035),white,'roof')
box('Architecture gable transom',(c,12.91,-.065),(.90,.035,.035),white,'roof')


# Main shop: arched fanlights, broad recessed entrance and slender brown frames.
for a,b,cx,dz in [(min(p[0] for p in h),max(p[0] for p in h),0,0) for h in ground_holes]:
 door=3.6<a<4
 z0=.04 if door else .9;z1=2.45 if door else 2.78;u=(a+b)/2
 poly('Glazing shop',rect(a,z0,b,z1),-.22,glass)
 for xx in (a+.025,b-.025):box('Architecture shop stile',(xx,(z0+z1)/2,-.13),(.05,z1-z0,.10),timber)
 for zz in ([z1-.04] if door else [z0+.04,z1-.04]):box('Architecture shop rail',(u,zz,-.13),(b-a-.10,.08,.10),timber)
 if door:
  box('Architecture entrance kick',(u,.27,-.12),(b-a-.12,.36,.12),timber)
  box('Architecture entrance midrail',(u,1.05,-.12),(b-a-.12,.07,.12),timber)
  box('Fine brass handle',(u+.32,1.18,-.04),(.028,.35,.045),gold)
 else:
  fan=arch(u,2.78,2.93,(b-a)/2-.02,.28)
  poly('Architecture fanlight glass',fan,.025,frost,thickness=.02)
  m=Mesh('Architecture fanlight rim');ring(m,u,2.93,(b-a)/2-.02,.28,.045,.08,.07);finish(m,material=timber,frame=F)
  box('Architecture fanlight mullion',(u,3.02,.08),(.03,.30,.035),white)
box('Architecture fascia',(flat/2,3.52,.12),(flat,.59,.26),gold)
course('Architecture curved takeaway fascia',line[1:],3.225,[(0,-.01),(0,.25),(.59,.25),(.59,-.01)],gold)
box('Architecture buffet panel',(flat/2,4.12,.47),(flat-.3,.49,.12),banner)
# First floor balcony slabs and upper curved parapet retain silhouette at Walk.
course('Architecture shop cornice',line[:2],3.78,[(0,.02),(.08,.34),(.16,.40),(.25,.29),(.30,.29),(.33,.02)],timber)
course('Architecture first balcony ledge',line[:2],4.23,[(0,.02),(.06,.18),(.13,.28),(.20,.34),(.27,.34),(.30,.02)],stone)
course('Architecture middle ledge',line[:2],7.93,[(0,.02),(.06,.16),(.12,.25),(.19,.25),(.23,.10),(.26,.02)],stone)
course('Architecture eave cornice',line,11.90,[(0,.02),(.08,.15),(.16,.20),(.21,.30),(.26,.30),(.30,.02)],brick)
course('Architecture central gable coving',[(c-1.43,0),(c+1.43,0)],11.82,[(0,.025),(.08,.10),(.13,.15),(.21,.22),(.29,.31),(.40,.39),(.46,.39),(.51,.025)],stone)
# Central upper balcony projects farther than continuous safety rail.
box('Architecture central balcony',(c,8.04,.34),(1.66,.22,.73),stone)

if DETAIL:
 # Pediments: matching front pairs, segmental upper heads and broken
 # triangular lower heads, with approximate carved flowers and scrolls.
 for u in (.95,7.75):
  m=Mesh('Architecture upper curved pediment');ring(m,u,10.99,.68,.25,.075,.28,.22);finish(m,material=clean,frame=F)
  poly('Architecture upper pediment field',arch(u,10.81,10.99,.64,.25),.13,stone)
  box('Architecture upper frieze',(u,10.92,.12),(1.40,.18,.25),stone)
  for j in range(7):box('Fine upper frieze block',(u-.51+j*.17,10.93,.26),(.085,.08,.035),shade)
 for u in (1.35,7.35):
  box('Architecture lower carved frieze',(u,7.15,.16),(1.41,.28,.34),stone)
  for sg in (-1,1):
   # Two moulded sloping sides stop short of the central carved crest.
   A=(u+sg*.72,7.30);B=(u+sg*.18,7.70);du=B[0]-A[0];dz=B[1]-A[1];ln=math.hypot(du,dz);ox=-dz/ln*.055;oz=du/ln*.055
   poly('Architecture broken pediment',[(A[0]-ox,A[1]-oz),(B[0]-ox,B[1]+oz),(B[0]+ox,B[1]+oz+.05),(A[0]+ox,A[1]+oz+.05)],.29,clean,thickness=.20)
   # Fit the support to the actual masonry pier between this window and its
   # narrow neighbour. Fixed offsets previously put capitals over the panes.
   idx=next(i for i,p in enumerate(D['first_windows']) if abs(p[0]-u)<.001)
   neighbour,nw=D['first_windows'][idx+sg]
   edges=sorted((u+sg*1.02/2,neighbour-sg*nw/2))
   pier=sum(edges)/2;clear=edges[1]-edges[0]-.02
   box('Architecture lower window pilaster',(pier,5.72,.10),(min(.14,clear),2.48,.22),stone)
   box('Architecture pilaster capital',(pier,6.91,.21),(clear,.27,.30),clean)
   m=Mesh('Fine capital leaves')
   for j in range(3):leaf(m,pier,6.66,.255,.30,(-.15+j*.15),.035)
   finish(m,material=stone,frame=F)
  m=Mesh('Fine pediment round crest');m.closed_ring((u,7.56,.31),.12,.035,segments=24,sections=6);finish(m,material=stone,frame=F)
  for j in range(7):box('Fine frieze inset',(u-.51+j*.17,7.15,.335),(.08,.10,.02),shade)
 # A circular carved medallion between the building name and central balcony.
 m=Mesh('Fine central medallion');m.closed_ring((c,7.53,.09),.21,.045,segments=32,sections=8);finish(m,material=stone,frame=F)
 m=Mesh('Fine medallion flower')
 for j in range(8):leaf(m,c,7.53,.10,.15,j*math.tau/8,.043)
 finish(m,material=stone,frame=F)
 # July 2026 close view: the large historical gable window is now mostly
 # bricked up. Only a low rectangular sash survives below decorated brickwork.
 for zz in (13.45,14.02,14.44):
  width=1.22 if zz==14.02 else 1.98;box('Architecture gable stone string',(c,zz,.09),(width,.10,.20),stone,'roof')
 for sg in (-1,1):
  # Centre on the solid pier, clear of both adjoining stone architraves.
  box('Architecture tall brick pilaster',(c+sg*.85,10.10,.035),(.20,3.70,.10),brick)
  box('Architecture gable block',(c+sg*.80,14.14,.17),(.36,.34,.34),stone,'roof')
 box('Architecture gable keystone',(c,13.81,.21),(.28,.29,.31),stone,'roof')
 m=Mesh('Fine gable peak ball');m.lathe((c,0),[(15.44,.015),(15.49,.065),(15.56,.070),(15.62,.01)],segments=12);finish(m,'roof',stone)
 # Gable cap with stepped raking cornice; current gable has no chimney/spire.
 for u,zpeak,half,base,part in [(c,15.45,1.10,14.66,'roof'),(1.25,13.18,.53,12.87,'roof'),(7.35,13.18,.53,12.87,'roof')]:
  for A,B in [((u-half,base),(u,zpeak)),((u,zpeak),(u+half,base))]:
   du=B[0]-A[0];dz=B[1]-A[1];ln=math.hypot(du,dz);ox=-dz/ln*.06;oz=du/ln*.06
   pp=[(A[0]-ox,A[1]-oz),(B[0]-ox,B[1]-oz),(B[0]+ox,B[1]+oz),(A[0]+ox,A[1]+oz)];from southport3d.planar import halfplane;pp=halfplane(pp,(u,-100),(u,100),inside=A[0]<u);poly('Architecture gable raking moulding',pp,.24,clean,part,thickness=.20)
  box('Architecture gable cap base',(u,base-.05,.13),(2*half,.12,.30),stone,part)
 for sg in (-1,1):
  u=c+sg*1.15
  box('Architecture gable shoulder',(u,12.42,.14),(.42,.62,.34),stone,'roof')
  box('Architecture gable shoulder cap',(u,12.77,.22),(.57,.12,.44),clean,'roof')
  m=Mesh('Architecture shoulder scroll');pts=[]
  for j in range(20):
   t=j/19;pts.append((u+sg*.25*(1-t),12.79+.68*t,.17+.05*math.sin(math.pi*t)))
  m.tube(pts,.065,sides=8);finish(m,'roof',stone,F)
 # Narrow dentils and stepped central cornice visible in the close gable view.
 for j in range(24):
  u=c-1.35+j*2.70/23;box('Fine central cornice dentil',(u,12.22,.41),(.075,.09,.035),shade)
 # Cornice consoles under the central balcony and central roof shoulders.
 for zz,centres in [(7.77,[c-.68,c+.68]),(11.51,[c-1.15,c+1.15])]:
  for u in centres:
   p=[(u-.10,zz-.23),(u+.10,zz-.23),(u+.16,zz+.25),(u-.16,zz+.25)]
   poly('Architecture scrolling console',p,.29,stone,thickness=.27)
   for j in range(4):box('Fine console flute',(u-.06+j*.04,zz+.04,.305),(.018,.25,.025),shade)
 # Current ironwork: continuous first-floor guard; upper central balcony with
 # graceful sagging runs to the curved corner. No solid replacement fence.
 def rails(path,z,upper=False):
  m=Mesh('Fine balcony ironwork')
  lengths=[0.]
  for A,B in zip(path,path[1:]):lengths.append(lengths[-1]+math.dist(A,B))
  total=lengths[-1]
  def point(t,h):
   dist=t*total
   for k in range(len(path)-1):
    if dist<=lengths[k+1]+1e-8:
     q=(dist-lengths[k])/(lengths[k+1]-lengths[k]);A=path[k];B=path[k+1];return(A[0]+q*(B[0]-A[0]),A[1]+q*(B[1]-A[1]),z+h)
   return(*path[-1],z+h)
  for h in (.05,.58):m.tube([(*p,z+h) for p in path],.017,sides=6)
  count=round(total/.15)
  for j in range(count+1):
   t=j/count;m.tube([point(t,.05),point(t,.60)],.011,sides=5)
  for j in range(round(total/.35)):
   t=(j+.5)/round(total/.35);P=point(t,.31)
   m.tube([(P[0]+.11*math.sin(a*math.tau/16),P[1],P[2]+.16*math.cos(a*math.tau/16)) for a in range(17)],.010,sides=5)
  finish(m,material=iron,frame=T)
 # Offset curve and straight front are assembled as one railing path.
 r=D['corner_radius'];cc=W-r;lower=[(.12,-.32)]+[(cc+(r+.32)*math.cos(-math.pi/2+j*math.pi/16),r+(r+.32)*math.sin(-math.pi/2+j*math.pi/16)) for j in range(9)]+[(W+.32,1.02)]
 rails(lower,4.52)
 rails([(c-.82,-.69),(c+.82,-.69)],8.19)
 for a,b in [(.18,c-.82),(c+.82,flat)]:
  pts=[(a+(b-a)*j/20,-.28,8.20+.30*abs(2*j/20-1)**2) for j in range(21)]
  m=Mesh('Fine draped upper iron rail')
  for dh in (0,.13):m.tube([(x,y,z+dh) for x,y,z in pts],.016,sides=6)
  finish(m,material=iron,frame=T)
 curved=[(cc+(r+.32)*math.cos(-math.pi/2+j*math.pi/16),r+(r+.32)*math.sin(-math.pi/2+j*math.pi/16)) for j in range(9)];rails(curved,8.20)
 # Corner balcony bowl, upper vertical brick slots and thin rainwater pipe.
 arc=line[1:]
 course('Architecture curved first balcony bowl',arc,3.95,[(0,.02),(.08,.08),(.14,.18),(.24,.29),(.32,.38),(.40,.38),(.43,.02)],stone)
 course('Architecture curved upper sill',arc,7.56,[(0,.02),(.08,.07),(.16,.19),(.25,.29),(.35,.34),(.40,.02)],stone)
 course('Architecture curved parapet crown',arc,12.50,[(0,.01),(.06,.11),(.14,.14),(.20,.04),(.20,.01)],stone)
 for zz in (7.05,11.35):course('Architecture corner stringcourse',arc,zz,[(0,.005),(.04,.045),(.09,.045),(.12,.005)],stone)
 for k in range(7):
  a=-math.pi/2+(k+.5)*math.pi/14;P=(cc+(r+.007)*math.cos(a),r+(r+.007)*math.sin(a),7.82);m=Mesh('Fine corner brick slit');m.tube([P,(P[0],P[1],P[2]+.22)],.012,sides=4);finish(m,material=shade,frame=T)
 # Long granite base sill and facade joints belong to the frontage asset.
 box('Architecture granite sill',(flat/2,.83,.045),(flat,.085,.12),timber)
 for u in (.10,flat-.10):box('Fine rainwater pipe',(u,6.3,.14),(.055,11.1,.065),iron)
 fonts={k:bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/'+n) for k,n in [('bold','LiberationSerif-Bold.ttf'),('italic','LiberationSerif-BoldItalic.ttf'),('plain','LiberationSans-Regular.ttf')]}
 def letters(body,u,z,w,h,font='bold',material=red,out=.26,part='frontage'):
  ob=text_object('Fine sign '+body,body,(0,0,0),(0,0,1),h,w,fonts[font],material,extrude=.003,collection=C[part],fit_bounds=True);M=F@Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='Glyph UV')
 fonts['chinese']=bpy.data.fonts.load('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf');letters('帝國',.51,3.55,.65,.32,'chinese');letters('EMPIRE',2.25,3.55,2.15,.40,'italic');letters('RESTAURANT',4.65,3.59,2.40,.25);letters('01704 547 718',4.65,3.36,1.46,.13,'plain',timber)
 letters('CHINESE · MALAYSIAN',7.10,3.62,2.14,.17,'plain',timber);letters('· THAI CUISINE',7.10,3.39,1.70,.16,'plain',timber)
 letters('DIM SUM BUFFET',4.45,4.13,4.78,.36,'italic',red,.538);letters('SUNDAYS &',1.12,4.20,1.20,.11,'plain',red,.538);letters('BANK HOLIDAYS',1.12,4.04,1.20,.11,'plain',red,.538)
 letters('12.00pm - 7.30pm',7.62,4.23,1.48,.10,'plain',red,.538);letters('EAT AS MUCH',7.62,4.10,1.48,.10,'plain',green,.538);letters('AS YOU CAN!',7.62,3.97,1.48,.10,'plain',green,.538)
 letters('NEVILLE BUILDINGS',4.35,7.19,4.48,.18,'bold',iron,.025)
 # The narrow return fascia carries the visible takeaway wording.
 A=line[3];B=line[7];du,dv=B[0]-A[0],B[1]-A[1];cf=T@face_matrix((*A,0),(dv,-du,0));ww=math.hypot(du,dv)
 for body,zz,hh in [('TAKEAWAY',3.60,.13),('01704 547 718',3.39,.075)]:
  ob=text_object('Fine return sign '+body,body,(0,0,0),(0,0,1),hh,ww*.97,fonts['plain'],timber,extrude=.002,collection=C['frontage'],fit_bounds=True);M=cf@Matrix.Translation((ww/2,zz,.32))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='Glyph UV')
 # Tiny unreadable shop print and the stylised buffet logotype are not traced;
 # legible text uses authored fonts, including the observed Chinese fascia.

# Low rectangular rooflights visible in 3D. These are raised glazing panels,
# with independently offset borders and no coplanar patch on the tiled slope.
if DETAIL:
 i=D['roof_inset'];e=D['roof_eave'];t=D['roof_top']
 def rooflight(name,side,u0,u1,v0,v1):
  def p(u,v):
   z=e+(t-e)*(u/i if side=='south' else (W-u)/i);return(u,v,z+.055)
  m=Mesh('Architecture rooflight '+name);m.add([p(u0,v0),p(u1,v0),p(u1,v1),p(u0,v1)],[(0,1,2,3)]);finish(m,'roof',frost)
  m=Mesh('Fine rooflight bars '+name)
  for j in range(7):
   v=v0+(v1-v0)*j/6;A=p(u0,v);B=p(u1,v);m.tube([(A[0],A[1],A[2]+.025),(B[0],B[1],B[2]+.025)],.025,sides=6)
  for u in (u0,u1):
   A=p(u,v0);B=p(u,v1);m.tube([(A[0],A[1],A[2]+.025),(B[0],B[1],B[2]+.025)],.03,sides=6)
  finish(m,'roof',lead)
 rooflight('north broad','north',7.25,9.00,4.55,7.70)
 rooflight('south narrow','south',.70,1.35,6.65,7.85)
 # Five narrow roof windows on the rear pitch, visible in the close 3D orbit.
 for u in (1.35,2.25,4.35,7.05,8.05):
  def p(u,v):return(u,v,roof_height(D,u,v)+.045)
  u0=u-.22;u1=u+.22;v0=L-1.10;v1=L-.32;m=Mesh('Architecture rear roof window');m.add([p(u0,v0),p(u1,v0),p(u1,v1),p(u0,v1)],[(0,1,2,3)]);finish(m,'roof',frost)
  m=Mesh('Fine rear roof window frame')
  for A,B in [(p(u0,v0),p(u1,v0)),(p(u1,v0),p(u1,v1)),(p(u1,v1),p(u0,v1)),(p(u0,v1),p(u0,v0))]:m.tube([(A[0],A[1],A[2]+.02),(B[0],B[1],B[2]+.02)],.023,sides=6)
  finish(m,'roof',lead)
 # Narrow capped ridge strips identify the real hip boundaries.
 m=Mesh('Fine tiled hip ridges')
 for a,b in [((0,0,e),(i,i,t)),((W-.2343,.2343,e+(t-e)*.2343/i),(W-i,i,t)),((W,L,e),(W-i,L-i,t)),((0,L,e),(i,L-i,t))]:m.tube([(a[0],a[1],a[2]+.04),(b[0],b[1],b[2]+.04)],.065,sides=8)
 finish(m,'roof',tile)

# Capped stacks are visible in the close 48 m orbit, though hidden from the
# street-level front. No guessed pots: current imagery resolves flat caps only.
for u,v,z0,z1,ww,ll in D['stacks']:
 box('Architecture capped chimney',(u,v,(z0+z1)/2),(ww,ll,z1-z0),brick,'roof',T)
 box('Architecture chimney coping',(u,v,z1+.09),(ww+.18,ll+.18,.18),lead,'roof',T)
 if DETAIL:
  box('Fine chimney neck band',(u,v,z1-.13),(ww+.09,ll+.09,.12),brick,'roof',T)

for part in C:
 groups={}
 for ob in list(C[part].objects):
  if ob.type!='MESH' or ob.name.startswith(('Shell ','Glazing ')):continue
  groups.setdefault('Fine' if ob.name.startswith('Fine ') else 'Architecture',[]).append(ob)
 for kind,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  obs[0].name=kind+' '+part
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.3;sun.rotation_euler=(.4,.6,.4)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/nevill-street-11-13.blend'))
