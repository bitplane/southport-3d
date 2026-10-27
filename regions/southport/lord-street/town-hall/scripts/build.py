"""Southport Town Hall: measured courtyard ring and evidenced classical exterior."""
from pathlib import Path
import bpy,bmesh,json,math,os,sys
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from shapes import rect,cuts,transform,roofs,elevations
from staircase import flight,baluster_points
D=json.loads((ROOT/'research/layout.json').read_text());W=D['front_width'];DETAIL=D['phase']=='detail';F=face_matrix((0,0,0),(0,-1,0))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for p in ['front','rear','roof','porch','steps']:C[p]=bpy.data.collections.new(p);s.collection.children.link(C[p])
def mat(n,rgb,rough=.8):
 m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;return m
cream=mat('White painted stucco',(.78,.775,.71));trim=mat('Pale dressings',(.86,.85,.79));stone=mat('Aged stair sandstone',(.39,.37,.29));brick=mat('Red brown brick',(.32,.125,.085));terra=mat('Red terracotta',(.48,.22,.14));slate=mat('Welsh slate',(.17,.185,.20));glass=mat('Muted blue grey glazing',(.105,.17,.21),.25);white=mat('Painted joinery',(.75,.78,.74));iron=mat('Black iron',(.035,.042,.041),.45);lead=mat('Roof lead',(.31,.34,.34));dark=mat('Door shadow',(.025,.032,.032));gold=mat('Weathered brass',(.48,.37,.16));mortar=mat('Mortar joints',(.21,.13,.10))
def finish(m,part,material,M=None):
 if not m.faces:return
 if m.name.startswith(('Shell','Joinery','Trim')):m=conform({'m':m})[0]['m']
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Metric')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 if M is not None:ob.data.transform(M)
 for v in ob.data.vertices:v.co=transform(D,tuple(v.co))
 return ob

def box(n,c,sz,ma=trim,part='front',M=F):
 if n in ['Porch landing','Stair central retaining wall','Stair tread']:part='steps'
 m=Mesh(n);m.box(c,sz)
 if M is not None and n.startswith(('Trim','Pilaster','Cornice','Fine','Rear stringcourse','Terracotta','Registrar')):
  omit={0,1,3} if n=='Pilaster shaft' else {0}
  m.faces=[f for i,f in enumerate(m.faces) if i not in omit];m.indices=[0]*len(m.faces)
 return finish(m,part,ma,M)
def plane(n,p,ma,part='front',M=F):
 from mathutils.geometry import tessellate_polygon
 vs=[Vector(v)for v in p];m=Mesh(n)
 for t in tessellate_polygon([vs]):m.add([tuple(vs[i]if isinstance(i,int)else i)for i in t],[(0,1,2)])
 return finish(m,part,ma,M)
def tube(n,p,r,ma=iron,part='front',M=None,sides=10):
 m=Mesh(n);m.tube(p,r,sides=sides);return finish(m,part,ma,M)
def lathe(n,x,y,z,profile,ma,part='front',sides=24,flutes=0):
 m=Mesh(n)
 for j,((h,r),(H,R))in enumerate(zip(profile,profile[1:])):
  for i in range(sides):
   a=math.tau*i/sides;b=math.tau*(i+1)/sides
   def p(t,rr,zz):
    rr*=1-.045*(1+math.cos(flutes*t)) if flutes else 1
    return(x+rr*math.cos(t),y+rr*math.sin(t),z+zz)
   m.add([p(a,r,h),p(b,r,h),p(b,R,H),p(a,R,H)],[(0,1,2,3)])
 return finish(m,part,ma)
def arch(x,z,w,h,n=16):
 r=w/2;rise=.7 if w>3 else r;spring=z+h-rise
 return [(x-r,z),(x+r,z)]+[(x+r*math.cos(t),spring+rise*math.sin(t))for t in [math.pi*i/n for i in range(n+1)]]
def wall(n,p,holes,ma,part='front',M=F):
 m=Mesh('Shell '+n)
 for q in cuts(p,holes):m.add([(*v,0)for v in q],[tuple(range(len(q)))])
 for q in holes:
  for a,b in zip(q,q[1:]+q[:1]):m.add([(*a,0),(*b,0),(*b,-.22),(*a,-.22)],[(0,1,2,3)])
 return finish(m,part,ma,M)
