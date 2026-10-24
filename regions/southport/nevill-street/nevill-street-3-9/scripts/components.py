"""Nevill 3–9 segmental arches, stone profiles and compact foliage abstractions."""
import math
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cut(poly,holes):
 parts=[poly]
 for h in holes:parts=[q for p in parts for q in subtract(p,h)]
 return parts

def arch(u,bottom,spring,rx,rise,n=20):
 return [(u-rx,bottom),(u+rx,bottom)]+[(u+rx*math.cos(math.pi*i/n),spring+rise*math.sin(math.pi*i/n)) for i in range(n+1)]

def ring(m,u,z,rx,ry,thick,out,depth,n=24):
 v=[]
 for i in range(n+1):
  t=math.pi*i/n
  for d in (out-depth,out):
   for x,y in [(rx,ry),(rx+thick,ry+thick)]:v.append((u+x*math.cos(t),z+y*math.sin(t),d))
 f=[]
 for i in range(n):
  a=i*4;b=a+4;f.extend([(a+2,a+3,b+3,b+2),(a,b,b+1,a+1),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 f.extend([(0,1,3,2),(4*n+2,4*n+3,4*n+1,4*n)])
 m.add(v,f)

def profile(m,a,b,z,p):
 if sum(x[0]*y[1]-y[0]*x[1] for x,y in zip(p,p[1:]+p[:1]))<0:p=list(reversed(p))
 n=len(p);v=[(u,z+h,d) for u in (a,b) for h,d in p]
 m.add(v,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])

def leaf(m,x,z,out,length,angle,width):
 # Curved, lobed low-relief acanthus leaves; approximate carving, not a scan.
 dx,dz=math.sin(angle),math.cos(angle);ox,oz=math.cos(angle),-math.sin(angle)
 verts=[];faces=[];rows=10;cols=4
 for i in range(rows+1):
  t=i/rows
  breadth=width*(.10+.90*math.sin(math.pi*t)**.65)*(1+.20*math.sin(6*math.pi*t))
  reach=length*(t-.09*t**5)
  for j in range(cols+1):
   a=2*j/cols-1
   relief=.022+.065*math.sin(math.pi*t)*(1-.65*abs(a))+.07*t**5
   verts.append((x+dx*reach+ox*breadth*a,z+dz*reach+oz*breadth*a,out+relief))
 for i in range(rows):
  for j in range(cols):
   a=i*(cols+1)+j;faces.append((a,a+1,a+cols+2,a+cols+1))
 m.add(verts,faces)
