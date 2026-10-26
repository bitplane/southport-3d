"""Fixed geometry independent of brick joints, carving, pane count and lettering."""
import json
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['width']
 def T(p):x,y,z=p;return d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x,d['base_z']+z
 s=Surfaces(['shell','frontage','gallery','verandah'],T)
 def panel(n,a,b,lo,hi,out=0,**kw):s.quad(n,[(a,-out,lo),(b,-out,lo),(b,-out,hi),(a,-out,hi)],**kw)
 for x,rev in ((0,True),(w,False)):
  p=[(x,0,-.45),(x,8.9,-.45),(x,8.9,13.3),(x,0,13.3)];s.quad('main side '+str(x),p[::-1] if rev else p)
 for a,b,za,zb in ((-.09,w/2,13.3,17.25),(w/2,w+.09,17.25,13.3)):
  s.quad('main roof '+str(a),[(a,-.76,za),(b,-.76,zb),(b,8.9,zb),(a,8.9,za)])
 s.quad('main rear',[(0,8.9,7.1),(0,8.9,13.3),(w,8.9,13.3),(w,8.9,7.1)])
 s.triangle('rear gable',[(0,8.9,13.3),(w/2,8.9,17.25),(w,8.9,13.3)])
 for x,rev in ((0,True),(w,False)):
  p=[(x,8.9,-.45),(x,33,-.45),(x,33,3.45),(x,8.9,3.45)];s.quad('low side '+str(x),p[::-1] if rev else p)
  p=[(x,8.9,3.45),(x,18.9,3.45),(x,18.9,6.5),(x,8.9,7.1)];s.quad('mid side '+str(x),p[::-1] if rev else p)
 s.quad('rear roof',[(0,8.9,7.1),(w,8.9,7.1),(w,18.9,6.5),(0,18.9,6.5)])
 s.quad('rear wall',[(0,18.9,3.45),(0,18.9,6.5),(w,18.9,6.5),(w,18.9,3.45)])
 s.quad('low roof',[(0,18.9,3.45),(w,18.9,3.45),(w,33,3.45),(0,33,3.45)])
 s.quad('low end',[(0,33,-.45),(0,33,3.45),(w,33,3.45),(w,33,-.45)])
 s.box('chimney',(w-.62,4.275,13.0),(w-.06,5.125,17.0))
 for n,a,b,lo,hi in [('left pier',0,.30,-.45,3.9),('right pier',w-.30,w,-.45,3.9),('lower head',0,w,3.9,4.38),('first left',0,.62,4.38,7.73),('first right',w-.62,w,4.38,7.73),('upper facade',0,w,7.73,11.6)]:panel(n,a,b,lo,hi,.03)
 s.part='frontage'
 path=[(.62,.04),(1.25,.58),(4.60,.58),(w-.62,.04)]
 for i,((a,o),(b,p)) in enumerate(zip(path,path[1:])):
  s.quad('bay '+str(i),[(a,-o,4.6),(b,-p,4.6),(b,-p,7.48),(a,-o,7.48)])
  s.quad('bay top '+str(i),[(a,-o,7.48),(b,-p,7.48),(b,0,7.48),(a,0,7.48)])
  s.quad('bay bottom '+str(i),[(a,0,4.6),(b,0,4.6),(b,-p,4.6),(a,-o,4.6)])
 shop=[(.30,-.10),(1.66,-.10),(2.40,-.70),(3.45,-.70),(4.19,-.10),(w-.30,-.10)]
 for i,((a,o),(b,p)) in enumerate(zip(shop,shop[1:])):s.quad('shop '+str(i),[(a,-o,0),(b,-p,0),(b,-p,2.99),(a,-o,2.99)])
 panel('sign',.3,w-.3,2.99,3.91,.10)
 s.part='gallery'
 panel('gallery back',0,w,11.6,13.3,-1.0)
 s.box('balcony slab',(-.06,-.65,11.55),(w+.06,1.15,11.73))
 s.triangle('white timber gable',[(0,-.71,13.3),(w,-.71,13.3),(w/2,-.71,17.25)],weight=2)
 s.box('gallery top rail',(0,-.82,13.19),(w,-.57,13.41))
 s.box('gallery handrail',(0,-.82,12.53),(w,-.57,12.69))
 s.box('gallery foot rail',(0,-.82,11.77),(w,-.57,11.92))
 for x in (.13,w/2,w-.13):s.box('gallery post '+str(x),(x-.09,-.82,11.73),(x+.09,-.62,13.3))
 # A small fixed set of aligned balusters preserves void, not one mesh per detailed spindle.
 for i in range(14):
  x=.23+i*(w-.46)/13;s.box('baluster '+str(i),(x-.028,-.72,11.92),(x+.028,-.64,12.53))
 s.part='verandah'
 s.box('fascia',(0,-2.465,3.54),(w,-2.335,3.86))
 s.quad('canopy',[(0,0,4.31),(0,-2.47,3.84),(w,-2.47,3.84),(w,0,4.31)])
 for x in (.1,w-.1):s.box('post '+str(x),(x-.07,-2.47,-.12),(x+.07,-2.33,3.54),cage=.2)
 return s.result