def frame(n,x,z,w,h,arched=False,part='front',M=F,ma=white):
 p=arch(x,z,w,h)if arched else rect(x-w/2,z,x+w/2,z+h)
 is_door=n in ('north ground 30','north registrar door')
 plane('Glazing '+n,[(*v,-.23)for v in p],dark if is_door else glass,part,M)
 # Ribbon frame has one front skin and no coplanar overlay at the opening.
 inner=arch(x,z+.065,w-.13,h-.13)if arched else rect(x-w/2+.065,z+.065,x+w/2-.065,z+h-.065)
 m=Mesh('Joinery '+n)
 for q in cuts(p,[inner]):m.add([(*v,-.10)for v in q],[tuple(range(len(q)))])
 finish(m,part,ma,M)
 spring=z+h-(.7 if w>3 else w/2) if arched else z+h
 if not is_door:
  divisions=1 if n.startswith('north return') else 3 if arched and w>3 else 2
  for i in range(1,divisions):box('Joinery '+n+' central bar',(x-w/2+w*i/divisions,(z+spring)/2,-.11),(.055,spring-z-.13,.12),ma,part,M)
  for i in range(divisions):
   xx=x-w/2+w*(i+.5)/divisions;ww=w/divisions-.055-(.0375 if i in [0,divisions-1] else 0)
   box('Joinery '+n+' sash rail',(xx,z+(spring-z)*.52,-.11),(ww,.075,.12),ma,part,M)
   if arched:box('Joinery '+n+' spring rail',(xx,spring,-.11),(ww,.055,.12),ma,part,M)
 if DETAIL and not is_door:
  box('Trim '+n+' sill',(x,z-.08,.17),(w+.25,.16,.34),trim if ma==white else ma,part,M)
  outer=arch(x,z-.08,w+.36,h+.26)if arched else rect(x-w/2-.18,z-.12,x+w/2+.18,z+h+.18)
  m=Mesh('Trim '+n+' architrave')
  for q in cuts(outer,[p]):m.add([(*v,.09)for v in q],[tuple(range(len(q)))])
  finish(m,part,trim if ma==white else ma,M)
  if arched:box('Trim '+n+' keystone',(x,z+h+.11,.17),(.30,.36,.18),trim if ma==white else ma,part,M)

def frustum(n,x,y,z,w,d,h,topw,topd,ma,part):
 p=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)];q=[(x-topw/2,y-topd/2,z+h),(x+topw/2,y-topd/2,z+h),(x+topw/2,y+topd/2,z+h),(x-topw/2,y+topd/2,z+h)]
 for i in range(4):plane(n+' '+str(i),[p[i],p[(i+1)%4],q[(i+1)%4],q[i]],ma,part,None)
 plane(n+' cap',q,ma,part,None)
# Front: shell cut around every opening, including entrance.
holes=[];windows=[]
for i,x in enumerate(D['front_bays']):
 if i!=3:
  windows += [(f'front basement {i}',x,.55,1.7,1.55,False),(f'front ground {i}',x,3.15,1.75,3.5,True)]
 windows += [(f'front upper {i}',x,8.5,1.75 if i!=3 else 1.55,3.2,False)]
