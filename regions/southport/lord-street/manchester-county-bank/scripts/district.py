"""Fixed budget building receiver independent of fine ornament."""
import json,math,os
from pathlib import Path
from blender_envelope import Surfaces
from shapes import transform,roofs,exterior,bays,rect,cuts,canopy_profile,tower_upstand,tower_oculus

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['front_width'];s=Surfaces(['front','rear','roof','canopy'],lambda p:transform(d,p))
 def face(name,p,**kw):
  from mathutils import Vector
  p=[Vector(v)for v in p]
  changed=True
  while changed and len(p)>3:
   changed=False
   for i in range(len(p)):
    if (p[i]-p[i-1]).length<1e-6 or (p[i]-p[i-1]).cross(p[(i+1)%len(p)]-p[i]).length<1e-7:
     p.pop(i);changed=True;break
  if len(p)==4:
   s.quad(name,p,**kw);return
  from mathutils.geometry import tessellate_polygon
  for i,tri in enumerate(tessellate_polygon([p])):
   vs=[p[v]if isinstance(v,int)else v for v in tri]
   if (vs[1]-vs[0]).cross(vs[2]-vs[0]).length>1e-8:s.triangle(name+' '+str(i),vs,**kw)
 s.part='front';hs=[rect(x-ww/2,z,x+ww/2,h)for x,ww,z,h,proj in bays(d)]
 if d['kind']=='bank':hs += [rect(cx-1.65,7.55,cx+1.65,8.65)for cx in d['bay_centres'][1:]]
 for i,p in enumerate(cuts(rect(0,0,w,d['front_eaves']),hs)):face('facade '+str(i),[(x,0,z)for x,z in p],cage=.65)
 for bi,(cx,ww,z0,z1,proj)in enumerate(bays(d)):
  chain=[(cx-ww/2,0),(cx-ww/2+.48,-proj),(cx+ww/2-.48,-proj),(cx+ww/2,0)]
  for i,(a,b)in enumerate(zip(chain,chain[1:])):face('bay '+str(bi)+' '+str(i),[(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],cage=.35)
  face('bay top '+str(bi),[(x,y,z1)for x,y in chain],cage=.35)
  face('bay bottom '+str(bi),[(x,y,z0)for x,y in chain[::-1]],cage=.35)
 if d['kind']=='red':
  cx=w/2;p=[(cx-2.75,12),(cx+2.75,12),(cx+2.75,12.55),(cx+2.15,12.85),(cx,14.8),(cx-2.15,12.85),(cx-2.75,12.55)]
  face('central gable',[(x,0,z)for x,z in p],cage=.35);face('gable back',[(x,.22,z)for x,z in p[::-1]],cage=.35)
 else:
  t=d['tower'];oc=tower_oculus(d);up=tower_upstand(d);dep=t['pediment_depth']
  for i,p in enumerate(cuts(rect(0,8.65,t['width'],t['eaves']),[rect(.65,8.65,3.25,10),oc])):
   face('tower '+str(i),[(x,0,z)for x,z in p],cage=.65)
  face('tower oculus glass',[(x,.205,z)for x,z in oc],cage=.08)
  face('tower pediment front',[(x,-dep,z)for x,z in up],cage=.35)
  face('tower pediment back',[(x,0,z)for x,z in up[::-1]],cage=.35)
  for i,(a,b)in enumerate(zip(up,up[1:]+up[:1])):
   face('tower pediment edge '+str(i),[(a[0],-dep,a[1]),(b[0],-dep,b[1]),(b[0],0,b[1]),(a[0],0,a[1])],cage=.20)
  for i,cx in enumerate(d['bay_centres'][1:]):
   a,c=cx-1.65,cx+1.65;p=[(a,7.55),(a,9.35),(cx,10.95),(c,9.35),(c,7.55)]
   face('gable '+str(i),[(x,-.68,z)for x,z in p[::-1]],cage=.45)
 s.part='rear'
 party=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/lord-street/lord-street-409-421/research/layout.json').read_text())if d['kind']=='bank'else None
 for name,p in exterior(d,party):face(name,p,cage=.40)
 s.part='roof'
 for name,p in roofs(d):face(name,p,cage=.28)
 if d['kind']=='bank':
  # The District envelope replaces source meshes, including kept Detail/Walk
  # crest objects, so preserve their silhouette with a few fixed receivers.
  t=d['tower'];x=t['width']/2;z=t['top']+t['crown_rise'];a=t['top_inset']+t['crown_inset']+.10;b=t['depth']-a
  for i,y in enumerate((a,b)):
   s.box('tower crest finial '+str(i),(x-.028,y-.028,z),(x+.028,y+.028,z+.50),cage=.10,weight=.25)
   s.box('tower crest terminal '+str(i),(x-.06,y-.06,z+.50),(x+.06,y+.06,z+.64),cage=.10,weight=.25)
  s.box('tower crest rail',(x-.023,a,z+.247),(x+.023,b,z+.293),cage=.10,weight=.25)
 for i,ch in enumerate(d['chimneys']):
  x,y,b,t,ww,dep=[ch[k]for k in ['x','y','base','top','w','d']]
  s.box('chimney '+str(i),(x-ww/2,y-dep/2,b),(x+ww/2,y+dep/2,t+.16),cage=.22)
  for j,dx in enumerate([-.22,.22]):s.box('pot '+str(i)+' '+str(j),(x+dx-.11,y-.11,t+.16),(x+dx+.11,y+.11,t+.64),cage=.12,weight=.4)
 s.part='canopy';p=canopy_profile(d,5)
 for i,((a,z),(b,Z))in enumerate(zip(p,p[1:])):
  s.quad('canopy top '+str(i),list(reversed([(0,-a,z),(w,-a,z),(w,-b,Z),(0,-b,Z)])),cage=.16)
  s.quad('canopy underside '+str(i),list(reversed([(0,-b,Z-.035),(w,-b,Z-.035),(w,-a,z-.035),(0,-a,z-.035)])),cage=.16,weight=.5)
 from southport3d.elevation import Elevations
 support=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/lord-corridor.json').surface(d['ground_surface'])
 for i,x in enumerate(d['canopy_posts']):
  X,Y,_=transform(d,(x,-3.18,0));base=support.height(X,Y)-d['floor_z']
  for j in range(6):
   a,b=math.tau*j/6,math.tau*(j+1)/6;r=.07
   s.quad('post '+str(i)+' '+str(j),[(x+r*math.cos(a),-3.18+r*math.sin(a),base),(x+r*math.cos(b),-3.18+r*math.sin(b),base),(x+r*math.cos(b),-3.18+r*math.sin(b),3.56),(x+r*math.cos(a),-3.18+r*math.sin(a),3.56)],cage=.16,weight=.5)
 return s.result
