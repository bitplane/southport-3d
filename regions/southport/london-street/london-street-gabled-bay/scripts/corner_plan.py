"""Measured corner plan and independent low-complexity roof surface arrangement."""
import math

def clip(poly,fn):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa,fb=fn(a),fn(b)
  if fa>=-1e-8:out.append(a)
  if (fa>1e-8 and fb< -1e-8) or (fa< -1e-8 and fb>1e-8):
   t=fa/(fa-fb);out.append(tuple(a[j]+t*(b[j]-a[j]) for j in range(2)))
 return out if len(out)>=3 else []

def frame(poly,i):
 a,b=poly[i],poly[(i+1)%len(poly)];w=math.dist(a,b);u=((b[0]-a[0])/w,(b[1]-a[1])/w);n=(-u[1],u[0])
 return a,u,n,w

def signed_area(p):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2

def roof_faces(d):
 p=[tuple(q) for q in d['corner_footprint']];run=d['roof_run'];e=d['wall_height'];rise=d['ridge_height']-e
 fs=[frame(p,i) for i in range(4)]
 def dist(j,q):
  a,u,n,w=fs[j];return -sum((q[k]-a[k])*n[k] for k in range(2))
 result=[]
 def emit(name,poly,z):
  if len(poly)<3 or abs(signed_area(poly))<1e-7:return
  if signed_area(poly)<0:poly=list(reversed(poly))
  result.append((name,[(x,y,z((x,y))) for x,y in poly]))
 for j,(a,u,n,w) in enumerate(fs):
  cell=p
  for k in range(4):
   if k!=j:cell=clip(cell,lambda q,k=k:dist(k,q)-dist(j,q))
  front=clip(cell,lambda q:run-dist(j,q));parts=[front]
  facade=next((f for f in d['facades'] if f['edge']==j),None)
  for c,h in (facade['gables'] if facade else []):
   def U(q):return sum((q[k]-a[k])*u[k] for k in range(2))
   # Cross gable triangular domain. Split each remaining base polygon outside
   # it; two gable planes meet along their ridge, never overlap the base slope.
   cuts=[lambda q,c=c,h=h:1-dist(j,q)/run-(U(q)-c)/h,lambda q,c=c,h=h:1-dist(j,q)/run+(U(q)-c)/h]
   remainder=[]
   for poly in parts:
    inside=poly
    for cut in cuts:
     outside=clip(inside,lambda q,cut=cut:-cut(q))
     if outside:remainder.append(outside)
     inside=clip(inside,cut)
    for side in (-1,1):
     half=clip(inside,lambda q,side=side,c=c:side*(U(q)-c))
     emit(f'gable {j} {c} {side}',half,lambda q,c=c,h=h:e+rise*(1-abs(U(q)-c)/h))
   parts=remainder
  for poly in parts:emit(f'front pitch {j}',poly,lambda q:e+rise*dist(j,q)/run)
  back=clip(clip(cell,lambda q:dist(j,q)-run),lambda q:2*run-dist(j,q))
  emit(f'back pitch {j}',back,lambda q:e+rise*(2-dist(j,q)/run))
  inner=clip(cell,lambda q:dist(j,q)-2*run)
  emit(f'inner flat {j}',inner,lambda q:e)
 return result

def world(d,p):
 x,y,z=p;px,py=d['registration_pivot'];a=d['registration_radians']
 return (px+math.cos(a)*(x-px)-math.sin(a)*(y-py),py+math.sin(a)*(x-px)+math.cos(a)*(y-py),z+d['base_z'])