for n,x,z,w,h,a in windows:holes.append(arch(x,z,w,h)if a else rect(x-w/2,z,x+w/2,z+h))
holes.append(rect(W/2-1.2,2.8,W/2+1.2,6.8))
wall('front',rect(0,-.15,W,D['eaves']),holes,cream)
for n,x,z,w,h,a in windows:frame(n,x,z,w,h,a)
plane('Entrance dark doorway',[(W/2-1.2,2.8,-.24),(W/2+1.2,2.8,-.24),(W/2+1.2,6.8,-.24),(W/2-1.2,6.8,-.24)],dark)
for xx in [W/2-.64,W/2+.64]:box('Door timber leaf',(xx,4.3,-.15),(1.12,2.9,.12),iron)
if DETAIL:
 for xx in [W/2-.64,W/2+.64]:
  for zz in [3.25,4.35,5.25]:box('Door raised panel',(xx,zz,-.075),(.86,.72,.035),dark)
  box('Door brass handle',(xx+(.32 if xx<W/2 else -.32),4.25,-.02),(.04,.30,.04),gold)
 # Horizontal channelled rustication, clipped to openings and pilaster zones.
 for j in range(17):
  z=.38+j*.42
  if z>7.25:break
  for q in cuts(rect(0,z,W,z+.018),holes):plane('Fine front rustication',[(*v,.012)for v in q],stone)
 # Run-out voussoir joints evidenced around the six round heads.
 for x in [v for i,v in enumerate(D['front_bays']) if i!=3]:
  spring=3.15+3.5-.875
  for k in range(1,6):
   t=math.pi*k/6
   tube('Fine radial masonry joint',[(x+1.08*math.cos(t),-.025,spring+1.08*math.sin(t)),(x+1.48*math.cos(t),-.025,spring+1.48*math.sin(t))],.008,stone,sides=6)
 # Paired pilasters framing1:2:1:2:1 composition; no overlap between storey segments.
 for x in [.35,4.63,5.12,10.8,11.29,16.90,17.39,23.07,23.56,W-.35]:
  for lo,hi in [(2.62,7.45),(8.03,12.35)]:
   box('Pilaster shaft',(x,(lo+hi)/2,.12),(.32,hi-lo,.24),trim)
   box('Pilaster base',(x,lo+.08,.20),(.44,.16,.40),trim)
   box('Pilaster capital',(x,hi-.08,.22),(.46,.16,.44),trim)
 for z,h,dep in [(2.35,.24,.20),(7.43,.24,.28),(7.75,.24,.42),(12.35,.24,.32),(12.65,.26,.52)]:box('Cornice front',(W/2,z,dep/2),(W,h,dep),trim)
 for i in range(112):box('Fine eaves dentil',(.13+i*(W-.26)/111,12.47,.36),(.13,.18,.22),trim)
# Parapet and central tympanum are actual silhouette.
for a,b in [(0,10.2),(17.99,W)]:
 box('Parapet base',((a+b)/2,12.95,.08),(b-a,.24,.46),trim)
 box('Parapet top',((a+b)/2,13.8,.08),(b-a,.19,.48),trim)
 if DETAIL:
  for i in range(int((b-a)/.38)):
   x=a+.22+i*.38;lathe('Baluster roof',x,-.08,13.07,[(0,.12),(.1,.12),(.18,.065),(.34,.10),(.46,.06),(.61,.09)],trim)
 else:box('Massing parapet',((a+b)/2,13.38,.08),(b-a,.62,.28),cream)
for x in [.4,5.0,10.3,17.89,23.19,W-.4]:box('Parapet pier',(x,13.4,.08),(.7,1.12,.65),trim)
ped=[(10.0,12.92),(18.19,12.92),(14.095,15.45)]
plane('Shell pediment',[(x,z,.16)for x,z in ped],cream)
plane('Pediment back',[(x,z,-.30)for x,z in ped[::-1]],cream)
for a,b in zip(ped,ped[1:]+ped[:1]):tube('Pediment moulding',[(a[0],-.27,a[1]),(b[0],-.27,b[1])],.15,trim)
# Porch freestanding floor/roof and columns. Ground and front wall own their own skins.
p=D['porch'];x0,x1=p['x0'],p['x1'];cx=W/2
box('Porch landing',(cx,-1.56,2.67),(x1-x0,3.12,.26),stone,'porch',None)
box('Porch ceiling',(cx,-1.52,7.72),(x1-x0+.32,3.28,.24),trim,'porch',None)
box('Porch entablature',(cx,-1.52,8.05),(x1-x0+.56,3.46,.42),cream,'porch',None)
for x in [x0+.4,x1-.4]:
 box('Porch corner pier',(x,-2.73,5.15),(.54,.60,4.7),trim,'porch',None)
for x in [cx-1.65,cx+1.65]:
 lathe('Doric porch column',x,-2.73,2.8,[(0,.42),(.18,.42),(.3,.34),(.45,.32),(4.22,.28),(4.35,.36),(4.5,.43),(4.67,.43)],trim,'porch',sides=100 if DETAIL else 24,flutes=20 if DETAIL else 0)
 box('Doric abacus',(x,-2.73,7.53),(.92,.92,.15),trim,'porch',None)
