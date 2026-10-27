"""Bounded independent district model with courtyard, door and stepped roof."""
from blender_envelope import Surfaces

def surfaces(asset):
 s=Surfaces(['architecture'],lambda p:(p[0]+.0367*(p[1]+25.45),p[1],p[2]))
 x0,x1=-286.4,-266.24;y0,y1=-46.42,-25.45;z=.1
 def wall(name,a,b,lo,hi):s.quad(name,[(a[0],a[1],hi+z),(b[0],b[1],hi+z),(b[0],b[1],lo+z),(a[0],a[1],lo+z)])
 # Street door remains physically recessed, not a projected solid front.
 for name,a,b in [('front-left',x0,-280.675),('front-right',-279.725,x1-2.4)]:wall(name,(a,y1),(b,y1),0,11.5)
 wall('front door head',(-280.675,y1),(-279.725,y1),2.36,11.5)
 wall('recessed door',(-280.675,y1-.30),(-279.725,y1-.30),0,2.36)
 for x in (-280.675,-279.725):s.quad('door reveal '+str(x),[(x,y1,0+z),(x,y1-.3,0+z),(x,y1-.3,2.36+z),(x,y1,2.36+z)])
 wall('corner ground front',(x1-2.4,y1),(x1,y1),0,3.55)
 wall('corner ground side',(x1,y1),(x1,y1-2.4),0,3.55)
 outline=[(x1,y1-2.4),(x1,y0),(-281.0,y0),(-281.0,-38.94),(-276.1,-38.94),(-276.1,-32.7),(x0,-32.7),(x0,y1)]
 for i,(a,b) in enumerate(zip(outline,outline[1:])):wall('wall '+str(i),a,b,0,11.5)
 # A fixed control grid samples the union of three raised mansard roof
 # envelopes. It deliberately has no dependence on small master features.
 xs=[x0,-283,-281,-279,-276.1,-273,-271.1,-269,-266.24]
 ys=[y0,-44,-41,-38.94,-36,-33,-32.7,-30,-28,-25.45]
 rects=[(x0,x1,-32.7,y1,16.2),(-276.1,x1,y0,y1,16.5),(-281.,-276.1,y0,-38.94,16.2)]
 def inside(x,y,r):return r[0]-1e-8<=x<=r[1]+1e-8 and r[2]-1e-8<=y<=r[3]+1e-8
 def roof(x,y):
  levels=[]
  for a,b,c,d,r in rects:
   if inside(x,y,(a,b,c,d)):
    dist=min(x-a,b-x,y-c,d-y);levels.append(11.5+dist*1.21 if dist<1.65 else 15.15+min(r-15.15,(dist-1.65)*.3))
  return (max(levels) if levels else 11.5)+z
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(ys,ys[1:]):
   if not any(inside((a+b)/2,(c+d)/2,r) for r in rects):continue
   s.quad('roof %s %s'%(a,c),[(a,c,roof(a,c)),(b,c,roof(b,c)),(b,d,roof(b,d)),(a,d,roof(a,d))])
 # Dominant Dutch-gable silhouettes and corner tower stand above the eave.
 def district_gable(u,axis):
  # Fixed polygonal approximation of the Dutch shoulders and rounded crown;
  # its silhouette remains independent of the detailed moulding topology.
  rings=[(11.5,1.55),(12.48,1.05),(13.60,.95),(14.70,.60)]
  def p(v,h):return (u+v,y1,h+z) if axis=='x' else (x1,u+v,h+z)
  for i,((h0,w0),(h1,w1)) in enumerate(zip(rings,rings[1:])):
   points=[p(-w0,h0),p(w0,h0),p(w1,h1),p(-w1,h1)]
   if axis=='x':points.reverse()
   s.quad('gable %s %s band %s'%(axis,u,i),points)
  points=[p(-.60,14.70),p(.60,14.70),p(0,15.10)]
  if axis=='x':points.reverse()
  s.triangle('gable %s %s crown'%(axis,u),points)
 for x in (-283,-273.2):district_gable(x,'x')
 for y in (-32.8,-40.0):district_gable(y,'y')
 # Faceted corner tower continues above the body, with the lower part
 # left open to the storefront below. The generator is fixed complexity.
 tower=[(x1-2.4,y1),(x1-.8,y1),(x1,y1-.8),(x1,y1-2.4)]
 for i,(a,b) in enumerate(zip(tower,tower[1:])):wall('tower '+str(i),a,b,3.55,14.65)
 centre=(x1-1.2,y1-1.2,17.0+z)
 for i,(a,b) in enumerate(zip(tower,tower[1:])):s.triangle('turret roof '+str(i),[(b[0],b[1],14.65+z),(a[0],a[1],14.65+z),centre])
 # The veranda is an open-sided canopy, not a solid block. Its roof and
 # sparse supports are part of the silhouette at District distance.
 s.quad('veranda front roof',[(x0,y1,4.65+z),(x1,y1,4.65+z),(x1,y1+2.48,4.225+z),(x0,y1+2.48,4.225+z)])
 s.quad('veranda side roof',[(x1,y0,4.65+z),(x1+2.48,y0,4.225+z),(x1+2.48,y1,4.225+z),(x1,y1,4.65+z)])
 s.quad('veranda corner roof',[(x1,y1,4.65+z),(x1+2.32,y1,4.225+z),(x1+2.32,y1+2.32,4.225+z),(x1,y1+2.32,4.225+z)])
 wall('veranda front fascia',(x0,y1+2.48),(x1+2.48,y1+2.48),3.675,4.225)
 wall('veranda side fascia',(x1+2.48,y0),(x1+2.48,y1+2.48),3.675,4.225)
 posts=[(x,y1+2.4) for x in (-285.7,-281.1,-276.5,-271.9,-267.3)]+[(x1+2.4,y) for y in (-45.2,-40.5,-35.8,-31.1,-26.4)]+[(x1+2.4,y1+2.4)]
 for i,(x,y) in enumerate(posts):
  corners=[(x-.07,y-.07),(x+.07,y-.07),(x+.07,y+.07),(x-.07,y+.07)]
  for j,(a,b) in enumerate(zip(corners,corners[1:]+corners[:1])):wall('veranda post %s %s'%(i,j),a,b,0,3.675)
 # Chimney silhouettes are fixed coarse solids, independent of individual
 # pots and mouldings in Detail. Sink their bases into the roof envelope.
 for i,(x,y) in enumerate([(-282.4,-30.2),(-272.6,-35.0),(-271.5,-43.0)]):
  lo=14.6+z;hi=18.22+z
  corners=[(x-.4,y-.4),(x+.4,y-.4),(x+.4,y+.4),(x-.4,y+.4)]
  for j,(a,b) in enumerate(zip(corners,corners[1:]+corners[:1])):wall('chimney %s wall %s'%(i,j),a,b,lo-z,hi-z)
  s.quad('chimney %s cap'%i,[(a,b,hi) for a,b in corners])
 # Tower is separate and bounded; faces are chosen to avoid a duplicated
 # surface with main walls. Its full projection is subject to review.
 return s.result
