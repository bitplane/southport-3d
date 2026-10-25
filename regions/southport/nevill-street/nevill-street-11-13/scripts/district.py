"""Bounded exterior receivers: architecture appearance is baked, never copied."""
import json
from blender_envelope import Surfaces
from plan import world,front_line,roof_faces,gable_profile,hood_faces,hood_cheeks

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['width'];l=d['depth'];r=d['corner_radius'];e=d['roof_eave'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p));s.part='frontage'
 line=front_line(d)
 for k,(A,B) in enumerate(zip(line,line[1:])):
  h=d['cornice'] if k==0 else 12.55;s.quad('street and curved corner '+str(k),[(*A,0),(*B,0),(*B,h),(*A,h)],weight=2)
 s.part='rear'
 for name,A,B in [('passage',(w,r),(w,l)),('rear',(w,l),(0,l)),('party',(0,l),(0,0))]:s.quad(name,[(*A,0),(*B,0),(*B,e),(*A,e)])
 s.part='roof'
 for name,p in roof_faces(d):
  (s.triangle if len(p)==3 else s.quad)(name,p)
 # Gable front split into rectangle and triangles, preserving the stepped peak.
 c=d['gable_centre'];a=c-1.05;b=c+1.05
 s.quad('central gable front',[(a,0,d['cornice']),(b,0,d['cornice']),(b,0,14.65),(a,0,14.65)],weight=2)
 s.triangle('central gable peak',[(a,0,14.65),(b,0,14.65),(c,0,15.45)],weight=2)
 for name,points in hood_faces(d)+hood_cheeks(d):
  (s.triangle if len(points)==3 else s.quad)(name,points)
 for u,v,z0,z1,ww,ll in d['stacks']:
  s.box('capped chimney',(u-ww/2-.09,v-ll/2-.09,z0),(u+ww/2+.09,v+ll/2+.09,z1+.18))
 for u in (1.25,7.35):
  s.quad('dormer front',[(u-.48,0,d['cornice']),(u+.48,0,d['cornice']),(u+.48,0,12.88),(u-.48,0,12.88)])
  s.triangle('dormer peak',[(u-.48,0,12.88),(u+.48,0,12.88),(u,0,13.18)])
  v=.775;z=e+(d['roof_top']-e)*v/d['roof_inset']
  s.quad('dormer left cheek',[(u-.48,v,z),(u-.48,0,d['cornice']),(u-.48,0,12.88),(u-.48,v,12.88)])
  s.quad('dormer right cheek',[(u+.48,0,d['cornice']),(u+.48,v,z),(u+.48,v,12.88),(u+.48,0,12.88)])
  s.quad('dormer back',[(u+.48,v,z),(u-.48,v,z),(u-.48,v,12.88),(u+.48,v,12.88)])
  s.triangle('dormer back peak',[(u+.48,v,12.88),(u-.48,v,12.88),(u,v,13.18)])
  s.quad('dormer left rake',[(u-.48,0,12.88),(u,0,13.18),(u,v,13.18),(u-.48,v,12.88)])
  s.quad('dormer right rake',[(u,0,13.18),(u+.48,0,12.88),(u+.48,v,12.88),(u,v,13.18)])
 return s.result
