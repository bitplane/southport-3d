import json,math
from blender_envelope import Surfaces
from plan import world,roof,outline
def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w,l,e=d['width'],d['depth'],d['eave'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p));p=outline(d)
 # Reflection reverses local polygon winding; reverse all receiver faces.
 def quad(n,q,**kw):s.quad(n,list(reversed(q)),**kw)
 for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
  if i==2:continue
  s.part='frontage' if i in (0,4) else 'rear';quad('wall '+str(i),[(*a,-.18),(*b,-.18),(*b,e),(*a,e)])
 s.part='rear';quad('rear above service',[(w,l,d['rear_height']),(0,l,d['rear_height']),(0,l,e),(w,l,e)])
 s.triangle('rear gable',list(reversed([(w,l,e),(0,l,e),(w/2,l,d['ridge'])])))
 s.part='roof'
 for n,q in roof(d):
  if len(q)==3:s.triangle(n,list(reversed(q)))
  else:quad(n,q)
 for k,(va,vb,ww,h) in enumerate([(l,27.,11.6,9.4),(27.,32.8,11.6,6.1),(32.8,35.9,5.55,4.)]):
  s.part='rear'
  for j,(a,b) in enumerate([((0,vb),(0,va)),((ww,va),(ww,vb)),((ww,vb),(0,vb))]):quad('service '+str(k)+' '+str(j),[(*a,-.18),(*b,-.18),(*b,h),(*a,h)])
  s.part='roof';quad('service roof '+str(k),[(0,va,h),(ww,va,h),(ww,vb,h),(0,vb,h)])
 # Main red awnings remain silhouette geometry; fixed count, independent of lettering.
 s.part='frontage';a,b=d['chamfer_u'],d['chamfer_v'];cw=math.hypot(a,b)
 for name,start,end,mapface in [('front',a,w,lambda x,z,o:(x,-o,z)),('corner',0,cw,lambda x,z,o:(a*x/cw-b*o/cw,b-b*x/cw-a*o/cw,z)),('Stanley',-6.5,-b,lambda x,z,o:(-o,-x,z))]:
  quad(name+' awning',[mapface(start,2.99,.27),mapface(end,2.99,.27),mapface(end,2.55,1.),mapface(start,2.55,1.)])
  quad(name+' valance',[mapface(start,2.55,1.),mapface(end,2.55,1.),mapface(end,2.38,1.),mapface(start,2.38,1.)])
 return s.result
