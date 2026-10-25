"""Fixed topology: authored roof planes, curved oriel and open iron verandah."""
import json,math
from blender_envelope import Surfaces
from ground_contact import post_base

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text())
 def T(p):x,y,z=p;return d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x,d['base_z']+z
 s=Surfaces(['facades','roof','frontage','verandah'],T)
 def q(name,p,**kw):s.quad(name,[(x,-out,z) for x,z,out in p],**kw)
 def panel(name,a,b,lo,hi,out=.015):q(name,[(a,lo,out),(b,lo,out),(b,hi,out),(a,hi,out)])
 # Facade ownership excludes projected oriel and shop aperture.
 for name,a,b,lo,hi in [('left base',0,.4,0,3.9),('right base',6.6,7,0,3.9),('shop head',0,7,3.9,4.48),('oriel left',0,.67,4.48,8.02),('oriel right',6.33,7,4.48,8.02),('upper front',0,7,8.02,16.3)]:panel(name,a,b,lo,hi)
 # Four cornice facets replace all small profile rings; front plane split avoided
 # by putting fronts in the exposed shape and retaining buried contacts only.
 for name,lo,hi,out in [('upper string',11.55,11.78,.14),('cornice',14.8,15.4,.25),('parapet cap',16.14,16.3,.12)]:
  panel(name,0,7,lo,hi,out);q(name+' top',[(0,hi,out),(7,hi,out),(7,hi,0),(0,hi,0)])
 for x in (0,7):
  p=[(x,0,0),(x,9.2,0),(x,9.2,13.3),(x,0,15.5)];s.quad('main side '+str(x),list(reversed(p)) if x==0 else p)
 back=[(0,9.2),(7,9.2),(7,18.8),(2.1,18.8),(2.1,15.5),(0,15.5)]
 def rz(x):return 13.3-x*2.7/7
 for i,(a,b) in enumerate(zip(back,back[1:]+back[:1])):
  if not i:continue
  s.quad('rear wing '+str(i),[(a[0],a[1],3.4),(b[0],b[1],3.4),(b[0],b[1],rz(b[0])),(a[0],a[1],rz(a[0]))])
 s.triangle('main rear',[(7,9.2,13.3),(7,9.2,10.6),(0,9.2,13.3)])
 for x in (0,7):
  p=[(x,9.2,0),(x,30.8,0),(x,30.8,3.4),(x,9.2,3.4)];s.quad('low side '+str(x),list(reversed(p)) if x==0 else p)
 s.quad('low back',[(0,30.8,0),(0,30.8,3.4),(7,30.8,3.4),(7,30.8,0)])
 s.part='roof'
 s.quad('front roof',[(0,0,15.5),(7,0,15.5),(7,9.2,13.3),(0,9.2,13.3)])
 for name,a,b,lo,hi in [('rear main',0,7,9.2,15.5),('rear offset',2.1,7,15.5,18.8)]:s.quad(name,[(a,lo,rz(a)),(b,lo,rz(b)),(b,hi,rz(b)),(a,hi,rz(a))])
 for name,a,b,lo,hi in [('low notch',0,2.1,15.5,18.8),('low back',0,7,18.8,30.8)]:s.quad(name,[(a,lo,3.4),(b,lo,3.4),(b,hi,3.4),(a,hi,3.4)])
 s.quad('parapet cap',[(0,0,16.3),(7,0,16.3),(7,.35,16.3),(0,.35,16.3)])
 s.quad('parapet back',[(0,.35,15.4),(0,.35,16.3),(7,.35,16.3),(7,.35,15.4)])
 s.part='frontage'
 # Eight fixed sides approximate rounded oriel corners independently of fine pane count.
 path=[(.67,.08),(.72,.34),(.87,.56),(1.09,.71),(1.35,.76),(5.65,.76),(5.91,.71),(6.13,.56),(6.28,.34),(6.33,.08)]
 for i,((a,o),(b,p)) in enumerate(zip(path,path[1:])):
  for j,(lo,hi,extra) in enumerate([(4.48,4.68,.05),(4.68,7.10,0),(7.10,7.44,.10),(7.44,8.02,.10)]):q(f'oriel {i} {j}',[(a,lo,o+extra),(b,lo,p+extra),(b,hi,p+extra),(a,hi,o+extra)])
 # Top and base horizontal bands close the projected volume against the wall.
 for i,((a,o),(b,p)) in enumerate(zip(path,path[1:])):
  q('oriel top '+str(i),[(a,7.44,o+.08),(b,7.44,p+.08),(b,7.44,0),(a,7.44,0)])
  q('oriel base '+str(i),[(a,4.48,0),(b,4.48,0),(b,4.48,p+.05),(a,4.48,o+.05)])
 for name,a,b,out in [('shop left',.4,2.5,-.15),('shop door',2.5,4.5,-.69),('shop right',4.5,6.6,-.15)]:panel(name,a,b,0,3.0,out)
 for x in (2.5,4.5):q('shop reveal '+str(x),[(x,0,-.15),(x,0,-.69),(x,3.0,-.69),(x,3.0,-.15)] if x==2.5 else [(x,0,-.69),(x,0,-.15),(x,3.0,-.15),(x,3.0,-.69)])
 panel('shop sign',.4,6.6,3.0,3.9,.08)
 s.part='verandah'
 for k,x in enumerate((.12,1.9,5.1,6.88)):
  for j,(lo,hi,r) in enumerate([(post_base(d,x),.32,.105),(.32,3.05,.065),(3.05,3.30,.12)]):
   for i in range(6):
    a=math.tau*i/6;b=math.tau*(i+1)/6
    q(f'column {k} {j} {i}',[(x+r*math.cos(a),lo,2.40-r*math.sin(a)),(x+r*math.cos(b),lo,2.40-r*math.sin(b)),(x+r*math.cos(b),hi,2.40-r*math.sin(b)),(x+r*math.cos(a),hi,2.40-r*math.sin(a))],cage=.16)
 s.box('fascia',(0,-2.48,3.26),(7,-2.32,3.77))
 s.quad('canopy top',[(0,0,4.32),(0,-2.5,3.65),(7,-2.5,3.65),(7,0,4.32)])
 s.quad('canopy underside',[(0,0,4.31),(7,0,4.31),(7,-2.5,3.64),(0,-2.5,3.64)])
 return s.result
