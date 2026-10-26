"""Bounded corner envelope: six curved facets, coarse columns and open canopy."""
import json,math,os
from pathlib import Path
from southport3d.terrain import GroundControls
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());W=d['width'];L=d['depth'];R=d['radius'];A=R*math.pi/2
 def T(p):x,y,z=p;return d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x,d['base_z']+z
 s=Surfaces(['facades','roof','frontage','canopy'],T)
 def face(name,p,side='front',**kwargs):
  if side=='front':q=[(u,-out,z) for u,z,out in p]
  elif side=='side':q=list(reversed([(-out,u,z) for u,z,out in p]))
  else:q=[(R+(R+out)*math.cos(math.pi+u/R),R+(R+out)*math.sin(math.pi+u/R),z) for u,z,out in p]
  s.quad(name,q,**kwargs)
 def panel(name,a,b,lo,hi,out,side,**kwargs):face(name,[(a,lo,out),(b,lo,out),(b,hi,out),(a,hi,out)],side,**kwargs)
 s.part='facades'
 for side,end in [('front',W),('side',L)]:
  panel(side+' upper wall',R,end,4.55,14.10,.015,side)
  panel(side+' parapet',R,end,14.10,14.45,0,side,cage=.22)
  face(side+' parapet top',[(R,14.54,-.345),(R,14.54,.085),(end,14.54,.085),(end,14.54,-.345)],side,cage=.12,weight=.4)
  # Fixed stepped envelope follows the projecting arched pavilions.
  segments=[(R,7.15,.18),(7.15,W,0)] if side=='front' else [(R,7.15,.18),(7.15,17.45,0),(17.45,21.45,.18),(21.45,L,0)]
  for i,(a,b,offset) in enumerate(segments):
   panel(side+' cornice '+str(i),a,b,12.60,14.10,.30+offset,side,cage=.48)
   face(side+' cornice underside '+str(i),[(a,12.60,offset),(b,12.60,offset),(b,12.60,.30+offset),(a,12.60,.30+offset)],side,cage=.48,weight=.3)
   face(side+' cornice top '+str(i),[(a,14.10,.30+offset),(b,14.10,.30+offset),(b,14.10,offset),(a,14.10,offset)],side,cage=.48,weight=.3)
  profile=[(12.60,0),(12.60,.14),(12.72,.14),(12.78,.24),(12.95,.24),(13.05,.36),(13.18,.36),(13.22,.12),(13.62,.12),(13.68,.28),(13.77,.33),(13.87,.45),(14.00,.45),(14.06,.11),(14.10,0)]
  for i,(left,right) in enumerate(zip(segments,segments[1:])):
   u=left[1];d0=left[2];d1=right[2]
   for j,((z0,o0),(z1,o1)) in enumerate(zip(profile,profile[1:])):
    if z1==z0:continue
    face(f'{side} cornice step {i} {j}',[(u,z0,o0+d0),(u,z0,o0+d1),(u,z1,o1+d1),(u,z1,o1+d0)],side,cage=.10,weight=.4)
  for b in d['front_bays' if side=='front' else 'side_bays']:
   if not b['arch']:continue
   u=b['u'];panel(side+' raised panel '+str(u),u-1.775,u+1.775,14.45,14.98,.08,side,cage=.25)
   face(side+' raised cap '+str(u),[(u-1.85,15.04,.13),(u+1.85,15.04,.13),(u+1.85,15.04,-.33),(u-1.85,15.04,-.33)],side,cage=.13,weight=.4)
 for name,side,u,w,top in [('Nevill A','side',10.5,.75,14.80),('Nevill B','side',14.0,.75,14.80),('Lord end','front',W-.25,.48,15.10)]:
  for suffix,lo,hi,width,front,back in [('body',14.44,top,w,.10,-.26),('cap',top,top+.10,w+.12,.15,-.31)]:
   a=u-width/2;b=u+width/2
   panel(name+suffix,a,b,lo,hi,front,side,cage=.14)
   face(name+suffix+' top',[(a,hi,front),(b,hi,front),(b,hi,back),(a,hi,back)],side,cage=.14,weight=.4)
   for edge in (a,b):face(name+suffix+str(edge),[(edge,lo,back),(edge,lo,front),(edge,hi,front),(edge,hi,back)],side,cage=.14,weight=.4)
 for j in range(6):
  a=A*j/6;b=A*(j+1)/6
  panel('corner wall '+str(j),a,b,4.55,14.10,.015,'curve',cage=.48)
  panel('corner cornice '+str(j),a,b,12.60,14.10,.48,'curve',cage=.50)
  face('corner cornice top '+str(j),[(a,14.10,.48),(b,14.10,.48),(b,14.10,.18),(a,14.10,.18)],'curve',cage=.5,weight=.3)
  # Balustrade remains open: rail, paired piers, never a solid parapet sheet.
  panel('corner rail '+str(j),a,b,14.51,14.61,.08,'curve',cage=.15,weight=.5)
  face('corner rail top '+str(j),[(a,14.61,.08),(b,14.61,.08),(b,14.61,-.30),(a,14.61,-.30)],'curve',cage=.15,weight=.5)
 for j in range(13):
  u=A*j/12
  panel('baluster '+str(j),u-.07,u+.07,14.115,14.545,.005,'curve',cage=.15,weight=.4)
 for name,side,u in [('side column A','side',10.5),('side column B','side',14.0),('corner column A','curve',.45),('corner column B','curve',A-.45)]:
  # Eight sides, two shaft intervals and a rectangular capital: topology fixed.
  rings=[(4.55,.50),(5.0,.42),(12.05,.36),(12.48,.47)]
  for k,((lo,r),(hi,rr)) in enumerate(zip(rings,rings[1:])):
   for j in range(8):
    a=math.tau*j/8;b=math.tau*(j+1)/8
    face(name+f' {k} {j}',[(u+r*math.cos(a),lo,.20-r*math.sin(a)),(u+r*math.cos(b),lo,.20-r*math.sin(b)),(u+rr*math.cos(b),hi,.20-rr*math.sin(b)),(u+rr*math.cos(a),hi,.20-rr*math.sin(a))],side,cage=.25,weight=.6)
  panel(name+' capital',u-.54,u+.54,12.44,12.60,.685,side,cage=.25,weight=.5)
 # Actual rear boundary and its small open service recess.
 a,b=d['lightwell']['x'];lo,hi=d['lightwell']['y'];p=[(W,0),(W,L),(b,L),(b,lo),(a,lo),(a,L),(0,L)]
 for j,(v,w) in enumerate(zip(p,p[1:])):
  low=8.7 if j in (2,3,4) else 0
  s.quad('rear skin '+str(j),[(*v,low),(*w,low),(*w,13.85),(*v,13.85)],cage=.35,weight=.7)
 s.quad('lower rear below well',[(a,L,0),(a,L,8.7),(b,L,8.7),(b,L,0)],cage=.2,weight=.7)
 s.part='frontage'
 for side,end in [('front',W),('side',L)]:panel(side+' shopfront',2,end,.03,4.55,.025,side,cage=.24)
 q=[(0,2,.03),(2,0,.03),(2,0,4.55),(0,2,4.55)];s.quad('chamfered entrance',q,cage=.25)
 s.part='roof'
 # Independent plan, four roof corner segments, preserving the rear notch.
 p=[(R,0),(W,0),(W,L),(b,L),(b,lo),(a,lo),(a,L),(0,L),(0,R)]+[(R+R*math.cos(math.pi+math.pi*j/8),R+R*math.sin(math.pi+math.pi*j/8)) for j in range(1,4)]
 points=[Vector((x,y,13.85)) for x,y in p]
 for j,tri in enumerate(tessellate_polygon([points])):s.triangle('membrane '+str(j),[points[v] if isinstance(v,int) else v for v in tri],cage=.7)
 s.quad('well floor',[(a,lo,8.7),(b,lo,8.7),(b,hi,8.7),(a,hi,8.7)],cage=.12,weight=.5)
 s.box('air handler',(9.5,18.1,13.85),(11.9,21.5,14.91),cage=.15)
 # One connected service run has no overlapping top faces or internal end caps.
 p=[(4.16,9.2),(4.64,9.2),(4.64,13.46),(7.34,13.46),(7.34,17.86),(9.9,17.86),(9.9,18.34),(6.86,18.34),(6.86,13.94),(4.16,13.94)]
 pts=[Vector((x,y,14.44)) for x,y in p]
 for j,tri in enumerate(tessellate_polygon([pts])):s.triangle('duct top '+str(j),[pts[v] if isinstance(v,int) else v for v in tri],cage=.12,weight=.6)
 for j,(a,b) in enumerate(zip(p,p[1:]+p[:1])):s.quad('duct side '+str(j),[(*a,13.96),(*b,13.96),(*b,14.44),(*a,14.44)],cage=.12,weight=.6)
 s.part='canopy'
 path=[(0,L,-1,0),(0,R,-1,0)]+[(R+R*math.cos(math.pi+math.pi*j/12),R+R*math.sin(math.pi+math.pi*j/12),math.cos(math.pi+math.pi*j/12),math.sin(math.pi+math.pi*j/12)) for j in range(1,7)]+[(W,0,0,-1)]
 def v(p,out,z):x,y,nx,ny=p;return x+nx*out,y+ny*out,z
 for j,(a,b) in enumerate(zip(path,path[1:])):
  # Split long straight lengths at structural spans for useful atlas islands.
  n=max(1,math.ceil(math.dist(a[:2],b[:2])/5))
  for k in range(n):
   aa=tuple(a[i]+(b[i]-a[i])*k/n for i in range(4));bb=tuple(a[i]+(b[i]-a[i])*(k+1)/n for i in range(4))
   s.quad(f'roof {j} {k}',[v(aa,3.05,4.02),v(bb,3.05,4.02),v(bb,.12,4.55),v(aa,.12,4.55)],cage=.30)
   s.quad(f'soffit {j} {k}',[v(aa,.12,4.53),v(bb,.12,4.53),v(bb,3.05,4.00),v(aa,3.05,4.00)],cage=.30,weight=.6)
   s.quad(f'fascia {j} {k}',[v(aa,3.05,3.15),v(bb,3.05,3.15),v(bb,3.05,3.35),v(aa,3.05,3.35)],cage=.15,weight=.6)
 ground=GroundControls(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/ground-controls.json')
 for side,positions in [('front',d['canopy_posts_front']),('side',d['canopy_posts_side'])]:
  for k,u in enumerate(positions):
   X,Y,_=T((u,-3.05,0) if side=='front' else (-3.05,u,0));foot=ground.height(X,Y)+.12-d['base_z']
   for j in range(6):
    a=math.tau*j/6;b=math.tau*(j+1)/6
    face(f'{side} post {k} {j}',[(u+.065*math.cos(a),foot,3.05-.065*math.sin(a)),(u+.065*math.cos(b),foot,3.05-.065*math.sin(b)),(u+.065*math.cos(b),3.15,3.05-.065*math.sin(b)),(u+.065*math.cos(a),3.15,3.05-.065*math.sin(a))],side,cage=.14,weight=.6)
 return s.result
