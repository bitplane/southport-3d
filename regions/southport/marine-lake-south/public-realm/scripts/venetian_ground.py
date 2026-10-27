"""Bounded, editable landings and lower-path grades at the Venetian Bridge.

The surrounding rough road grid is not a surveyed lake-edge level. These
small transition surfaces blend to that grid at their boundaries, while the
bridge deck and the lower path remain independent support layers.
"""
import json,math
from pathlib import Path
from southport3d.planar import halfplane,area

# One authored frame for the floor, fascia, fittings, stairs and UVs. The two
# endpoints and width live in the layout; the elevation profile must use the
# same axis. The cap of a .45 m pier just reaches the outer edge of the deck.
LAYOUT=json.loads((Path(__file__).resolve().parents[1]/'research/layout.json').read_text())
assert len(LAYOUT['venetian_axis'])==2, 'Venetian centreline must be straight'
A,B=map(tuple,LAYOUT['venetian_axis']);L=math.dist(A,B)
WIDTH=LAYOUT['venetian_width_m'];HALF_WIDTH=WIDTH/2
RAIL_OFFSET=HALF_WIDTH-.225
# The oblique reference shows green metal railings where the deck crosses the
# islands; their exact station limits and lamp registration remain estimates.
GREEN_SECTIONS=((45.19,64.81),(95.19,114.81))
GREEN_STANDARDS=(55,105)
PIERS=tuple(sorted([.23,L-.23,80]+[5+10*i for i in range(16) if 5+10*i not in GREEN_STANDARDS]))
RAIL_START=PIERS[0]+.19;RAIL_END=PIERS[-1]-.19
def green_at(t):return any(lo<t<hi for lo,hi in GREEN_SECTIONS)
U=((B[0]-A[0])/L,(B[1]-A[1])/L);V=(-U[1],U[0])
def at(t,o=0):return (A[0]+U[0]*t+V[0]*o,A[1]+U[1]*t+V[1]*o)
def local(x,y):
 dx=x-A[0];dy=y-A[1];return dx*U[0]+dy*U[1],dx*V[0]+dy*V[1]
def assert_frame(bridge):
 assert math.dist(bridge.origin,A)<1e-8 and math.dist(bridge.axis,U)<1e-8, 'Deck profile and Venetian centreline differ'
 assert abs(bridge.stations[0])<1e-8 and abs(bridge.stations[-1]-L)<1e-8, 'Deck profile does not cover the full Venetian axis'
 assert abs(bridge.crossfall)<1e-12, 'Rail contacts assume zero bridge crossfall'
def polygon(t0,t1,o0,o1):return [at(t0,o0),at(t1,o0),at(t1,o1),at(t0,o1)]
def clamp(v):return max(0.,min(1.,v))
class Transition:
 def __init__(self,base,bridge,kind):
  self.base=base;self.bridge=bridge;self.kind=kind;self.name='venetian-'+kind;self.bounds=base.bounds
  if kind=='landing':self.ts=list(range(-35,27,2))+[0,15,25];self.os=list(range(-20,21,2))+[-3,3]
  else:self.ts=list(range(138,165))+[149,153];self.os=list(range(-26,27,2))+[-3,3]
 def height(self,x,y):
  t,o=local(x,y);natural=self.base.height(x,y)
  if self.kind=='landing':
   alpha=clamp((t+35)/35)*clamp((25-t)/10)*clamp((20-abs(o))/17)
   if alpha==0:return natural
   target=self.bridge.height(x,y)
  else:
   alpha=clamp((t-138)/11)*clamp((164-t)/11)*clamp((26-abs(o))/23)
   target=-1.8
  return natural+(target-natural)*alpha
 def contains(self,x,y,tolerance=1e-7):return self.base.contains(x,y,tolerance)
 def lift_triangle(self,tri):
  # Refine both the underlying control grid and the transition breaklines.
  for base in self.base.lift_triangle(tri):
   pieces=[[p[:2] for p in base]]
   lines=[(at(t,-1),at(t,1)) for t in sorted(set(self.ts))]+[(at(-1,o),at(1,o)) for o in sorted(set(self.os))]
   for a,b in lines:
    divided=[]
    for p in pieces:
     ds=[(b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0]) for q in p]
     if min(ds)<-1e-9 and max(ds)>1e-9:divided.extend(q for side in (True,False) if len(q:=halfplane(p,a,b,side))>=3 and area(q)>1e-10)
     else:divided.append(p)
    pieces=divided
   for p in pieces:
    for i in range(1,len(p)-1):
     q=(p[0],p[i],p[i+1])
     if area(q)>1e-10:yield [(x,y,self.height(x,y)) for x,y in q]
 def edge_points(self,a,b):
  # Include all authored grade breaks and the rough grid's breaks.
  points={tuple(p[:2]) for p in self.base.edge_points(a,b)}
  ta,oa=local(*a);tb,ob=local(*b)
  for start,end,breaks in ((ta,tb,self.ts),(oa,ob,self.os)):
   if abs(end-start)>1e-10:
    for q in breaks:
     f=(q-start)/(end-start)
     if 0<f<1:points.add((a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1])))
  for x,y in sorted(points,key=lambda p:(p[0]-a[0])**2+(p[1]-a[1])**2):yield x,y,self.height(x,y)