if DETAIL:
 for i in range(17):
  x=x0-.12+i*(x1-x0+.24)/16;box('Fine porch triglyph',(x,-3.275,8.04),(.20,.07,.32),trim,'porch',None)
  for dx in [-.055,0,.055]:box('Fine triglyph groove',(x+dx,-3.315,8.04),(.015,.012,.25),stone,'porch',None)
 for x in [cx-1.46,cx+1.46]:
  lathe('Ionic upper semi column',x,-.10,8.40,[(0,.25),(.18,.25),(.3,.20),(3.35,.18),(3.47,.25),(3.58,.30)],trim,sides=40)
  for dx in [-.23,.23]:
   pts=[(x+dx+.13*math.cos(t),-.32,12.04+.13*math.sin(t))for t in [math.tau*k/32 for k in range(33)]];tube('Ionic volute',pts,.045,trim)
# Parallel lateral flights. Each has eight risers, a short landing, then eight
# more risers. The solid side cheek, spindle seats and rail share this profile.
st=D['stair'];z0=-.02;h=2.8;N=st['steps'];left=(st['x0'],x0);right=(x1,st['x1']);yf=-st['front'];yb=-st['back']
box('Stair central retaining wall',(cx,(yf+yb)/2,1.325),(x1-x0,yb-yf,2.95),cream,'porch',None)
for a,b,rise_right in [(left[0],left[1],True),(right[0],right[1],False)]:
 treads,segments=flight(st,a,b,rise_right,z0,h)
 for xa,xb,top in treads:
  lo,hi=sorted((xa,xb))
  box('Stair tread',((lo+hi)/2,(yf+yb)/2,(top-.16)/2),(hi-lo,yb-yf,top+.16),stone,'porch',None)
 if DETAIL:
  for yy in [yf,yb]:
   # Offset the cheek outside the walking treads. Its top surface is a real
   # continuous stone seat for every spindle, including the flat landing.
   outer=yy+(-.22 if yy==yf else .22);mid=(outer+yy)/2
   for (xa,za),(xb,zb) in segments:
    if xa>xb:xa,xb,za,zb=xb,xa,zb,za
    za+=.09;zb+=.09
    side=[(xa,outer,-.16),(xb,outer,-.16),(xb,outer,zb),(xa,outer,za)]
    plane('Stair cheek side',side if outer<yy else side[::-1],cream,'porch',None)
    seat=[(xa,outer,za),(xb,outer,zb),(xb,yy,zb),(xa,yy,za)]
    plane('Stair cheek seat',seat if outer<yy else seat[::-1],stone,'porch',None)
    # A rectangular rail has a defined underside rather than a round tube.
    for edge in [outer,yy]:
     side=[(xa,edge,za+.85),(xb,edge,zb+.85),(xb,edge,zb+1.02),(xa,edge,za+1.02)]
     plane('Stair handrail side',side if edge==min(outer,yy) else side[::-1],stone,'porch',None)
    bottom=[(xa,outer,za+.85),(xb,outer,zb+.85),(xb,yy,zb+.85),(xa,yy,za+.85)]
    top=[(xa,outer,za+1.02),(xb,outer,zb+1.02),(xb,yy,zb+1.02),(xa,yy,za+1.02)]
    plane('Stair handrail bottom',bottom[::-1] if outer<yy else bottom,stone,'porch',None)
    plane('Stair handrail top',top if outer<yy else top[::-1],stone,'porch',None)
   for x,z in baluster_points(st,segments):
    lathe('Baluster stair',x,mid,z,[(0,.105),(.12,.105),(.25,.055),(.43,.105),(.58,.08),(.70,.055),(.85,.085)],stone,'porch',sides=16)
for x in [st['x0'],x0,x1,st['x1']]:
 z=h if x in [x0,x1]else z0
 box('Stair balustrade pier',(x,yf,z+.55),(.6,.64,1.15),stone,'porch',None)
 box('Stair pier cap',(x,yf,z+1.2),(.77,.8,.15),stone,'porch',None)
 lathe('Stair finial',x,yf,z+1.275,[(0,.17),(.12,.22),(.25,.18),(.34,0)],stone,'porch',sides=20)
