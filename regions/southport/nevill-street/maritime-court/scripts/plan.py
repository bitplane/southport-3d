"""Measured plan controls shared by detailed architecture and fixed receivers."""
import json,math
from pathlib import Path
D=json.loads((Path(__file__).resolve().parents[1]/'research/layout.json').read_text())
def world(p):
 x,y,z=p;a,b=D['u_axis'],D['v_axis'];o=D['origin_site']
 return (o[0]+a[0]*x+b[0]*y,o[1]+a[1]*x+b[1]*y,z+D['base'])
def outline():
 w,d,t=D['width'],D['depth'],D['wing']
 return [(0,0),(w,0),(w,t),(t,t),(t,d),(0,d)]
def facade(i):
 p=outline();a=p[i];b=p[(i+1)%6];l=math.dist(a,b);u=((b[0]-a[0])/l,(b[1]-a[1])/l)
 def at(x,z,o=0):return(a[0]+u[0]*x+u[1]*o,a[1]+u[1]*x-u[0]*o,z)
 return l,at
# Bay measurements are fixed architectural controls, independent of ornament density.
TALL={0:[14,24,34,44],1:[],2:[5.1,15.1,25.1],3:[4,12,20],4:[],5:[5.0,15.0,25.0,35.0]}
SMALL={0:[(4,.85),(9,1.7),(19,1.9),(20.95,1.1),(29,1.9),(30.95,1.1),(39,1.8),(40.95,1.0)],1:[(13.8,.8)],2:[(1.2,1.3),(10.1,1.7),(20.1,1.7),(29,1.2)],3:[(8,1.5),(16,1.5),(23,1.1)],4:[(3,1.5),(8.3,.65),(15.3,1.4)],5:[(1.2,1),(10,1.8),(12.0,1),(20,1.8),(22.0,1),(30,1.8),(32.0,1),(39.2,.8)]}
def strips(i):
 l,_=facade(i);cuts={0.,l}
 for x in TALL[i]:cuts.update([max(0,x-2.2),x-1.35,x+1.35,min(l,x+2.2)])
 # Slim pilasters between paired small windows, only street elevations.
 for x,w in SMALL[i]:
  if w<1.2 and i in (0,5) and x>6:cuts.update([x-.9,x-.65])
 cuts=sorted(cuts);out=[]
 for a,b in zip(cuts,cuts[1:]):
  c=(a+b)/2;pier=any(1.35<abs(c-x)<2.21 for x in TALL[i]);slim=any(x-.91<c<x-.64 for x,w in SMALL[i] if w<1.2 and x>6) and i in (0,5)
  out.append((a,b,1.0 if pier else (.18 if slim else 0),D['parapet'] if pier else D['roof']))
 return out
