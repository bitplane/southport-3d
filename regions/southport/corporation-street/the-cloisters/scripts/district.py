import json
from blender_envelope import Surfaces
from plan import world,roofs
def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w,l,e=d['width'],d['depth'],d['eave'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p))
 def wall(n,a,b,z0,z1):s.quad(n,[(*a,z0),(*b,z0),(*b,z1),(*a,z1)])
 s.part='frontage';wall('front',(0,0),(w,0),-.45,e)
 s.part='rear';wall('church',(0,l),(0,0),-.45,e);wall('Boots',(w,0),(w,14.8),-.45,e);wall('Boots low',(w,14.8),(w,l),-.45,9.9);wall('rear',(w,l),(0,l),-.45,9.9);wall('rear high',(3.8,l),(0,l),9.9,e)
 s.part='roof'
 for n,p in roofs(d):s.quad(n,p)
 wall('rear step',(w,14.8),(3.8,14.8),9.9,e)
 s.quad('corner side',[(3.8,14.8,9.9),(3.8,l,9.9),(3.8,l,e),(3.8,14.8,e)])
 s.triangle('corner triangle',[(3.8,14.8,e),(3.8,l,e),(3.8,16.55,12.8)])
 for u in [0,w]:
  for a,b,h in [(0,7.6,14.35),(7.6,14.8,13.9)]:
   p=[(u,a,e),(u,b,e),(u,(a+b)/2,h)]
   if u==0:p.reverse()
   s.triangle('roof end '+str((u,a)),p)
 s.triangle('corner end',[(0,l,e),(0,14.8,e),(0,16.55,12.8)])
 for i in [1,2]:
  u=(i+.5)*w/4;a,b=u-1.87,u+1.87
  wall('dormer '+str(i),(a,0),(b,0),e,13.1);s.triangle('dormer gable '+str(i),[(a,0,13.1),(b,0,13.1),(u,0,15)])
  s.quad('dormer slope1 '+str(i),[(a,0,13.1),(u,0,15),(u,.3,15),(a,.3,13.1)]);s.quad('dormer slope2 '+str(i),[(u,0,15),(b,0,13.1),(b,.3,13.1),(u,.3,15)])
 # Deliberately fixed five low-sided pinnacle silhouettes, independent of ornament.
 for i in range(5):
  u=i*w/4;h=d['pinnacle_cap_base'][i]
  s.box('pinnacle '+str(i),(u-.23,-.23,e-.05),(u+.23,.23,h+.60),cage=.5)
 return s.result
