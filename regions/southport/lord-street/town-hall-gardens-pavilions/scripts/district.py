"""Independently authored, fixed-budget pavilion walls, roof and supports."""
import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());s=Surfaces(['north','south'],lambda p:p)
 for b in d['pavilions']:
  s.part=b['id'];p=b['footprint'];n=len(p);cx=sum(x for x,y in p)/n;cy=sum(y for x,y in p)/n;z=b['base_m'];e=z+b['eave_m'];ap=z+b['ridge_m']
  winding=sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(p,p[1:]+p[:1]))
  for i,a in enumerate(p):
   c=p[(i+1)%n];wall=[(a[0],a[1],z-.18),(c[0],c[1],z-.18),(c[0],c[1],e),(a[0],a[1],e)]
   s.quad('wall '+str(i),wall if winding>0 else list(reversed(wall)))
  over=[]
  for x,y in p:
   dx=x-cx;dy=y-cy;r=math.hypot(dx,dy);over.append((x+.48*dx/r,y+.48*dy/r,e+.04))
  ridge=[(cx,cy-1.8,ap),(cx,cy+1.8,ap)]
  for i,a in enumerate(p):
   j=(i+1)%n;c=p[j];r=0 if a[1]<cy else 1;t=0 if c[1]<cy else 1
   roof=[over[i],over[j],ridge[t],ridge[r]] if r!=t else [over[i],over[j],ridge[r]]
   cross=(roof[1][0]-roof[0][0])*(roof[2][1]-roof[0][1])-(roof[1][1]-roof[0][1])*(roof[2][0]-roof[0][0])
   if cross<0:roof.reverse()
   if len(roof)==3:s.triangle('roof '+str(i),roof)
   else:s.quad('roof '+str(i),roof)
   x,y,_=over[i];s.box('canopy post '+str(i),(x-.055,y-.055,z-.18),(x+.055,y+.055,e-.1),cage=.20)
 return s.result
