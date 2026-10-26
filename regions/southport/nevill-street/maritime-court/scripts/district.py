"""Fixed L-envelope: topology/atlas independent of windows, lettering and railings."""
from blender_envelope import Surfaces
from plan import D,world,outline,facade,strips,TALL
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
def surfaces(asset):
 s=Surfaces(['architecture'],world)
 for i in range(6):
  l,at=facade(i);low=D['podium'] if i in (2,3) else -.15;bands=strips(i)
  for j,(a,b,o,top) in enumerate(bands):
   s.quad(f'elevation{i} strip{j}',[at(a,low,o),at(b,low,o),at(b,top,o),at(a,top,o)])
   if o:s.quad(f'coping{i} strip{j}',[at(a,top,o),at(b,top,o),at(b,top,0),at(a,top,0)],weight=.2)
  for j,(left,right) in enumerate(zip(bands,bands[1:])):
   x=left[1];o0,o1=left[2],right[2];top=max(left[3],right[3])
   if o0!=o1:s.quad(f'projection{i}-{j}',[at(x,low,o0),at(x,low,o1),at(x,top,o1),at(x,top,o0)],weight=.3)
  if i in (2,3):
   s.quad(f'undercroft{i}',[at(0,-.1,-2.4),at(l,-.1,-2.4),at(l,D['podium'],-2.4),at(0,D['podium'],-2.4)])
   s.quad(f'soffit{i}',[at(0,D['podium'],0),at(l,D['podium'],0),at(l,D['podium'],-2.4),at(0,D['podium'],-2.4)],weight=.2)
   for k,x in enumerate([.3]+TALL[i]+[l-.3]):
    a,b=max(0,x-.22),min(l,x+.22)
    s.quad(f'column{i}-{k}',[at(a,-.1,0),at(b,-.1,0),at(b,D['podium'],0),at(a,D['podium'],0)],weight=.2)
    s.quad(f'columnleft{i}-{k}',[at(a,-.1,0),at(a,D['podium'],0),at(a,D['podium'],-2.4),at(a,-.1,-2.4)],weight=.2)
    s.quad(f'columnright{i}-{k}',[at(b,D['podium'],0),at(b,-.1,0),at(b,-.1,-2.4),at(b,D['podium'],-2.4)],weight=.2)
 p=[Vector((x,y,D['roof']))for x,y in outline()]
 for i,tri in enumerate(tessellate_polygon([p])):s.triangle('roof'+str(i),[tuple(p[k])if isinstance(k,int)else tuple(k)for k in tri],weight=.6)
 s.box('lift',(9.5,10.3,D['roof']),(15,15.6,D['lift_top']))
 s.box('porch',(7.2,-1.45,2.85),(11,-.1,3.10))
 return s.result
