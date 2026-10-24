"""Fixed-budget T-shaped envelope sharing dimensions, never detailed topology."""
import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());A=d['front_left'];W=A+d['front_width'];B=d['back'];Y=d['wing_start'];Z=d['wing_end'];R=d['rear_strip_left']
 def T(p):x,y,z=p;return d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x,d['base_z']+z
 s=Surfaces(['lord','nevill','rear','roof','canopy'],T)
 def face(name,p,side,**kw):
  q=[(A+u,-out,z) for u,z,out in p] if side=='lord' else list(reversed([(-out,Y+u,z) for u,z,out in p]))
  s.quad(name,q,**kw)
 def panel(name,a,b,lo,hi,out,side,**kw):face(name,[(a,lo,out),(b,lo,out),(b,hi,out),(a,hi,out)],side,**kw)
 for part,width,top in [('lord',d['front_width'],13.35),('nevill',Z-Y,17.1)]:
  s.part=part
  # One frontage owns all its masonry, glazing and shopfront at every level.
  panel(part+' lower frontage',0,width,0,4.5,.025,part,cage=.38)
  panel(part+' upper frontage',0,width,4.5,top,.015,part,cage=.48)
  face(part+' parapet cap',[(0,top,.10),(width,top,.10),(width,top,-.24),(0,top,-.24)],part,cage=.20,weight=.4)
 # Main cornices preserve their projection; balcony slabs remain silhouette geometry.
 s.part='lord';panel('main cornice',0,d['front_width'],11.85,12.38,.32,'lord',cage=.30)
 s.part='nevill'
 for i,u in enumerate(d['boots_bays']):
  for j,z in enumerate((4.53,9.66)):
   # Keep platform and a thin railing band; crossed infill becomes baked appearance.
   face(f'balcony slab top {i} {j}',[(u-1.455,z+.11,-.135),(u+1.455,z+.11,-.135),(u+1.455,z+.11,.915),(u-1.455,z+.11,.915)],'nevill',cage=.22,weight=.6)
   face(f'balcony soffit {i} {j}',[(u-1.455,z-.11,.915),(u+1.455,z-.11,.915),(u+1.455,z-.11,-.135),(u-1.455,z-.11,-.135)],'nevill',cage=.22,weight=.5)
   panel(f'balcony edge {i} {j}',u-1.455,u+1.455,z-.11,z+.11,.915,'nevill',cage=.22,weight=.5)
   # Thin disconnected rail remains open below, without a filled balcony box.
   panel(f'balcony rail {i} {j}',u-1.38,u+1.38,z+.86,z+.92,.91,'nevill',cage=.12,weight=.4)
 s.part='rear'
 boundaries=[((W,0),(W,9.5),12.3),((W,9.5),(W,Y),10.1),((W,Y),(W,Z),16.1),((W,Z),(W,48),14.25),((W,48),(W,B),17.1),((W,B),(R,B),17.1),((R,B),(R,48),17.1),((R,48),(R,Z),14.25),((R,Z),(0,Z),16.1),((0,Y),(A,Y),16.1),((A,Y),(A,9.5),10.1),((A,9.5),(A,0),12.3)]
 for i,(a,b,h) in enumerate(boundaries):s.quad('external '+str(i),[(*a,0),(*b,0),(*b,h),(*a,h)],cage=.30)
 s.part='roof';e=d['front_eaves'];h=d['front_ridge'];depth=d['roof_front_depth'];ridge=depth/2;hip=2.6
 s.quad('front slate',[(A,0,e),(W,0,e),(W-hip,ridge,h),(A+hip,ridge,h)],cage=.15)
 s.triangle('right hip',[(W,0,e),(W,depth,e),(W-hip,ridge,h)],cage=.15)
 s.quad('back slate',[(W,depth,e),(A,depth,e),(A+hip,ridge,h),(W-hip,ridge,h)],cage=.15)
 s.triangle('left hip',[(A,depth,e),(A,0,e),(A+hip,ridge,h)],cage=.15)
 for name,x0,x1,y0,y1,zz in [('link',A,W,depth,Y,10.1),('Boots',0,W,Y,Z,16.1),('rear service',R,W,Z,48,14.25),('rear tower',R,W,48,B,17.1)]:s.quad(name,[(x0,y0,zz),(x1,y0,zz),(x1,y1,zz),(x0,y1,zz)],cage=.25)
 for name,p in [('front back',[(A,depth,10.1),(W,depth,10.1),(W,depth,e-.12),(A,depth,e-.12)]),('Boots front',[(A,Y,10.1),(W,Y,10.1),(W,Y,15.98),(A,Y,15.98)]),('Boots rear',[(R,Z,14.25),(W,Z,14.25),(W,Z,15.98),(R,Z,15.98)]),('tower step',[(R,48,14.25),(W,48,14.25),(W,48,16.98),(R,48,16.98)])]:s.quad(name,p,cage=.20)
 # Raised perimeter walls are silhouette geometry, not texture-only detail.
 for i,(x0,x1,y0,y1,z0,z1) in enumerate([(W-.25,W,Y,Z,16.1,16.72),(.25,W-.25,Z-.25,Z,16.1,16.72),(.25,W-.25,Y,Y+.25,16.1,16.72),(R,R+.20,Z,48,14.25,14.70),(W-.20,W,Z,48,14.25,14.7)]):
  s.box('parapet '+str(i),(x0,y0,z0+.002),(x1,y1,z1),cage=.12,weight=.6)
 rl=d['rooflight'];x0,x1=rl['x'];y0,y1=rl['y'];zz=rl['base'];ap=rl['apex'];cx=(x0+x1)/2;cy=(y0+y1)/2
 s.box('lantern curb',(x0-.175,y0-.175,16.1),(x1+.175,y1+.175,16.5),cage=.2,weight=.5)
 p=[(x0,y0,zz),(x1,y0,zz),(x1,y1,zz),(x0,y1,zz)]
 for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):s.triangle('lantern '+str(i),[a,b,(cx,cy,ap)],cage=.18)
 s.box('chimney',(W-1.15,6.10,13.8),(W-.05,7.70,16.80),cage=.30)
 for i,dx in enumerate((-.29,.29)):
  for j,dy in enumerate((-.52,0,.52)):s.box(f'pot {i} {j}',(W-.60+dx-.12,6.9+dy-.12,16.80),(W-.60+dx+.12,6.9+dy+.12,17.4),cage=.18,weight=.4)
 # Only major rooftop plant, not every grille or pipe.
 s.box('link plant',(17,16.5,10.1),(19,19.5,11.3),cage=.20,weight=.6)
 for i,y in enumerate((28,30,32)):s.box('cooler '+str(i),(2.5,y-.575,16.1),(3.5,y+.575,17.1),cage=.20,weight=.5)
 s.part='canopy'
 for side,width,positions in [('lord',d['front_width'],[.25,4.20,8.80,d['front_width']-.22]),('nevill',Z-Y,[.28,Z-Y-.28])]:
  n=3
  outer=3.68 if side=='lord' else 4.00;fascia=3.51 if side=='lord' else 3.25
  for j in range(n):
   a=width*j/n;b=width*(j+1)/n
   face(f'{side} roof {j}',[(a,outer,3.02),(b,outer,3.02),(b,4.58,.10),(a,4.58,.10)],side,cage=.15)
   face(f'{side} underside {j}',[(a,4.545,.10),(b,4.545,.10),(b,outer-.035,3.02),(a,outer-.035,3.02)],side,cage=.15,weight=.5)
   panel(f'{side} fascia {j}',a,b,fascia-.13,fascia+.13,3.02,side,cage=.15,weight=.5)
  for i,u in enumerate(positions):
   for j in range(6):
    a=math.tau*j/6;b=math.tau*(j+1)/6
    face(f'{side} post {i} {j}',[(u+.07*math.cos(a),0,3.02+.07*math.sin(a)),(u+.07*math.cos(b),0,3.02+.07*math.sin(b)),(u+.07*math.cos(b),fascia-.08,3.02+.07*math.sin(b)),(u+.07*math.cos(a),fascia-.08,3.02+.07*math.sin(a))],side,cage=.16,weight=.5)
 return s.result
