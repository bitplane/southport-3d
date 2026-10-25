"""Explicit independently authored structural surfaces."""
import math
from bridge_alignment import D,U,N,E,GRADE,xy,transform,grade,width,stations

class Faces:
 def __init__(self):self.items=[]
 def face(self,name,p,mat='concrete',part='deck',cage=.16,weight=1):self.items.append({'name':name,'vertices':[tuple(v)for v in p],'material':mat,'part':part,'cage_m':cage,'weight':weight})
 def box(self,name,a,b,mat='concrete',part='deck',omit=(),**kw):
  x,y,z=a;X,Y,Z=b;v=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
  for side,ix in [('bottom',(0,3,2,1)),('front',(0,1,5,4)),('right',(1,2,6,5)),('back',(2,3,7,6)),('left',(3,0,4,7)),('top',(4,5,6,7))]:
   if side not in omit:self.face(name+' '+side,[v[i]for i in ix],mat,part,**kw)
 def tube(self,name,a,b,r,mat='white',part='fittings',segments=8,cap=True,cage=.06,weight=.4,r2=None):
  import numpy as np
  a,b=np.array(a,float),np.array(b,float);u=b-a;u/=np.linalg.norm(u);n=np.cross(u,[0,0,1]if abs(u[2])<.9 else [0,1,0]);n/=np.linalg.norm(n);v=np.cross(u,n);rr=r if r2 is None else r2
  A=[a+r*(math.cos(i*math.tau/segments)*n+math.sin(i*math.tau/segments)*v)for i in range(segments)]
  B=[b+rr*(math.cos(i*math.tau/segments)*n+math.sin(i*math.tau/segments)*v)for i in range(segments)]
  for i in range(segments):j=(i+1)%segments;self.face(name+' side '+str(i),[A[i],A[j],B[j],B[i]],mat,part,cage,weight)
  if cap:
   self.face(name+' start',list(reversed(A)),mat,part,cage,weight);self.face(name+' end',B,mat,part,cage,weight)
 def leg(self,side,segments=32,fine=True):
  d=D;top=d['pylon_top_z'];zs=[d['pylon_base_z'],54.4]
  if fine:zs=[d['pylon_base_z'],*range(4,53,4),54.4]
  def ring(z,r=1):
   t=side*(d['pylon_base_offset']+(d['pylon_top_offset']-d['pylon_base_offset'])*(z-d['pylon_base_z'])/(54.4-d['pylon_base_z']))
   return [(d['pylon_station']+d['pylon_radius_along']*r*math.cos(i*math.tau/segments),t+d['pylon_radius_across']*r*math.sin(i*math.tau/segments),z)for i in range(segments)]
  rr=[ring(z)for z in zs]
  # Separate rounded tapered metallic caps, with a blunt final crown, not one apex.
  capz=[(54.4,1),(55.4,.76),(56.1,.42),(56.55,.12),(56.6,.025)]if fine else [(54.4,1),(56.0,.45),(56.6,.025)]
  for k,(a,b)in enumerate(zip(rr,rr[1:])):
   for i in range(segments):j=(i+1)%segments;self.face(f'leg {side} lift{k} face{i}',[a[i],a[j],b[j],b[i]],'concrete','pylons',.22)
  self.face('leg bottom '+str(side),list(reversed(rr[0])),'concrete','pylons',.22)
  # Cap centres continue the leg inclination, retaining the separated tips.
  caps=[ring(z,r)for z,r in capz]
  for k,(a,b)in enumerate(zip(caps,caps[1:])):
   for i in range(segments):j=(i+1)%segments;self.face(f'cap {side} ring{k} face{i}',[a[i],a[j],b[j],b[i]],'cap','pylons',.22)
  self.face('cap crown '+str(side),caps[-1],'cap','pylons',.22)
 def deck(self,coarse=False):
  ss=stations()
  for k,(a,b)in enumerate(zip(ss,ss[1:])):
   wa,wb=width(a),width(b)
   # Ground owns the entire flat top between the rail lines. Structure starts at
   # their boundary and wraps the outboard concrete fascia into the soffit.
   self.face('soffit '+str(k),[(a,-wa-.95,grade(a,-wa)-1.05),(a,wa+.95,grade(a,wa)-1.05),(b,wb+.95,grade(b,wb)-1.05),(b,-wb-.95,grade(b,-wb)-1.05)],cage=.18)
   for side in [-1,1]:
    profiles=[(0,0),(1.25,-.50),(.95,-1.05)]
    for j,((t,z),(T,Z))in enumerate(zip(profiles,profiles[1:])):
     p=[(a,side*(wa+t),grade(a,side*wa)+z),(b,side*(wb+t),grade(b,side*wb)+z),(b,side*(wb+T),grade(b,side*wb)+Z),(a,side*(wa+T),grade(a,side*wa)+Z)]
     if side<0:p.reverse()
     self.face(f'fascia {side} {k} {j}',p,cage=.18)
  # End vertical closure lies beneath ground, ending exactly at the top boundary.
  for s,rev in [(0,True),(150,False)]:
   w=width(s);p=[(s,-w,grade(s,-w)),(s,w,grade(s,w)),(s,w+.95,grade(s,w)-1.05),(s,-w-.95,grade(s,-w)-1.05)]
   if rev:p.reverse()
   self.face('deck end '+str(s),p,cage=.18)
  # Western terrace retaining skins meet existing mainland below the fascia;
  # these close the visible gap instead of leaving a raised platform floating.
  west=sorted({112.,*[v for v in stations() if v>112.]})
  for k,(a,b)in enumerate(zip(west,west[1:])):
   for side in [-1,1]:
    ta,tb=side*(width(a)+.95),side*(width(b)+.95)
    p=[(a,ta,1.7),(b,tb,1.7),(b,tb,grade(b,side*width(b))-1.05),(a,ta,grade(a,side*width(a))-1.05)]
    if side>0:p.reverse()
    self.face(f'west retaining {side} {k}',p,cage=.16)
  for st in [0.,150.]:
   w=width(st)+.95;p=[(st,-w,1.7),(st,w,1.7),(st,w,grade(st,width(st))-1.05),(st,-w,grade(st,-width(st))-1.05)]
   if st==150:p.reverse()
   self.face('abutment closure '+str(st),p,cage=.16)
  # Two observed circular support shafts at the eastern lower promenade.
  for side in [-1,1]:
   st=D['main_pier_station'];t=side*5.9;self.tube('east pier '+str(side),(st,t,1.8),(st,t,grade(st,t)-1.05),.72,'concrete','deck',8 if coarse else 24,False,.16,1)
  # Main stays carry regular transverse ribs; underside geometry stops below slab.
  if not coarse:
   for st in D['fore_stations']:
    self.box('transverse rib '+str(st),(st-.22,-8.9,grade(st)-1.40),(st+.22,8.9,grade(st)-1.06),'concrete','deck',omit=('top',),cage=.18)
  # Backstay anchorage wedges: three separate sloping blocks on each terrace.
  for side in [-1,1]:
   for i,st in enumerate(D['back_stations']):
    t=side*(10.5+.80*i);base=grade(st,t);a,b=st-1.5,st+1.5;lo,hi=sorted((t-.6,t+.6));p=[(a,lo,base),(b,lo,base),(b,lo,base+1.9),(a,lo,base+.35),(a,hi,base),(b,hi,base),(b,hi,base+1.9),(a,hi,base+.35)]
    for j,ix in enumerate([(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7)]):self.face(f'backstay wedge {side} {i} {j}',[p[k]for k in ix],cage=.12)
 def stays(self,coarse=False):
  d=D;seg=4 if coarse else 12
  for side in [-1,1]:
   for family in ['fore','back']:
    for i,(st,z)in enumerate(zip(d[family+'_stations'],d[family+'_levels'])):
     if family=='fore':t=side*8.85;bottom=(st,t,grade(st,t)+.18);head=(d['pylon_station']-.77,side*(d['pylon_base_offset']+(d['pylon_top_offset']-d['pylon_base_offset'])*(z-d['pylon_base_z'])/(54.4-d['pylon_base_z'])-.65),z)
     else:t=side*(10.5+.8*i);bottom=(st+.65,t,grade(st,t)+1.45);head=(d['pylon_station']+.77,side*(d['pylon_base_offset']+(d['pylon_top_offset']-d['pylon_base_offset'])*(z-d['pylon_base_z'])/(54.4-d['pylon_base_z'])-.65),z)
     name=f'{family} stay {side} {i}';rad=.095 if family=='fore'else .125
     self.tube(name,bottom,head,rad,'white','fittings',seg,True,.05,.5)
     if not coarse:
      import numpy as np
      a,b=np.array(bottom),np.array(head);u=(b-a)/np.linalg.norm(b-a)
      # White protective sleeves are larger and fully hide the inner cable.
      self.tube('sleeve '+name,a,a+u*3.5,rad*1.65,'white','fittings',12,False,.05,.5)
      self.tube('collar '+name,a+u*3.5,a+u*3.57,rad*1.68,'dark','fittings',12,False,.05,.5)
      self.tube('socket '+name,a-u*.25,a+u*.22,rad*2.2,'cap','fittings',12,True,.05,.5)
      # Large sockets project outboard, so no plates duplicate the walkway.
      if family=='fore':self.box('anchor shoe '+name,(st-.32,t-.27,grade(st,t)-.12),(st+.32,t+.27,grade(st,t)+.10),'cap','deck',omit=('bottom',),cage=.1)
 def rails(self,coarse=False):
  import numpy as np
  d=D;ss=stations() if coarse else sorted(set([0.,*np.arange(3,150,3),*stations(),150.]));h=d['rail_height']
  for side in [-1,1]:
   # Independent District silhouette uses the same main post rhythm, not pickets.
   for k,(a,b)in enumerate(zip(ss,ss[1:])):
    for z in [.10,1.07]:
     self.tube(f'rail {side} {k} {z}',(a,side*width(a),grade(a,side*width(a))+z),(b,side*width(b),grade(b,side*width(b))+z),.037,'blue','fittings',4,False,.045,.3)
   for st in np.arange(0,150.01,3):
    t=side*width(st);z=grade(st,t);self.box(f'post {side} {st}',(st-.045,t-.045,z),(st+.045,t+.045,z+h),'blue','fittings',omit=('bottom',),cage=.04,weight=.3)
    if not coarse:
     # Each horn is a curved outboard continuation, with two tension-wire saddles.
     pts=[(st,t+side*q,z+H)for q,H in [(0,1.08),(.10,1.09),(.23,1.17),(.34,1.29)]]
     for j,(a,b)in enumerate(zip(pts,pts[1:])):self.tube(f'horn {side} {st} {j}',a,b,.024,'blue','fittings',6,False,.03,.3)
   if not coarse:
    for st in np.arange(.14,149.99,.14):
     if min(st%3,3-st%3)<.065:continue
     t=side*width(st);z=grade(st,t);self.box(f'picket {side} {st:.3f}',(st-.013,t-.016,z+.14),(st+.013,t+.016,z+1.032),'blue','fittings',omit=('bottom','top'),cage=.025,weight=.2)
    for offset,z in [(.23,1.17),(.34,1.29)]:
     for k,(a,b)in enumerate(zip(ss,ss[1:])):self.tube(f'wire {side} {offset} {k}',(a,side*(width(a)+offset),grade(a,side*width(a))+z),(b,side*(width(b)+offset),grade(b,side*width(b))+z),.007,'cap','fittings',4,False,.01,.2)
 def lamps(self,coarse=False):
  import numpy as np
  for side in [-1,1]:
   for i,st in enumerate(np.arange(6,148,9)):
    t=side*4.7;z=grade(st,t)
    self.tube(f'lamp stem {side} {i}',(st,t,z),(st,t,z+.81),.075,'grey','fittings',6 if coarse else 12,False,.06,.4)
    if coarse:continue
    self.tube(f'lamp lens {side} {i}',(st,t,z+.82),(st,t,z+.97),.047,'lamp','fittings',8,True,.03,.4)
    self.tube(f'lamp cap {side} {i}',(st,t,z+1.045),(st,t,z+1.075),.13,'grey','fittings',12,True,.04,.4)
    for j in range(3):
     a=j*math.tau/3;self.tube(f'lamp cage {side} {i} {j}',(st+.064*math.cos(a),t+.064*math.sin(a),z+.81),(st+.11*math.cos(a),t+.11*math.sin(a),z+1.045),.009,'grey','fittings',6,False,.02,.2)
 def pylons(self,coarse=False):
  for side in [-1,1]:self.leg(side,8 if coarse else 32,not coarse)
  d=D;p=d['pylon_station'];z=d['crosshead_bottom'];Z=d['crosshead_top']
  # The dark crosshead widens downward to meet both inclined leg interiors.
  lo,hi=2.70,1.15
  v=[(p-.75,-lo,z),(p+.75,-lo,z),(p+.75,lo,z),(p-.75,lo,z),(p-.75,-hi,Z),(p+.75,-hi,Z),(p+.75,hi,Z),(p-.75,hi,Z)]
  for j,ix in enumerate([(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]):self.face('dark anchorage crosshead '+str(j),[v[i]for i in ix],'dark','pylons',.15)
  if not coarse:
   for side in [-1,1]:
    for i in range(3):
     t=-1.1+i*1.1;self.tube(f'crosshead guard post {side} {i}',(p+side*.65,t,53.4),(p+side*.65,t,54.45),.022,'dark','pylons',8,True,.04)
    for z in [53.92,54.45]:self.tube(f'crosshead guard rail {side} {z}',(p+side*.65,-1.1,z),(p+side*.65,1.1,z),.022,'dark','pylons',8,True,.04)
