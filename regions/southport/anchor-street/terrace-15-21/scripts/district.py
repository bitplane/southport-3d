"""Fixed terrace envelope: four shop bays, coarse openings and stepped wings."""
import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());a=math.radians(d['rotation_degrees']);c=math.cos(a);sn=math.sin(a)
 def T(p):x,y,z=p;return d['origin_site_xy'][0]+c*x-sn*y,d['origin_site_xy'][1]+sn*x+c*y,d['base_z']+z
 s=Surfaces(['walls','roof','joinery'],T);W=d['width'];dep=d['main_depth'];H=d['parapet']
 def front(name,a,b,z,Z,y=0):s.quad(name,[(a,y,z),(b,y,z),(b,y,Z),(a,y,Z)])
 # Deliberately simple upper facade. Glazing and lintels project onto one atlas.
 front('upper frontage',0,W,3.60,H+.07)
 for j in range(4):
  lo=j*5.2;hi=lo+5.2;bay=lo+(1.95 if j<2 else 3.05);door=lo+(4.65 if j<2 else .55)
  # Tile the remaining wall around each projected bay, without duplicate faces.
  intervals=sorted([(lo,lo),(bay-1.64,bay+1.64),(door-.43,door+.43),(hi,hi)])
  for k in range(len(intervals)-1):
   l=intervals[k][1];r=intervals[k+1][0]
   if r>l+.001:front(f'ground pier {j} {k}',l,r,0,3.60)
  front('door head '+str(j),door-.43,door+.43,3.05,3.60)
  s.part='joinery';front('door '+str(j),door-.43,door+.43,0,3.05,.15);s.part='walls'
  for side in (-1,1):
   x=door+side*.43;p=[(x,0,0),(x,.15,0),(x,.15,3.05),(x,0,3.05)];s.quad('door reveal '+str(j)+str(side),p if side==-1 else list(reversed(p)))
  front('bay '+str(j),bay-1.64,bay+1.64,0,3.22,-.44)
  for side in (-1,1):
   x=bay+side*1.64;p=[(x,0,0),(x,-.44,0),(x,-.44,3.22),(x,0,3.22)];s.quad('bay cheek '+str(j)+str(side),p if side==1 else list(reversed(p)))
  front('bay upper backing '+str(j),bay-1.64,bay+1.64,3.22,3.60)
  s.part='roof';s.quad('canopy '+str(j),[(bay-1.77,-.69,3.22),(bay+1.77,-.69,3.22),(bay+1.77,0,3.55),(bay-1.77,0,3.55)]);s.part='walls'
 s.quad('east main',[(W,0,0),(W,dep,0),(W,dep,d['eaves']),(W,0,d['eaves'])])
 s.quad('west main',[(0,dep,0),(0,0,0),(0,0,d['eaves']),(0,dep,d['eaves'])])
 # Rear courtyard front has no false solid fill across the real wing gaps.
 intervals=[(0,1.7,0),(1.7,8.2,8.9),(8.2,12.4,0),(12.4,18.8,9.0),(18.8,20.6,3.05),(20.6,W,0)]
 for i,(x,X,z) in enumerate(intervals):
  s.quad('main rear '+str(i),[(X,dep,z),(x,dep,z),(x,dep,d['eaves']),(X,dep,d['eaves'])])
 for v in d['rear_volumes']:
  name=v['name'];x,X=v['u'];y,Y=v['v'];h=v['eaves']
  s.quad(name+' east',[(X,y,0),(X,Y,0),(X,Y,h),(X,y,h)])
  s.quad(name+' west',[(x,Y,0),(x,y,0),(x,y,h),(x,Y,h)])
  z=6.5 if name=='east paired upper wing' else 0
  s.quad(name+' end',[(X,Y,z),(x,Y,z),(x,Y,h),(X,Y,h)])
 s.quad('parapet top',[(0,0,H+.07),(W,0,H+.07),(W,.24,H+.07),(0,.24,H+.07)])
 s.quad('parapet back',[(W,.24,d['eaves']),(0,.24,d['eaves']),(0,.24,H+.07),(W,.24,H+.07)])
 s.part='roof';s.hip('main',0,W,0,dep,d['eaves'],d['ridge'])
 for v in d['rear_volumes']:s.hip(v['name'],*v['u'],*v['v'],v['eaves'],v['ridge'],axis='y')
 for u in (.38,5.2,10.4,20.42):s.box('chimney '+str(u),(u-.275,3.525,9.0),(u+.275,4.675,12.51))
 for u,v,z in [(4.95,11.3,10.9),(15.60,10.7,10.9)]:s.box('rear chimney '+str(u),(u-.315,v-.515,z-.55),(u+.315,v+.515,z+.66))
 return s.result
