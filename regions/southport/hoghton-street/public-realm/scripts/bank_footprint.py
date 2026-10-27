"""Cut the researched bank out of the provisional Hoghton ground."""
import json,math

def bank_cutouts(repo):
 d=json.loads((repo/'regions/southport/london-street/lloyds-bank/research/layout.json').read_text())
 x,y=d['front_x'],d['side_y'];a=d['registration_angle_rad'];c,s=math.cos(a),math.sin(a)
 def point(X,Y):return [x+c*(X-x)-s*(Y-y),y+s*(X-x)+c*(Y-y)]
 def rectangle(x0,x1,y0,y1):return [point(x0,y0),point(x1,y0),point(x1,y1),point(x0,y1)]
 return [rectangle(x,x+d['main_depth_m'],y-d['width_m'],y),
         rectangle(x+d['main_depth_m'],x+d['main_depth_m']+d['service_depth_m'],y-d['service_width_m'],y)]
