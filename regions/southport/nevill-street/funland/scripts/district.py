"""Fixed receivers: roof volumes, scalloped frontage, provisional tent; atlas stays fixed."""
import math
from blender_envelope import Surfaces
from plan import D,W,L,world,top,XS,YS,at,canopy_ring
def surfaces(asset):
 s=Surfaces(['architecture','carousel'],world)
 for side,length,cuts,heights in [('front',W,XS,lambda x:top(x,.01)),('north',L,YS,lambda y:top(W-.01,y)),('rear',W,[0,W],lambda x:top(W-x,L-.01)),('pier',L,sorted(L-y for y in YS),lambda y:top(.01,L-y))]:
  f=at(side)
  for a,b in zip(cuts,cuts[1:]):
   z=heights((a+b)/2);s.quad(side+str(a),[f(a,D['footing']),f(b,D['footing']),f(b,z),f(a,z)])
 for x,X in zip(XS,XS[1:]):
  for y,Y in zip(YS,YS[1:]):
   z=top((x+X)/2,(y+Y)/2);s.quad('roof'+str((x,y)),[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z)],weight=.4)
 for x in XS[1:-1]:
  for y,Y in zip(YS,YS[1:]):
   a,b=top(x-.001,(y+Y)/2),top(x+.001,(y+Y)/2)
   if a!=b:
    p=[(x,y,min(a,b)),(x,Y,min(a,b)),(x,Y,max(a,b)),(x,y,max(a,b))];s.quad('roofreturnX'+str((x,y)),p if a>b else list(reversed(p)),weight=.4)
 for y in YS[1:-1]:
  for x,X in zip(XS,XS[1:]):
   a,b=top((x+X)/2,y-.001),top((x+X)/2,y+.001)
   if a!=b:
    p=[(X,y,min(a,b)),(x,y,min(a,b)),(x,y,max(a,b)),(X,y,max(a,b))];s.quad('roofreturnY'+str((x,y)),p if a>b else list(reversed(p)),weight=.4)
 for k in range(8):
  for j in range(8):
   x0=(k+j/8)*W/8;x1=(k+(j+1)/8)*W/8;z0=8.65-.45*math.sin(math.pi*j/8);z1=8.65-.45*math.sin(math.pi*(j+1)/8)
   for name,p in [('front',[(x0,0,8.05),(x1,0,8.05),(x1,0,z1),(x0,0,z0)]),('back',[(x1,.2,8.05),(x0,.2,8.05),(x0,.2,z0),(x1,.2,z1)]),('top',[(x0,0,z0),(x1,0,z1),(x1,.2,z1),(x0,.2,z0)])]:s.quad('scallop'+str((k,j))+name,p,weight=.2)
 s.part='carousel';r=D['carousel']['radius'];cx,cy=D['carousel']['centre'];bottom=canopy_ring(r*.79,-.25);mid=canopy_ring(r*.79,3.55);edge=canopy_ring(r,3.8);shoulder=canopy_ring(r*.42,5.7);tip=(cx,cy,10)
 for i in range(16):
  j=(i+1)%16;s.quad('enclosure'+str(i),[bottom[i],bottom[j],mid[j],mid[i]])
  s.quad('canopy'+str(i),[edge[i],edge[j],shoulder[j],shoulder[i]])
  s.triangle('cap'+str(i),[shoulder[i],shoulder[j],tip])
 return s.result