for yy in [yf]:
 box('Balcony rail',(cx,yy,h+.95),(x1-x0,.24,.20),stone,'porch',None)
 if DETAIL:
  for j in range(1,st['landing_balusters']+1):lathe('Baluster landing',x0+j*(x1-x0)/(st['landing_balusters']+1),yy,h,[(0,.12),(.15,.12),(.3,.065),(.48,.12),(.62,.075),(.85,.11)],stone,'porch',sides=16)
# Upper balcony railing same robust architectural form.
for yy in [-3.29]:
 box('Porch balcony base',(cx,yy,8.285),(x1-x0+.5,.30,.05),trim,'porch',None)
 box('Porch balcony rail',(cx,yy,9.12),(x1-x0+.5,.30,.18),trim,'porch',None)
 if DETAIL:
  for j in range(1,20):lathe('Baluster porch',x0+j*(x1-x0)/20,yy,8.31,[(0,.11),(.15,.11),(.3,.06),(.48,.105),(.60,.06),(.72,.10)],trim,'porch',sides=16)
for x in [x0-.1,x1+.1]:box('Porch balcony pier',(x,-3.29,8.72),(.52,.48,.85),trim,'porch',None)
for x in [x0-.1,x1+.1]:
 box('Porch balcony return base',(x,-1.57,8.285),(.30,3.14,.05),trim,'porch',None)
 box('Porch balcony return rail',(x,-1.57,9.12),(.30,3.14,.18),trim,'porch',None)
 if DETAIL:
  for j in range(1,9):lathe('Baluster porch return',x,-3.29+j*3.29/9,8.31,[(0,.11),(.15,.11),(.3,.06),(.48,.105),(.60,.06),(.72,.10)],trim,'porch',sides=16)
