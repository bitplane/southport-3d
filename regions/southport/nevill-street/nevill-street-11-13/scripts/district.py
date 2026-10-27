"""Bounded exterior receivers: architecture appearance is baked, never copied."""
import json
from blender_envelope import Surfaces
from plan import world,front_line,roof_faces,gable_profile,hood_faces,hood_cheeks,attachments,attachment_faces,attachment_cheeks

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['width'];l=d['depth'];r=d['corner_radius'];e=d['roof_eave'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p));s.part='frontage'
 line=front_line(d)
 for k,(A,B) in enumerate(zip(line,line[1:])):
  h=d['cornice'] if k==0 else 12.55;s.quad('street and curved corner '+str(k),[(*A,0),(*B,0),(*B,h),(*A,h)],weight=2)
 # Coarse open gate frame: individual receivers preserve the passage openings.
 a,b=9.72,11.87;mid=(a+b)/2
 def gate_quad(name,x0,x1,z0,z1):
  s.quad(name,[(x0,.46,z0),(x1,.46,z0),(x1,.46,z1),(x0,.46,z1)])
 for i,u in enumerate((a+.055,mid,b-.055)):gate_quad('gate upright '+str(i),u-.055,u+.055,0,2.16)
 for i,(left,right) in enumerate(((a+.11,mid-.055),(mid+.055,b-.11))):
  for j,z in enumerate((.055,1.10,2.105)):gate_quad('gate rail '+str(i)+' '+str(j),left,right,z-.055,z+.055)
 for i,z in enumerate((2.22,3.0)):gate_quad('grille rail '+str(i),a,b,z-.0125,z+.0125)
 u=a+(b-a)*12/25;gate_quad('grille bar',u-.0075,u+.0075,2.235,2.985)
 s.part='rear'
 for name,A,B in [('passage',(w,r),(w,l)),('rear',(w,l),(0,l)),('party',(0,l),(0,0))]:s.quad(name,[(*A,0),(*B,0),(*B,e),(*A,e)])
 s.part='roof'
 for name,p in roof_faces(d):
  (s.triangle if len(p)==3 else s.quad)(name,p)
 # Gable front split into rectangle and triangles, preserving the stepped peak.
 c=d['gable_centre'];a=c-1.05;b=c+1.05
 s.quad('central gable front',[(a,0,d['cornice']),(b,0,d['cornice']),(b,0,14.65),(a,0,14.65)],weight=2)
 s.triangle('central gable peak',[(a,0,14.65),(b,0,14.65),(c,0,15.45)],weight=2)
 attachment(s,d,attachments(d)[0])
 for u,v,z0,z1,ww,ll in d['stacks']:
  s.box('capped chimney',(u-ww/2-.09,v-ll/2-.09,z0),(u+ww/2+.09,v+ll/2+.09,z1+.18))
 for u in (1.25,7.35):
  s.quad('dormer front',[(u-.48,0,d['cornice']),(u+.48,0,d['cornice']),(u+.48,0,13.40),(u-.48,0,13.40)])
  s.triangle('dormer peak',[(u-.48,0,13.40),(u+.48,0,13.40),(u,0,13.75)])
  spec=attachments(d)[1 if u==1.25 else 2]
  attachment(s,d,spec)
 return s.result

def attachment(s,d,spec):
 # The distant roof is a single sheet at the detailed slab underside. This
 # joins the same cheek and hip endpoints without a floating 7 cm gap; the
 # atlas projects the tiled outer surface across that omitted thickness.
 for name,points in attachment_faces(d,spec):
  points=[(x,y,z-.07) for x,y,z in points]
  for k in range(1,len(points)-1):s.triangle(name+' '+str(k),[points[0],points[k],points[k+1]])
 for name,points in attachment_cheeks(d,spec):
  for k in range(1,len(points)-1):s.triangle(name+' '+str(k),[points[0],points[k],points[k+1]])
 name,c,h,v0,eave,peak,fall=spec
 profile=[(c+h,d['cornice']),(c+h,eave),(c,peak),(c-h,eave),(c-h,d['cornice'])]
 for i,(a,b) in enumerate(zip(profile,profile[1:])):
  def back(p):return(p[0],v0,p[1]-(.07 if p[1]>d['cornice'] else 0))
  s.quad(name+' stone front return '+str(i),[(a[0],0,a[1]),back(a),back(b),(b[0],0,b[1])])
