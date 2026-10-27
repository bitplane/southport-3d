"""Independent fixed envelopes for Regent Court, podium and service wing."""
import os,sys
from pathlib import Path
from blender_envelope import Surfaces
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/lord-street/corridor-placeholders/scripts'))
from datum import grade

def surfaces(asset):
 base=grade(494,-20)-.15
 s=Surfaces(['tower','roof'],lambda p:(p[0],p[1],p[2]+base))
 s.part='tower'
 # Podium and attached service wall. The diagonal return is retained.
 # Open parking level: structural beams and piers remain open between.
 for x in (481.5,485.8,490.1,494.4,498.7,503,507.3):
  s.quad('podium pier '+str(x),[(x+.175,-9.35,.24),(x-.175,-9.35,.24),(x-.175,-9.35,6.2),(x+.175,-9.35,6.2)],cage=.3)
 for i,(a,b) in enumerate(((481.68,485.62),(485.98,489.92),(490.28,494.22),(494.58,498.52),(498.88,502.82),(503.18,507.12))):
  s.quad('retail '+str(i),[(b,-9.82,.24),(a,-9.82,.24),(a,-9.82,3.1),(b,-9.82,3.1)])
 for lo,hi in ((0,.24),(3.175,3.525),(6.2,6.5)):
  s.quad('podium beam '+str(lo),[(507.4,-9.6,lo),(481.4,-9.6,lo),(481.4,-9.6,hi),(507.4,-9.6,hi)])
 for x in (481.4,507.4):
  p=[(x,-29.6,.24),(x,-9.6,.24),(x,-9.6,6.2),(x,-29.6,6.2)]
  s.quad('podium end '+str(x),list(reversed(p)) if x==481.4 else p)
 s.quad('podium rear',[(481.4,-29.6,.24),(507.4,-29.6,.24),(507.4,-29.6,6.2),(481.4,-29.6,6.2)])
 service_plan=[(483.5,-29.9),(499.1,-29.9),(499.1,-49.4),(496.8,-51.9),(485.8,-51.9),(483.5,-49.4)]
 for i,(a,b) in enumerate(zip(service_plan,service_plan[1:]+service_plan[:1])):
  s.quad('service wall '+str(i),[(b[0],b[1],0),(a[0],a[1],0),(a[0],a[1],4.65),(b[0],b[1],4.65)])
 # Perimeter of two wings, including the recessed west side.
 for name,plan in [('west',[(481.5,-28.6),(492.5,-28.6),(492.5,-10.6),(481.5,-10.6),(481.5,-14),(485,-14),(485,-24),(481.5,-24)]),('east',[(495.9,-28.6),(506.9,-28.6),(506.9,-10.6),(495.9,-10.6)])]:
  for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
   # The middle of the inside wall is enclosed, not an exposed source skin.
   inside=(name=='west' and i==1) or (name=='east' and i==3)
   intervals=((-28.6,-25.6),(-13.6,-10.6)) if inside else ((a[1],b[1]),)
   for j,(y0,y1) in enumerate(intervals):
    if inside:
     if b[1]<a[1]:y0,y1=y1,y0
     p=[(a[0],y0,6.5),(a[0],y1,6.5),(a[0],y1,34.5),(a[0],y0,34.5)]
    else:p=[(a[0],a[1],6.5),(b[0],b[1],6.5),(b[0],b[1],34.5),(a[0],a[1],34.5)]
    s.quad(name+' wall '+str((i,j)),p)
 for name,p in [('core front',[(495.9,-13.6,6.5),(492.5,-13.6,6.5),(492.5,-13.6,34.5),(495.9,-13.6,34.5)]),('core rear',[(492.5,-25.6,6.5),(495.9,-25.6,6.5),(495.9,-25.6,34.5),(492.5,-25.6,34.5)])]:s.quad(name,p)
 # Fixed simplified balcony slabs preserve the projecting silhouette; the
 # envelope count remains unchanged when fine railings or windows change.
 for y,sign in ((-10.6,1),(-28.6,-1)):
  for cx in (487,501.4):
   for i in range(10):
    z=6.5+i*2.8+.01
    a=(cx-1.115,min(y,y+sign*1.17),z);b=(cx+1.115,max(y,y+sign*1.17),z+.18)
    s.box('balcony slab '+str((y,cx,i)),a,b,omit=('bottom','rear' if sign==1 else 'front'),cage=.25)
 s.part='roof'
 # Explicit perimeter and deck, including roof opening outline.
 s.box('roof border north',(480.7,-11.6,34.5),(507.7,-9.6,35),omit=('bottom',))
 s.box('roof border south',(480.7,-29.6,34.5),(507.7,-27.6,35),omit=('bottom',))
 s.box('roof border west',(480.7,-27.6,34.5),(482.7,-11.6,35),omit=('bottom',))
 s.box('roof border east',(505.7,-27.6,34.5),(507.7,-11.6,35),omit=('bottom',))
 for name,x0,x1,y0,y1 in [('south',482.7,505.7,-27.6,-23),('north',482.7,505.7,-21,-11.6),('left',482.7,484,-23,-21),('middle',486,502.4,-23,-21),('right',504.4,505.7,-23,-21)]:
  s.quad('roof deck '+name,[(x0,y0,34.5),(x1,y0,34.5),(x1,y1,34.5),(x0,y1,34.5)],cage=.2)
 s.box('roof access',(487.8,-22,34.5),(491.8,-19.6,35.8),omit=('bottom',))
 s.quad('lantern slope one',[(491.7,-19.5,34.6),(495.4,-19.5,34.6),(495.4,-20.35,35.35),(491.7,-20.35,35.35)],cage=.2)
 s.quad('lantern slope two',[(495.4,-21.2,34.6),(491.7,-21.2,34.6),(491.7,-20.35,35.35),(495.4,-20.35,35.35)],cage=.2)
 # Flat service roof uses fixed triangles via four quads in a convex fan.
 center=(491.3,-40.9,4.65)
 for i,(a,b) in enumerate(zip(service_plan,service_plan[1:]+service_plan[:1])):
  s.triangle('service roof '+str(i),[center,(b[0],b[1],4.65),(a[0],a[1],4.65)],cage=.3)
 return s.result
