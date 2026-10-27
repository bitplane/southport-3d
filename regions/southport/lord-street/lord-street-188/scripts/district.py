"""Independent fixed-topology District receivers; no dependence on ornament counts."""
from blender_envelope import Surfaces

def surfaces(asset):
 s=Surfaces(['front-tower','middle-tower','rear-block'])
 def tower(part,x0,x1,y0,y1,dx=0,dy=0):
  s.part=part;s.transform=lambda p:(p[0],p[1],p[2]+.18)
  # Main walls and terrace surrounding a recessed top floor.
  s.box('main',(x0,y0,0),(x1,y1,18),omit=('bottom','top'),cage=1.8)
  a,b=444.2+dx,468.95+dx;c,d=-25.8+dy,-11.3+dy
  for i,(u,v,U,V) in enumerate(((x0,y0,x1,c),(x0,d,x1,y1),(x0,c,a,d),(b,c,x1,d))):
   s.quad('terrace '+str(i),[(u,v,18),(U,v,18),(U,V,18),(u,V,18)],cage=.5)
  s.box('penthouse',(a,c,18),(b,d,20.3),omit=('bottom','top'),cage=.5)
  s.box('roof',(a-.8,c-.8,20.3),(b+.8,d+.8,20.55),omit=('bottom',),cage=.5)
  s.box('headhouse',(452.2+dx,-21+dy,20.55),(460.2+dx,-16.2+dy,21.2),omit=('bottom',),cage=.5)
  # Retained projecting balcony bands are independent of frame counts.
  for level in range(1,6):
   z=.4+2.9*level+.25
   for lo,hi in ((x0+.3,x0+4.5),(x0+9.4,x0+19),(x0+23.4,x1-.2)):
    for yy,sgn in ((y0,-1),(y1,1)):
     out=yy+sgn*1.0
     s.quad('balcony front',[(lo,out,z-.1),(hi,out,z-.1),(hi,out,z+.1),(lo,out,z+.1)],cage=.8)
     s.quad('balcony top',[(lo,yy,z+.1),(hi,yy,z+.1),(hi,out,z+.1),(lo,out,z+.1)],cage=.8)
  # A ground-floor outer balcony appears at the road front.
  z=.65;lo=x0+.3;hi=x0+4.5;out=y1+1
  s.quad('ground balcony',[(lo,out,z-.1),(hi,out,z-.1),(hi,out,z+.1),(lo,out,z+.1)],cage=.8)
 tower('front-tower',442.7,470.45,-27.3,-9.8)
 tower('middle-tower',442,469.49,-56.31,-40.2,-.7,-30.4)
 s.part='rear-block';s.transform=lambda p:(p[0],p[1],p[2]+.5);s.box('rear block',(450.3,-105.3,0),(462.5,-74.1,8.3),omit=('bottom','top'),cage=1.6)
 x0,x1=449.95,462.85;y0,y1=-105.65,-73.75;xm=(x0+x1)/2;z=8.3;h=10
 v=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),(xm,y0+5,h),(xm,y1-5,h)]
 for i,ids in enumerate(((0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5))):
  p=[v[k] for k in ids];(s.triangle if len(p)==3 else s.quad)('hip '+str(i),p,cage=.5)
 return s.result