# Roof and remaining wall ring. Courtyard geometry stays open.
for n,poly in roofs(D):plane('Roof '+n,poly,slate,'roof',None)
for n,a,b,ha,hb in elevations(D):
 dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy);tx,ty=dx/L,dy/L
 M=Matrix(((tx,0,ty,a[0]),(ty,0,-tx,a[1]),(0,1,0,0),(0,0,0,1)))
 wins=[]
 if n=='north':
  side=D['north_return']
  for yy in side['lower_windows_m']:wins.append((f'north return lower {yy}',L-yy,.55,1.1,1.75,False,white))
  for yy in side['middle_windows_m']:wins.append((f'north return middle {yy}',L-yy,3.4,1.1,2.5,False,white))
  for yy in side['upper_windows_m']:
   small=abs(yy-side['door_depth_m'])<.2
   wins.append((f'north return upper {yy}',L-yy,9.05 if small else 8.5,.85 if small else 1.1,1.45 if small else 2.1,False,white))
  wins.append(('north registrar door',L-side['door_depth_m'],side['door_threshold_m'],1.25,2.22,False,white))
  for yy in [15.5,18.4,21.3,25.0,28.0,31.0,34.5]:
   for zz,hh in [(5.2,2.15),(9.1,1.5)]:wins.append((f'{n} red {yy} {zz}',L-yy,zz,1.25,hh,zz==1.0,terra))
  for yy,ww,zz,hh in [(16,3.4,1,3.0),(24,1.25,1,2.8),(27,1.25,1,3.5),(30,1.25,.96,2.84),(35,3.4,1,3.0)]:wins.append((f'north ground {yy}',L-yy,zz,ww,hh,True,terra))
  for yy in [39.5,42.8,46.1]:wins.append((f'{n} rear arch {yy}',L-yy,8.0,1.65,2.7,True,white))
 elif n=='arcade':
  for yy in [5.5,10,16,20,24,28,32,36,41,45]:
   for zz in [4.7,8.1]:wins.append((f'{n} upper {yy} {zz}',yy,zz,1.4,2.0,False,white))
 if n=='arcade':
  for yy,ww in [(5.0,2.4),(9.2,2.6),(14.0,3.4),(19.2,3.2),(24.0,3.2),(29.2,3.5),(35.0,3.7),(41.5,4.0),(46.0,2.8)]:wins.append((f'arcade shop {yy}',yy,.35,ww,2.8,False,white))
 hs=[arch(x,z,w,h)if ar else rect(x-w/2,z,x+w/2,z+h)for _,x,z,w,h,ar,_ in wins]
 if n=='north':
  cut=L-12;zc=ha+(hb-ha)*cut/L
  wall(n+' brick',[(0,-.15),(cut,-.15),(cut,zc),(0,ha)],[h for h,v in zip(hs,wins) if v[1]<cut],brick,'rear',M)
  wall(n+' stucco',[(cut,-.15),(L,-.15),(L,hb),(cut,zc)],[h for h,v in zip(hs,wins) if v[1]>=cut],cream,'rear',M)
 else:wall(n,[(0,-.15),(L,-.15),(L,hb),(0,ha)],hs,cream if n.startswith('court')else brick,'rear',M)
 for name,x,z,w,h,ar,ma in wins:frame(name,x,z,w,h,ar,'rear',M,ma)
 if DETAIL and n in ['north','arcade']:
  courseL=L-12 if n=='north' else L
  for zz in [4.3,7.8,11.45]:box('Rear stringcourse '+n,(courseL/2,zz,.10),(courseL,.18,.20),terra,'rear',M)
  if n=='north':
   for zz in [7.75,12.55]:box('Rear stringcourse white return',(L-6,zz,.12),(12,.24,.24),trim,'rear',M)
   # The white return is rusticated to first-floor level; the registrar's
   # ground-level doorway is recessed, with projecting pilasters and lintel.
   for zz in [.45,1.0,1.55,2.1,2.65,3.2,3.75,4.3,4.85,5.4,5.95,6.5,7.05]:
    for q in cuts(rect(L-12,zz,L,zz+.016),[h for h,v in zip(hs,wins) if v[1]>=L-12]):
     plane('Fine north return joint',[(*v,.012) for v in q],stone,'rear',M)
   door=L-D['north_return']['door_depth_m'];threshold=D['north_return']['door_threshold_m']
   for xx in [door-.78,door+.78]:
    box('Registrar entrance jamb',(xx,threshold+1.11,.17),(.31,2.22,.34),trim,'rear',M)
    box('Registrar entrance capital',(xx,threshold+2.10,.22),(.43,.18,.44),trim,'rear',M)
   box('Registrar entrance lintel',(door,threshold+2.41,.18),(1.9,.38,.36),cream,'rear',M)
   box('Registrar entrance cap',(door,threshold+2.66,.23),(2.1,.12,.46),trim,'rear',M)
   box('Registrar sign blank',(door+1.3,threshold+1.65,.035),(.64,.56,.07),mat('Registrar sign blue',(.06,.10,.25)),'rear',M)
   plane('Registrar door leaf',[(door-.48,threshold+.03,-.16),(door+.48,threshold+.03,-.16),(door+.48,threshold+2.15,-.16),(door-.48,threshold+2.15,-.16)],mat('Registrar door timber',(.075,.065,.055)),'rear',M)
   box('Registrar door pull',(door+.32,threshold+1.02,-.12),(.045,.24,.035),gold,'rear',M)
  for yy in [12,23,35,48]:box('Rear downpipe '+n,(yy,5.6,.21),(.11,11.2,.12),iron,'rear',M)
  if n=='north':
   # Stucco front return is clipped at12m and owns its outward skin.
   for yy in [13,20.5,32,37.5]:
    x=L-yy
    for j in range(15):box('Terracotta rusticated pier',(x,.55+j*.25,.10),(.58,.235,.20),terra,'rear',M)
   # White two-level oriel at rear, long observed glazing bands; existing wall holes absent behind this attached projection.
   for z in [1.0,4.0]:
    plane('Rear oriel glazing',[(.85,z,.425),(11.15,z,.425),(11.15,z+2.1,.425),(.85,z+2.1,.425)],glass,'rear',M)
    for i in range(12):box('Rear oriel mullion',(.85+i*.94,z+1.05,.46),(.055,2.1,.12),white,'rear',M)
    for zz in [z,z+2.1]:box('Rear oriel sill',(6,zz,.47),(10.55,.14,.25),white,'rear',M)
