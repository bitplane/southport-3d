"""Independent fixed District receivers; no topology from decorative source."""
import json,os
from pathlib import Path
from southport3d.terrain import GroundControls
from blender_envelope import Surfaces
from plan import world,roof
def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w,l,c=d['width'],d['depth'],d['chamfer'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p));s.part='frontage';h=d['parapet']
 for name,A,B in [('front',(c,0),(w,0)),('chamfer',(0,c),(c,0)),('Stanley',(0,l),(0,c))]:s.quad(name,[(*A,0),(*B,0),(*B,h),(*A,h)],weight=2)
 s.part='rear';s.quad('rear',[(w,l,0),(0,l,0),(0,l,d['rear_eave']),(w,l,d['rear_eave'])])
 # Party closure shaped to the actual unequal roof pitches.
 for i,(a,b,z0,z1) in enumerate([(0,d['ridge_v'],d['front_eave'],d['ridge']),(d['ridge_v'],l,d['ridge'],d['rear_eave'])]):s.quad('party '+str(i),[(w,a,0),(w,b,0),(w,b,z1),(w,a,z0)])
 s.part='roof'
 s.quad('front parapet cap',[(c,0,h),(w,0,h),(w,.24,h),(c,.24,h)],weight=.3)
 s.quad('front parapet back',[(w,.24,h),(c,.24,h),(c,.24,d['front_eave']),(w,.24,d['front_eave'])],weight=.3)
 s.quad('Stanley parapet cap',[(0,c,h),(0,l,h),(.24,l,h),(.24,c,h)],weight=.3)
 s.quad('Stanley parapet back',[(.24,c,h),(.24,l,h),(.24,l,d['rear_eave']),(.24,c,d['front_eave'])],weight=.3)
 for name,p in roof(d):
  s.triangle(name+' a',[p[0],p[1],p[2]]);s.triangle(name+' b',[p[0],p[2],p[3]])
 q=d['canopy'];a,b=q['start'],q['end'];v=-q['depth'];zi,zo=q['inner_z'],q['outer_z']
 s.quad('glazed canopy',[(a,0,zi),(a,v,zo),(b,v,zo),(b,0,zi)])
 s.quad('canopy underside',[(b,0,zi-.015),(b,v,zo-.015),(a,v,zo-.015),(a,0,zi-.015)])
 ground=GroundControls(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/ground-controls.json')
 for u in (3.4,9.0,15.7):
  X,Y,_=world(d,(u,v,0));foot=ground.height(X,Y)+.12-d['base_z']
  s.box('canopy post',(u-.045,v-.045,foot),(u+.045,v+.045,zo),weight=.15,cage=.08)
 from courtyard import district
 district(s)
 return s.result
