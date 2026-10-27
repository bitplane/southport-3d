"""Fixed-budget envelope, independently authored from the bank dimensions."""
import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());x=d['front_x'];y=d['side_y'];a=d['registration_angle_rad'];z=d['base_z'];w=d['width_m'];depth=d['main_depth_m'];h=d['upper_height_m'];r=.70;sd=d['service_depth_m'];sw=d['service_width_m'];sh=d['service_height_m']
 def world(p):
  X,Y,Z=p;return x+math.cos(a)*(X-x)-math.sin(a)*(Y-y),y+math.sin(a)*(X-x)+math.cos(a)*(Y-y),Z+z
 s=Surfaces(['architecture'],world)
 def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
 # Upper front and the true ground-storey opening, with a recessed receiver.
 wall('front upper',(x,y-r),(x,y-w),3.20,h)
 wall('front corner pier',(x,y-r),(x,y-2.5),0,3.20)
 wall('front end pier',(x,y-9.55),(x,y-w),0,3.20)
 wall('recessed banking front',(x+.20,y-2.5),(x+.20,y-9.55),.12,3.20)
 wall('threshold face',(x,y-2.5),(x,y-9.55),0,.12)
 for u in (2.5,9.55):s.quad('shop jamb '+str(u),[(x,y-u,.12),(x+.2,y-u,.12),(x+.2,y-u,3.2),(x,y-u,3.2)])
 # Rounded exterior turns join the two main elevations without an overlapping box.
 curve=[(x+r+r*math.cos(math.pi-i*math.pi/16),y-r+r*math.sin(math.pi-i*math.pi/16)) for i in range(9)]
 for i,(A,B) in enumerate(zip(curve,curve[1:])):wall('corner '+str(i),B,A,0,h)
 wall('anchor side',(x+depth,y),(x+r,y),0,h)
 wall('party side',(x,y-w),(x+depth,y-w),0,h)
 wall('main rear',(x+depth,y-w),(x+depth,y),0,h)
 roof=curve+[(x+depth-.15,y-.15),(x+depth-.15,y-w+.15),(x+.15,y-w+.15)]
 centre=(x+depth/2,y-w/2,h-.20)
 for i,(A,B) in enumerate(zip(roof,roof[1:]+roof[:1])):s.triangle('main roof '+str(i),[centre,(*B,h-.20),(*A,h-.20)])
 # Gated service range and raised rear light bay remain explicitly separate.
 wall('service side',(x+depth+sd,y),(x+depth,y),0,sh)
 wall('service party',(x+depth,y-sw),(x+depth+sd,y-sw),0,sh)
 wall('service rear',(x+depth+sd,y-sw),(x+depth+sd,y),0,sh)
 s.quad('service roof',[(x+depth+3.05,y-.15,sh+.04),(x+depth+sd-.15,y-.15,sh+.04),(x+depth+sd-.15,y-sw+.15,sh+.04),(x+depth+3.05,y-sw+.15,sh+.04)][::-1])
 towerh=11.7;td=3.0
 wall('raised bay side',(x+depth+td,y),(x+depth,y),sh,towerh)
 wall('raised bay party',(x+depth,y-sw),(x+depth+td,y-sw),sh,towerh)
 wall('raised bay end',(x+depth+td,y-sw),(x+depth+td,y),sh,towerh)
 wall('raised bay exposed return',(x+depth,y),(x+depth,y-sw),h,towerh)
 s.quad('raised bay roof',[(x+depth+.15,y-.15,towerh+.04),(x+depth+td-.15,y-.15,towerh+.04),(x+depth+td-.15,y-sw+.15,towerh+.04),(x+depth+.15,y-sw+.15,towerh+.04)][::-1])
 return s.result