# Glazed pyramidal roof lantern near front, physically modelled mullions.
frustum('Lantern kerb',14.0,16.0,13.35,5.1,4.4,.45,5.1,4.4,lead,'roof')
frustum('Lantern glazing',14.0,16.0,13.80,5.0,4.3,1.3,.18,.18,glass,'roof')
if DETAIL:
 apex=(14,16.0,15.12)
 for x,y in [(11.5,13.85),(16.5,13.85),(16.5,18.15),(11.5,18.15),(14,13.85),(14,18.15),(11.5,16.0),(16.5,16.0)]:tube('Lantern glazing bar',[(x,y,13.80),apex],.045,white,'roof')
 # A restrained central relief: three observed figures and round shields; no invented inscription.
 for i,(x,z,hh)in enumerate([(12.75,13.3,1.05),(14.095,13.26,1.68),(15.48,13.3,.98)]):
  # Carved drapery is a shallow folded relief surface, never a detached statue.
  verts=[];faces=[];rows=16;cols=16
  for j in range(rows+1):
   t=j/rows;width=(.40*(1-t)+.19*t)
   for k in range(cols+1):
    u=k/cols*2-1;verts.append((x+u*width,-.22-.10*(1-u*u)-.026*math.cos(u*math.pi*4+t*2),z+t*hh*.76))
  for j in range(rows):
   for k in range(cols):q=j*(cols+1)+k;faces.append((q,q+1,q+cols+2,q+cols+1))
  m=Mesh('Carving drapery '+str(i));m.add(verts,faces);finish(m,'front',trim)
  # Head flattened ellipsoid and shoulder/arm gestures follow visible grouping only.
  bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=(0,0,0));ob=bpy.context.object;ob.name='Carving head '+str(i);ob.scale=(.13,.07,.17);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for v in ob.data.vertices:v.co=transform(D,(v.co.x+x,v.co.y-.30,v.co.z+z+hh*.88))
  for c in list(ob.users_collection):c.objects.unlink(ob)
  C['front'].objects.link(ob);ob.data.materials.append(trim)
  tube('Carving arm '+str(i),[(x-.2,-.28,z+hh*.68),(x-.38,-.30,z+hh*.45)],.075,trim)
  tube('Carving arm '+str(i),[(x+.2,-.28,z+hh*.68),(x+.40,-.30,z+hh*.57)],.075,trim)
 for x in [11.75,16.45]:
  pts=[(x+.27*math.cos(t),-.25,13.4+.26*math.sin(t))for t in [math.tau*j/40 for j in range(41)]];tube('Carving roundel',pts,.05,trim)
 # Twin globe lamps mounted on inner stair piers.
 for x in [x0,x1]:
  lathe('Stair lamp',x,yf,4.02,[(0,.18),(.18,.18),(.3,.11),(1.65,.075),(1.8,.16),(1.92,.16)],iron,'porch',sides=24)
  lathe('Lamp globe',x,yf,5.94,[(0,.10),(.07,.23),(.22,.32),(.42,.31),(.57,.21),(.63,.05)],trim,'porch',sides=32)
 box('Noticeboard case',(cx,yf-.09,1.25),(2.9,.20,1.42),iron,'porch',None)
 for x in [cx-.83,cx-.23,cx+.47]:box('Noticeboard blank paper',(x,yf-.20,1.25),(.44,.015,.82),white,'porch',None)
if DETAIL:
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
 ob=text_object('Noticeboard heading','SOUTHPORT TOWN HALL',(cx,yf-.205,1.78),(0,-1,0),.12,2.5,font,gold,extrude=.001,collection=C['porch'])
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
 for v in ob.data.vertices:v.co=transform(D,tuple(v.co))
# Merge repeated members by semantic family before export/baking. This keeps
# source topology and ownership checks, but bounds the selected-to-active object
# count: hundreds of separate balusters otherwise repeat BVH work per texel.
for part,col in C.items():
 groups={}
 for ob in list(col.objects):
  if ob.type!='MESH':continue
  family='Stair treads' if ob.name.startswith('Stair tread') else ob.name.split()[0]
  groups.setdefault(family,[]).append(ob)
 for family,objects in groups.items():
  if len(objects)<2:continue
  members=[o.name for o in objects]
  bpy.ops.object.select_all(action='DESELECT')
  for ob in objects:ob.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=bpy.context.object
  ob.name=family+' '+part;ob['source_members']=json.dumps(members)
# The entrance owns walking support; buried undersides cannot act as floors.
for ob in C['steps'].objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update()
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.normal.z < -.9],context='FACES')
 bm.to_mesh(ob.data);bm.free()
# Standard render rig.
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
li=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));li.data.energy=2.5;li.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(li)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
(ROOT/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/building.blend'))
