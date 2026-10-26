import json
from blender_envelope import Surfaces
from plan import world,roofs
def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());h,w,l=d['hall_width'],d['width'],d['depth'];e=d['bath_eave'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p))
 def q(n,p):s.quad(n,list(reversed(p)))
 def wall(n,a,b,z0,z1):q(n,[(*a,z0),(*b,z0),(*b,z1),(*a,z1)])
 s.part='frontage';wall('hall',(0,0),(h,0),-.6,7.65);wall('corner',(h,0),(w,0),-.6,e)
 s.part='rear';wall('Bath',(w,0),(w,l),-.6,e);wall('end',(w,l),(h,l),-.6,e);wall('court',(h,l),(h,23.2),-.6,e);wall('court upper',(h,23.2),(h,0),7.1,e);wall('hall rear',(h,23.2),(0,23.2),-.6,7.1);wall('party',(0,23.2),(0,0),-.6,7.1)
 s.part='roof'
 for n,p in roofs(d):q(n,p)
 wall('roof step',(h,9),(0,9),7.1,7.65)
 # Fixed end roof triangles and shallow fascia silhouette.
 for v in [0,l]:
  ps=[(h,v,e),(w,v,e),((h+w)/2,v,d['bath_ridge'])]
  if v==l:ps.reverse()
  s.triangle('Bath gable '+str(v),list(reversed(ps)))
 for v in [1.6,l-1.4]:
  # Authored chimney envelope independent of detail generator.
  u=(h+w)/2;lo,hi=u-.55,u+.55;va,vb=v-.325,v+.325
  wall('chimney front '+str(v),(lo,va),(hi,va),12.55,13.65);wall('chimney side '+str(v),(hi,va),(hi,vb),12.55,13.65);wall('chimney back '+str(v),(hi,vb),(lo,vb),12.55,13.65);wall('chimney side2 '+str(v),(lo,vb),(lo,va),12.55,13.65);q('chimney top '+str(v),[(lo,va,13.65),(hi,va,13.65),(hi,vb,13.65),(lo,vb,13.65)])
 return s.result
