"""Fixed independent envelope; omitted canopy curvature and joinery."""
import os,sys
from pathlib import Path
from blender_envelope import Surfaces
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/marine-drive/frontage-placeholders/scripts'))
from datum import grade

def surfaces(asset):
 base=grade(-45.6,660.6)-.25
 def T(p):
  x,y,z=p;X=17.4-y*17.4/20.8;Y=x*20.8/17.4;return (-55.41+.9936*X+.1128*Y,669.959+.1128*X-.9936*Y,base+z)
 s=Surfaces(['walls','roof','joinery'],T);s.part='walls';W=17.4;D=20.8
 # Reversed to account for the reflected local plan frame.
 for name,p in [('rear',[(W,D,0),(0,D,0),(0,D,3.25),(W,D,3.25)]),('left',[(0,D,0),(0,0,0),(0,0,3.25),(0,D,3.25)]),('right',[(W,0,0),(W,D,0),(W,D,3.25),(W,0,3.25)])]:s.quad(name,list(reversed(p)))
 # Doorway recess is modelled in the independent envelope rather than only painted.
 for name,p in [('front left',[(0,0,0),(7.1,0,0),(7.1,0,3.25),(0,0,3.25)]),('front right',[(8.3,0,0),(W,0,0),(W,0,3.25),(8.3,0,3.25)]),('front sill',[(7.1,0,0),(8.3,0,0),(8.3,0,.2),(7.1,0,.2)]),('front head',[(7.1,0,2.56),(8.3,0,2.56),(8.3,0,3.25),(7.1,0,3.25)]),('door recessed',[(7.1,.12,.2),(8.3,.12,.2),(8.3,.12,2.56),(7.1,.12,2.56)]),('door left',[(7.1,0,.2),(7.1,.12,.2),(7.1,.12,2.56),(7.1,0,2.56)]),('door right',[(8.3,.12,.2),(8.3,0,.2),(8.3,0,2.56),(8.3,.12,2.56)]),('door soffit',[(7.1,0,2.56),(7.1,.12,2.56),(8.3,.12,2.56),(8.3,0,2.56)]),('door threshold',[(7.1,0,.2),(8.3,0,.2),(8.3,.12,.2),(7.1,.12,.2)])]:s.quad(name,list(reversed(p)))
 s.part='roof'
 outer=[(-.5,-.5,3.45),(W+.5,-.5,3.45),(W+.5,D+.5,3.45),(-.5,D+.5,3.45)];inner=[(3.4,3.5,4.25),(14,3.5,4.25),(14,17.3,4.25),(3.4,17.3,4.25)];top=[(4,4.1,5.75),(13.4,4.1,5.75),(13.4,16.7,5.75),(4,16.7,5.75)]
 for i in range(4):
  j=(i+1)%4;s.quad('lower '+str(i),list(reversed([outer[i],outer[j],inner[j],inner[i]])));s.quad('raised '+str(i),list(reversed([inner[i],inner[j],top[j],top[i]])))
 inside=[(4.28,4.38,5.75),(13.12,4.38,5.75),(13.12,16.42,5.75),(4.28,16.42,5.75)];low=[(4.28,4.38,4.55),(13.12,4.38,4.55),(13.12,16.42,4.55),(4.28,16.42,4.55)]
 for i in range(4):
  j=(i+1)%4;s.quad('cap '+str(i),list(reversed([top[i],top[j],inside[j],inside[i]])));s.quad('inside '+str(i),list(reversed([inside[i],inside[j],low[j],low[i]])))
 s.quad('plant deck',list(reversed(low)))
 s.part='joinery';s.quad('canopy',list(reversed([(4.1,-1.25,3.45),(10.5,-1.25,3.45),(10.5,0,3.45),(4.1,0,3.45)])))
 return s.result
