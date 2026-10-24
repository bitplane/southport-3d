"""Fixed cinema envelope; photographs supply appearance, not mesh complexity."""
import json, math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());a=math.radians(d['rotation_degrees']);c=math.cos(a);sn=math.sin(a)
 def T(p):
  x,y,z=p
  return d['origin_site_xy'][0]+c*x-sn*y,d['origin_site_xy'][1]+sn*x+c*y,d['base_z']+z
 s=Surfaces(['walls','roof','joinery'],T);poly=d['footprint_uv'];W=d['front_width'];H=d['eaves'];u=d['door_u']
 def front(name,x,X,z,Z,y=0):s.quad(name,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z)])
 # Preserve the deep porch entry while small window reveals project into walls.
 front('front left',0,u-1.55,0,H);front('front right',u+1.55,W,0,H)
 front('above porch',u-1.55,u+1.55,3.42,H)
 front('porch left',u-1.55,u-.86,0,3.42,-.75)
 front('porch right',u+.86,u+1.55,0,3.42,-.75)
 front('porch door head',u-.86,u+.86,3.22,3.42,-.75)
 # Fanlight curve remains a coarse six-segment opening; no solid wall across it.
 pts=[(u+.86*math.cos(i*math.pi/6),2.36+.86*math.sin(i*math.pi/6)) for i in range(7)]
 for i,(p,q) in enumerate(zip(pts,pts[1:])):
  face=[(q[0],-.75,q[1]),(p[0],-.75,p[1]),(p[0],-.75,3.22),(q[0],-.75,3.22)]
  if i==2:face=face[1:]
  if i==3:face=[face[0],face[1],face[3]]
  (s.triangle if len(face)==3 else s.quad)('arch spandrel '+str(i),face)
 for x in (u-1.55,u+1.55):
  p=[(x,0,0),(x,-.75,0),(x,-.75,3.42),(x,0,3.42)]
  s.quad('porch cheek '+str(x),p if x>u else list(reversed(p)))
 s.triangle('pediment',[(u-1.63,-.89,3.24),(u+1.63,-.89,3.24),(u,-.89,4.18)])
 front('backing central',u-1.05,u+1.05,3.42,4.28,-.8)
 for x,X in [(u-1.55,u-1.05),(u+1.05,u+1.55)]:front('backing shoulder '+str(x),x,X,3.42,3.56,-.8)
 pts=[(u+.79*math.cos(i*math.pi/6),2.36+.79*math.sin(i*math.pi/6)) for i in range(7)]
 s.part='joinery';front('door',u-.79,u+.79,0,2.36,-.28)
 front('left door jamb',u-.86,u-.79,0,2.36,-.33)
 front('right door jamb',u+.79,u+.86,0,2.36,-.33)
 for i,(p,q) in enumerate(zip(pts,pts[1:])):
  s.triangle('fanlight '+str(i),[(u,-.28,2.36),(p[0],-.28,p[1]),(q[0],-.28,q[1])])
 s.part='walls'
 s.quad('door threshold',[(u-.91,-.87,0),(u+.91,-.87,0),(u+.91,.03,0),(u-.91,.03,0)])
 for i in range(1,len(poly)):
  p,q=poly[i],poly[(i+1)%len(poly)]
  s.quad('wall '+str(i),[(*p,0),(*q,0),(*q,H),(*p,H)])
 A=(0,0,H);B=(W,0,H);RC=(13.38,18.47,H);D=(2.25,19.11,H);E=(1.68,9.09,H);G=(-.87,9.15,H)
 S=(12.49,9.12,H);R0=(5.8,4.5,d['ridge']);R1=(6.2,9.12,d['ridge']);R2=(7.815,18.79,d['ridge'])
 s.triangle('east gable',[RC,D,R2]);s.part='roof'
 for i,f in enumerate([[A,B,R0],[B,S,R1,R0],[S,RC,R2,R1],[D,E,R1,R2],[E,G,R1],[G,A,R0,R1]]):
  (s.triangle if len(f)==3 else s.quad)('roof '+str(i),f)
 for i,p in enumerate(poly):
  q=poly[(i+1)%len(poly)];s.quad('fascia '+str(i),[(*q,H),(*p,H),(*p,H-.12),(*q,H-.12)])
 for x,y in [(11.8,15.0),(10.,6.2)]:s.box('stack '+str(x),(x-.31,y-.415,8.0),(x+.31,y+.415,9.7))
 inner=lambda v:11.63+(13.38-11.63)*v/18.47
 q=[(inner(1),1),(inner(1)+2.9,1),(inner(9.1)+2.9,9.1),(inner(9.1),9.1)]
 s.quad('lean-to roof',[(*q[0],4.15),(*q[1],3.15),(*q[2],3.15),(*q[3],4.15)]);s.part='walls'
 for i in range(3):s.quad('lean-to wall '+str(i),[(*q[i],0),(*q[i+1],0),(*q[i+1],3.15),(*q[i],3.15)])
 for i,(p,q1) in enumerate([(q[0],q[1]),(q[3],q[2])]):s.triangle('lean-to wedge '+str(i),[(*p,3.15),(*q1,3.15),(*p,4.15)])
 s.part='walls'
 for name,p,q in [('south',(4.10,-10),(4.10,0)),('north',(1,0),(1,-10)),('west',(1,-10),(4.10,-10))]:
  h=3.5 if name=='north' else 3.2
  s.quad('access range '+name,[(*p,0),(*q,0),(*q,h),(*p,h)])
 s.triangle('access range west wedge',[(1,-10,3.2),(4.10,-10,3.2),(1,-10,3.5)])
 s.part='roof';s.quad('access range roof',[(1,-10,3.5),(4.10,-10,3.2),(4.10,0,3.2),(1,0,3.5)])
 return s.result
