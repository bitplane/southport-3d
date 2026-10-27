"""Fixed, coarse replacement surfaces, independent of ornament."""
import json
from blender_envelope import Surfaces
from plan import world,roofs
def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());s=Surfaces(['frontage','rear','roof','projecting-sign'],lambda p:world(d,p));w=d['width'];m=d['main_depth'];dep=d['depth'];e=d['eave'];p=[(1,0),(w,0),(w,m),(0,m),(0,1)]
 for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
  s.part='frontage' if i in (0,4) else 'rear';low=4.1 if i==2 else -.2;s.quad('main '+str(i),[(*a,low),(*b,low),(*b,e),(*a,e)])
 # Projecting double-sided fish sign has its own fixed receiver planes.
 s.part='projecting-sign';s.quad('projecting sign front',[(1.134,-.50,2.84),(1.134,-1.20,2.84),(1.134,-1.20,3.46),(1.134,-.50,3.46)])
 s.quad('projecting sign back',[(1.226,-1.20,2.84),(1.226,-.50,2.84),(1.226,-.50,3.46),(1.226,-1.20,3.46)])
 q=[(0,m),(w,m),(w,dep),(0,dep)];s.part='rear'
 for i,(a,b) in enumerate(zip(q,q[1:]+q[:1])):
  if i==0:continue
  za=4.1 if a[1]==m else 3.8;zb=4.1 if b[1]==m else 3.8
  s.quad('extension '+str(i),[(*a,-.2),(*b,-.2),(*b,zb),(*a,za)])
 s.part='roof'
 for name,p in roofs(d):
  if len(p)==3:s.triangle(name,p)
  else:s.quad(name,p)
 return s.result
