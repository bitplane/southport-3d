"""Fixed independent envelope; dimensions and segment counts never depend on Detail."""
import json,math
from mathutils import Vector
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());ox,oy=d['origin_site_xy'];ux,uy=d['x_axis_site'];vx,vy=d['y_axis_site'];g=d['ground_datum_m']
 def P(p):x,y,z=p;return (ox+ux*x+vx*y,oy+uy*x+vy*y,g+z)
 s=Surfaces(['building'],P)
 def wing(x):return 3.8-1.12*(abs(x)/11.25)**2.6
 def barrel(x):return 4.12+.53*(1-(x/2.8)**2)
 def q(name,pts):
  # mirrored X/Y frame, with explicit principal wall outward normals
  a,b,c=map(Vector,pts[:3]);n=(b-a).cross(c-a)
  if abs(n.y)>1e-9 and max(p[1] for p in pts)-min(p[1] for p in pts)<1e-7 and abs(pts[0][1])>5:
   if n.y*pts[0][1]<0:pts=list(reversed(pts))
  elif abs(n.x)>1e-9 and max(p[0] for p in pts)-min(p[0] for p in pts)<1e-7 and abs(pts[0][0])>2.7:
   if n.x*pts[0][0]<0:pts=list(reversed(pts))
  s.quad(name,list(reversed(pts)))
 def tri(name,pts):s.triangle(name,list(reversed(pts)))
 for y,segments in [(6.5,[(-10.84,-2.8),(2.87,11.5)]),(-6,[(-10.84,-2.04),(2.04,11.5)])]:
  for a,b in segments:
   xs=[a+(b-a)*i/6 for i in range(7)]
   for p,r in zip(xs[:-1],xs[1:]):q('wing wall',[(p,y,0),(r,y,0),(r,y,wing(r)),(p,y,wing(p))])
 for x in [-10.84,11.5]:q('end wall',[(x,-6,0),(x,6.5,0),(x,6.5,wing(x)),(x,-6,wing(x))])
 for a,b in [(-10.84,-2.8),(2.87,11.5)]:
  xs=[a+(b-a)*i/8 for i in range(9)]
  for p,r in zip(xs[:-1],xs[1:]):q('wing roof',[(p,-6.20,wing(p)),(r,-6.20,wing(r)),(r,6.70,wing(r)),(p,6.70,wing(p))])
 # Retain two actual entrance openings rather than filling central frontage.
 for a,b in [(-2.8,-1.1),(1.1,2.87)]:q('entry door',[(a,6.5,0),(b,6.5,0),(b,6.5,2.3),(a,6.5,2.3)])
 q('entry infill',[(-1.1,6.5,0),(1.1,6.5,0),(1.1,6.5,2.30),(-1.1,6.5,2.30)])
 q('entry transom',[(-2.8,6.5,2.30),(2.8,6.5,2.30),(2.8,6.5,3.57),(-2.8,6.5,3.57)])
 for a,b in zip([-2.8,-1.4,0,1.4],[-1.4,0,1.4,2.8]):
  q('arched sign',[(a,6.5,3.57),(b,6.5,3.57),(b,6.5,barrel(b)-.10),(a,6.5,barrel(a)-.10)])
 for i in range(8):
  a=-2.8+5.6*i/8;b=-2.8+5.6*(i+1)/8
  q('barrel roof',[(a,-6,barrel(a)),(b,-6,barrel(b)),(b,8.85,barrel(b)),(a,8.85,barrel(a))])
 for x in [-2.8,2.8]:q('barrel cheek',[(x,-6,3.86),(x,8.85,3.86),(x,8.85,barrel(x)),(x,-6,barrel(x))])
 r=4.05;cy=-9.5;alpha=math.asin(3.5/r);A=[math.pi-alpha+(math.pi+2*alpha)*i/18 for i in range(19)]
 for a,b in zip(A[:-1],A[1:]):
  x0,y0=r*math.cos(a),cy+r*math.sin(a);x1,y1=r*math.cos(b),cy+r*math.sin(b)
  q('rear drum wall',[(x0,y0,0),(x1,y1,0),(x1,y1,4.24),(x0,y0,4.24)])
  tri('rear drum roof',[(0,cy,4.24),(x0,y0,4.24),(x1,y1,4.24)])
 r=1.1;cy=7.5;A=[math.pi*i/12 for i in range(13)]
 for a,b in zip(A[:-1],A[1:]):
  x0,y0=r*math.cos(a),cy+r*math.sin(a);x1,y1=r*math.cos(b),cy+r*math.sin(b)
  q('kiosk wall',[(x0,y0,0),(x1,y1,0),(x1,y1,2.13),(x0,y0,2.13)])
  tri('kiosk roof',[(0,cy,2.13),(x0,y0,2.13),(x1,y1,2.13)])
 return s.result
