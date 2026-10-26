"""Fixed authored receiver envelope; ornament cannot grow topology or atlases."""
import json,math,os,sys
from pathlib import Path
from blender_envelope import Surfaces
from shapes import transform,roofs,exterior,canopy_profile,main_roof_z

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['front_width'];s=Surfaces(['front','rear','roof','canopy'],lambda p:transform(d,p))
 def face(name,p,**kw):
  from mathutils import Vector
  p=[Vector(v) for v in p]
  changed=True
  while changed and len(p)>3:
   changed=False
   for i in range(len(p)):
    if (p[i]-p[i-1]).length<1e-6 or (p[i]-p[i-1]).cross(p[(i+1)%len(p)]-p[i]).length<1e-7:
     p.pop(i);changed=True;break
  if len(p)==4:s.quad(name,p,**kw)
  else:
   for i in range(1,len(p)-1):
    if (p[i]-p[0]).cross(p[i+1]-p[0]).length>1e-7:s.triangle(name+' '+str(i),[p[0],p[i],p[i+1]],**kw)
 s.part='front'
 s.quad('front lower',[(0,-.01,-.18),(w,-.01,-.18),(w,-.01,4.44),(0,-.01,4.44)],cage=.75)
 s.quad('front upper',[(0,-.01,4.44),(w,-.01,4.44),(w,-.01,12.85),(0,-.01,12.85)],cage=.55)
 for a,b in zip(d['bay_edges'],d['bay_edges'][1:]):
  h=13.65 if abs(a-13.9)<.01 else 13.35
  s.quad('parapet',[(a,0,12.85),(b,0,12.85),(b,0,h),(a,0,h)],cage=.30)
  s.quad('parapet back',[(b,.16,12.85),(a,.16,12.85),(a,.16,h),(b,.16,h)],cage=.30)
  s.quad('parapet cap',[(a,-.16,h),(b,-.16,h),(b,.16,h),(a,.16,h)],cage=.20)
 # One projecting bay is a geometric silhouette; its rear remains behind the body skin.
 s.box('cafe projecting bay',(20.77,-.48,4.61),(24.53,-.06,7.77),omit=('bottom','front'),cage=.45)
 for i,x in enumerate(d['bay_edges']):
  width=.26 if i in (0,4) else .30;xx=max(width/2,min(w-width/2,x));h=13.92 if i in (2,3) else 13.63
  s.box('parapet pier '+str(i),(max(0,xx-.19),-.18,12.86),(min(w,xx+.19),.18,h+.15),cage=.25)
  s.box('finial '+str(i),(xx-.1,-.10,h+.15),(xx+.1,.1,h+.55),cage=.25,weight=.4)
 s.part='rear'
 for name,p in exterior(d):face(name,p,cage=.40)
 s.part='roof'
 for name,p in roofs(d):face(name,p,cage=.28)
 for i,ch in enumerate(d['chimneys']):
  x,y,width,depth,top=ch['x'],ch['y'],ch['w'],ch['d'],ch['top'];base=main_roof_z(d,y)-.5 if y<d['main_depth'] else d['rear_eaves']-.2
  s.box('stack '+str(i),(x-width/2,y-depth/2,base),(x+width/2,y+depth/2,top+.14),cage=.25)
  for j in range(ch['pots']):
   xx=x+(-.25 if j%2==0 else .25);yy=y+(-.35 if j//2==0 else .35)
   s.box('pot '+str(i)+' '+str(j),(xx-.12,yy-.12,top+.14),(xx+.12,yy+.12,top+.57),cage=.12,weight=.4)
 s.part='canopy';p=canopy_profile(d,5)
 for j,((a,z),(b,Z)) in enumerate(zip(p,p[1:])):
  s.quad('curved canopy top '+str(j),[(0,-b,Z),(w,-b,Z),(w,-a,z),(0,-a,z)],cage=.14)
  s.quad('curved canopy underside '+str(j),[(0,-a,z-.035),(w,-a,z-.035),(w,-b,Z-.035),(0,-b,Z-.035)],cage=.14,weight=.6)
 s.box('street beam',(0,-3.23,3.46),(w,-3.13,3.62),cage=.16)
 from southport3d.elevation import Elevations
 plan=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/lord-burlington.json').surface('burlington-canopy-support')
 for i,x in enumerate(d['canopy']['post_x']):
  X,Y,_=transform(d,(x,-3.18,0));base=plan.height(X,Y)-d['floor_z']
  for j in range(6):
   a=math.tau*j/6;b=math.tau*(j+1)/6;r=.075
   s.quad('post '+str(i)+' '+str(j),[(x+r*math.cos(a),-3.18+r*math.sin(a),base),(x+r*math.cos(b),-3.18+r*math.sin(b),base),(x+r*math.cos(b),-3.18+r*math.sin(b),3.55),(x+r*math.cos(a),-3.18+r*math.sin(a),3.55)],cage=.18,weight=.6)
 return s.result
