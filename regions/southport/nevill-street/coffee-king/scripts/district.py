"""Bounded envelope: four octagonal columns, recessed door and measured roof."""
import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());W=d['width']
 def T(p):x,y,z=p;return d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x,d['base_z']+z
 s=Surfaces(['facades','roof','frontage'],T);s.part='facades';u=d['bays'][0]
 def q(name,p,**kw):s.quad(name,[(x,-out,z) for x,z,out in p],**kw)
 # Real recess has continuous reveals on every edge, including threshold.
 for name,a,b,lo,hi in [('front left',0,u-.70,0,14.98),('front right',u+.70,W,0,14.98),('door head',u-.70,u+.70,2.76,14.98)]:q(name,[(a,lo,.022),(b,lo,.022),(b,hi,.022),(a,hi,.022)])
 q('door left',[(u-.70,0,.022),(u-.70,0,-.03),(u-.70,2.76,-.03),(u-.70,2.76,.022)])
 q('door right',[(u+.70,0,-.03),(u+.70,0,.022),(u+.70,2.76,.022),(u+.70,2.76,-.03)])
 q('threshold',[(u-.70,0,.022),(u+.70,0,.022),(u+.70,0,-.03),(u-.70,0,-.03)])
 q('door soffit',[(u-.70,2.76,-.03),(u+.70,2.76,-.03),(u+.70,2.76,.022),(u-.70,2.76,.022)])
 q('passage upper front',[(-.61,3.3,0),(0,3.3,0),(0,14.98,0),(-.61,14.98,0)])
 q('passage lower pier',[(-.22,0,0),(0,0,0),(0,3.3,0),(-.22,3.3,0)])
 q('passage upper end',[(-.61,3.3,-.4),(-.61,3.3,0),(-.61,14.98,0),(-.61,14.98,-.4)])
 q('passage pier end',[(-.22,0,-.4),(-.22,0,0),(-.22,3.3,0),(-.22,3.3,-.4)])
 q('passage soffit',[(-.61,3.3,-.4),(0,3.3,-.4),(0,3.3,0),(-.61,3.3,0)])
 q('passage cap',[(-.61,14.98,0),(0,14.98,0),(0,14.98,-.4),(-.61,14.98,-.4)])
 for k,x in enumerate(d['columns']):
  s.box('pedestal '+str(k),(x-.37,-.435,0),(x+.37,.115,1.86))
  for j,((z,r),(Z,R)) in enumerate(zip([(1.86,.36),(2.15,.285),(4.65,.224),(5.,.36)],[(2.15,.285),(4.65,.224),(5.,.36)])):
   for i in range(8):
    a=math.tau*i/8;b=math.tau*(i+1)/8
    q(f'column {k} {j} {i}',[(x+r*math.cos(a),z,.20-r*math.sin(a)),(x+r*math.cos(b),z,.20-r*math.sin(b)),(x+R*math.cos(b),Z,.20-R*math.sin(b)),(x+R*math.cos(a),Z,.20-R*math.sin(a))],cage=.15)
 for name,lo,hi,out in [('frieze',5.,6.05,.21),('lower cornice',6.05,6.56,.32),('sign fascia',6.56,7.03,.16),('upper cornice',13.8,14.24,.27)]:
  q(name,[(0,lo,out),(W,lo,out),(W,hi,out),(0,hi,out)])
  q(name+' top',[(0,hi,out),(W,hi,out),(W,hi,0),(0,hi,0)])
 # Side profiles split into convex quads and the roof gable triangle.
 for side in (0,W):
  def sideq(name,p):s.quad(name,list(reversed(p)) if side==0 else p)
  sideq('main side '+str(side),[(side,0,0),(side,13.5,0),(side,13.5,10.7),(side,0,10.7)])
  sideq('upper front side '+str(side),[(side,0,10.7),(side,6.05,10.7),(side,6.05,16),(side,0,14.45)])
  p=[(side,6.05,10.7),(side,13.5,10.7),(side,6.05,16)];s.triangle('upper back side '+str(side),list(reversed(p)) if side==0 else p)
 for name,a,b,lo,hi,z in [('middle',0,W,13.5,19.15,7.22),('rear',3.7,W,19.15,25.15,3.)]:
  s.quad(name+' left',[(a,lo,0),(a,lo,z),(a,hi,z),(a,hi,0)])
  s.quad(name+' right',[(b,lo,0),(b,hi,0),(b,hi,z),(b,lo,z)])
  s.quad(name+' back',[(a,hi,0),(a,hi,z),(b,hi,z),(b,hi,0)])
 s.quad('main rear',[(0,13.5,7.22),(0,13.5,10.7),(W,13.5,10.7),(W,13.5,7.22)])
 s.part='frontage';q('door',[(u-.70,0,-.03),(u+.70,0,-.03),(u+.70,2.76,-.03),(u-.70,2.76,-.03)])
 s.part='roof'
 s.quad('front pitch',[(0,0,14.45),(W,0,14.45),(W,6.05,16),(0,6.05,16)])
 s.quad('rear pitch',[(0,6.05,16),(W,6.05,16),(W,13.5,10.7),(0,13.5,10.7)])
 for name,a,b,lo,hi,z in [('middle',0,W,13.5,19.15,7.22),('rear',3.7,W,19.15,25.15,3.)]:s.quad(name+' roof',[(a,lo,z),(b,lo,z),(b,hi,z),(a,hi,z)])
 s.quad('parapet cap',[(0,0,14.98),(W,0,14.98),(W,.32,14.98),(0,.32,14.98)])
 s.quad('parapet back',[(0,.32,14.28),(0,.32,14.98),(W,.32,14.98),(W,.32,14.28)])
 for x in (0,W):s.quad('parapet end '+str(x),[(x,0,14.45),(x,.32,14.45+.32*1.55/6.05),(x,.32,14.98),(x,0,14.98)] if x==W else [(x,0,14.45),(x,0,14.98),(x,.32,14.98),(x,.32,14.45+.32*1.55/6.05)])
 return s.result
