"""Fixed topology receivers share dimensions, not the detailed facade mesh."""
import json
from blender_envelope import Surfaces
from plan import world,roof_faces,wing_roof

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());W=d['width'];L=d['depth'];E=d['cornice'];bay=d['end_bay_start'];a,b,c,e,h,r=d['rear_wing'];q,Q,v,V,hh,rr=d['low_rear']
 s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p));s.part='frontage'
 line=[(0,0),(bay,0),(bay+.26,-.25),(W-.26,-.25),(W,0)]
 for A,B in zip(line,line[1:]):s.quad('street facade',[(*A,0),(*B,0),(*B,E),(*A,E)],weight=2)
 s.triangle('terminal pediment',[(bay-.02,-.44,E-.12),(W+.02,-.44,E-.12),((bay+W)/2,-.44,E+.61)],weight=1.5)
 s.part='rear'
 s.quad('south party wall',[(0,L,0),(0,0,0),(0,0,d['roof_eave']),(0,L,d['roof_eave'])])
 s.quad('north party wall',[(W,0,0),(W,L,0),(W,L,d['roof_eave']),(W,0,d['roof_eave'])])
 for lo,hi,z in [(Q,a,0),(0,Q,hh),(a,b,h),(b,W,0)]:s.quad('main rear',[(hi,L,z),(lo,L,z),(lo,L,d['roof_eave']),(hi,L,d['roof_eave'])])
 for label,spec in [('wing',d['rear_wing']),('low',d['low_rear'])]:
  a,b,c,e,h,r=spec
  for A,B in [((a,e),(a,c)),((b,c),(b,e)),((b,e),(a,e))]:s.quad(label+' wall',[(*A,0),(*B,0),(*B,h),(*A,h)])
  s.triangle(label+' gable',[(b,e,h),(a,e,h),((a+b)/2,e,r)])
 a,b,c,e,h,r=d['rear_wing'];z0=d['roof_eave'];delta=(z0-h)/(r-h)*(b-a)/2
 if r>z0:s.triangle('wing junction gable',[(a+delta,c,z0),(b-delta,c,z0),((a+b)/2,c,r)])
 s.part='roof'
 for name,p in roof_faces(d):s.quad(name,p)
 for label,spec in [('wing',d['rear_wing']),('low',d['low_rear'])]:
  for i,p in enumerate(wing_roof(spec)):s.quad(label+' roof '+str(i),p)
 s.box('raised roof cover',(2.9,3.725,d['roof_top']),(W-2.9,5.175,d['roof_top']+.14))
 return s.result
