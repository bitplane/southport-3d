"""Independent fixed-budget courtyard ring, porch and stair envelope."""
import json,math
from blender_envelope import Surfaces
from shapes import transform,roofs,elevations

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['front_width'];s=Surfaces(['front','rear','roof','porch','steps'],lambda p:transform(d,p))
 s.quad('front facade',[(0,0,-.15),(w,0,-.15),(w,0,d['eaves']),(0,0,d['eaves'])],cage=.55)
 s.triangle('pediment',[(10, -.16,12.92),(18.19,-.16,12.92),(14.095,-.16,15.45)],cage=.4)
 for a,b in [(0,10.0),(18.19,w)]:s.box('parapet',(a,-.16,12.7),(b,.32,13.9),omit=('bottom',),cage=.4)
 s.part='rear'
 for n,a,b,ha,hb in elevations(d):s.quad(n,[(a[0],a[1],-.15),(b[0],b[1],-.15),(b[0],b[1],hb),(a[0],a[1],ha)],cage=.6 if n=='north'else .4)
 s.part='roof'
 for n,p in roofs(d):s.quad(n,p,cage=.24)
 # Authored lantern receiver, independent of its mullion count.
 a=[(11.5,13.85,13.8),(16.5,13.85,13.8),(16.5,18.15,13.8),(11.5,18.15,13.8)];c=(14,16.0,15.1)
 for i in range(4):s.triangle('lantern '+str(i),[a[i],a[(i+1)%4],c],cage=.18)
 s.part='porch';p=d['porch'];x0,x1=p['x0'],p['x1'];cx=w/2
 s.part='steps'
 s.box('landing',(x0,-3.12,2.54),(x1,0,2.8),omit=(),cage=.2)
 s.part='porch'
 s.box('entablature',(x0-.28,-3.25,7.6),(x1+.28,.21,8.26),omit=(),cage=.25)
 for x in [x0+.4,x1-.4]:s.box('corner pier',(x-.27,-3.03,2.8),(x+.27,-2.43,7.5),omit=('bottom','top'),cage=.14)
 for x in [cx-1.65,cx+1.65]:
  for i in range(8):
   a,b=math.tau*i/8,math.tau*(i+1)/8
   s.quad('Doric shaft',[(x+.34*math.cos(a),-2.73+.34*math.sin(a),2.8),(x+.34*math.cos(b),-2.73+.34*math.sin(b),2.8),(x+.31*math.cos(b),-2.73+.31*math.sin(b),7.47),(x+.31*math.cos(a),-2.73+.31*math.sin(a),7.47)],cage=.17)
  s.box('abacus',(x-.46,-3.19,7.47),(x+.46,-2.27,7.60),omit=('bottom',),cage=.12)
 # Steps preserve the two physical flights. Fixed16 treads, independent of trim.
 s.part='steps'
 st=d['stair'];yf=-st['front'];yb=-st['back'];N=16
 s.box('central stair wall',(x0,yf,-.15),(x1,yb,2.8),omit=('bottom',),cage=.25)
 for a,b,r in [(st['x0'],x0,True),(x1,st['x1'],False)]:
  for i in range(N):
   xx=a+i*(b-a)/N;XX=a+(i+1)*(b-a)/N;z=-.02+(2.82)*(i+1 if r else N-i)/N
   s.quad('tread',[(xx,yf,z),(XX,yf,z),(XX,yb,z),(xx,yb,z)],cage=.12)
   edge=xx if r else XX;lo=z-2.82/N
   pts=[(edge,yf,lo),(edge,yb,lo),(edge,yb,z),(edge,yf,z)]
   s.quad('riser',pts if r else pts[::-1],cage=.12)
  # Outer stair cheek slopes receive the source's stepped wall appearance.
  za=-.02 if r else 2.8;zb=2.8 if r else -.02
  s.quad('flight cheek',[(a,yf,-.16),(b,yf,-.16),(b,yf,zb),(a,yf,za)],cage=.25)
 # Coarse low rail strips carry baluster appearance; open portico volume retained.
 s.part='porch'
 for yy,z in [(yf,3.8),(-3.29,8.95)]:s.box('balustrade rail',(x0,yy-.12,z),(x1,yy+.12,z+.2),omit=('bottom',),cage=.25)
 return s.result
