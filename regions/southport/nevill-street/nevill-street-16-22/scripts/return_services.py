"""Estimated extraction run from July 2026 Stanley Street imagery.
The two bends return into/around the wall; there are no exposed flat end caps.
Small joint collars and suspended brackets remain Detail/Walk geometry.
"""
import math
DUCT_Z=3.18
DUCT_RADIUS=.16

def planar_tube(m,pts,radius,sides=20):
 # Fixed vertical frame avoids ring twisting where a bend meets a wall-normal leg.
 vertices=[]
 for i,(u,z,out) in enumerate(pts):
  before=pts[max(0,i-1)];after=pts[min(len(pts)-1,i+1)]
  du=after[0]-before[0];do=after[2]-before[2];length=math.hypot(du,do);du/=length;do/=length
  for j in range(sides):
   a=math.tau*j/sides;vertices.append((u-radius*do*math.cos(a),z-radius*math.sin(a),out+radius*du*math.cos(a)))
 faces=[tuple(reversed(range(sides)))]
 for i in range(len(pts)-1):
  for j in range(sides):
   a=i*sides+j;b=i*sides+(j+1)%sides;faces.append((a,b,b+sides,a+sides))
 faces.append(tuple((len(pts)-1)*sides+j for j in range(sides)));m.add(vertices,faces)

def build(api):
 Mesh,finish,box,SIDE,steel,iron=api
 pts=[(-.36,DUCT_Z,-.35),(-.36,DUCT_Z,.20)]
 for j in range(1,9):
  a=math.pi-math.pi/2*j/8;pts.append((-.01+.35*math.cos(a),DUCT_Z,.20+.35*math.sin(a)))
 pts.append((4.45,DUCT_Z,.55))
 for j in range(1,9):
  a=math.pi/2-math.pi/2*j/8;pts.append((4.45+.35*math.cos(a),DUCT_Z,.20+.35*math.sin(a)))
 pts.append((4.8,DUCT_Z,-.12))
 m=Mesh('Architecture return duct');planar_tube(m,pts,DUCT_RADIUS);finish(m,material=steel,frame=SIDE)
 for u in (.35,2.3,4.25):
  m=Mesh('Architecture return duct collar');m.tube([(u-.03,DUCT_Z,.55),(u+.03,DUCT_Z,.55)],.174,sides=20);finish(m,material=steel,frame=SIDE)
 for u in (.45,2.25,4.2):
  box('Architecture return duct bracket',(u,3.43,.30),(.045,.26,.045),iron,frame=SIDE)
  box('Architecture return duct bracket foot',(u,3.32,.42),(.045,.04,.24),iron,frame=SIDE)
