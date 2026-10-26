"""Measured main envelope shared by detailed masonry and bounded receivers."""
import math

def world(d,p):
 u,v,z=p;x,y,b=d['origin'];return (x+.0135*u-v,y+u-.02087*v,z+b)

def front_line(d,n=8):
 w=d['width'];r=d['corner_radius'];c=w-r
 return [(0,0)]+[(c+r*math.cos(-math.pi/2+math.pi*j/(2*n)),r+r*math.sin(-math.pi/2+math.pi*j/(2*n))) for j in range(n+1)]

def footprint(d):return front_line(d)+[(d['width'],d['depth']),(0,d['depth'])]

def roof_faces(d):
 w=d['width'];l=d['depth'];e=d['roof_eave'];t=d['roof_top'];i=d['roof_inset']
 ov=.10;ee=e-(t-e)*ov/i;A=(-ov,-ov,ee);C=(w+ov,l+ov,ee);D=(-ov,l+ov,ee)
 a=(i,i,t);b=(w-i,i,t);c=(w-i,l-i,t);dd=(i,l-i,t)
 r=d['corner_radius'];arc=[]
 for j in range(9):
  angle=-math.pi/2+j*math.pi/16;u=w-r+(r+ov)*math.cos(angle);v=r+(r+ov)*math.sin(angle);arc.append((u,v,e+(t-e)*min(v,w-u)/i))
 out=[('front pitch',[A,arc[0],b,a]),('north hip',[arc[-1],C,c,b]),('rear pitch',[C,D,dd,c]),('south hip',[D,A,a,dd]),('ridge deck',[a,b,c,dd])]
 # Follow the rounded corner with a 10 cm eave. Pitch intersects wall tops
 # exactly, while the closed slab edge lies outside the wall surface.
 for k in range(4):out.append(('front rounded roof '+str(k),[arc[k],arc[k+1],b]))
 for k in range(4,8):out.append(('north rounded roof '+str(k),[arc[k],arc[k+1],b]))
 return out

def gable_profile(d):
 c=d['gable_centre'];w=d['gable_width']/2;z=d['roof_eave']
 return [(c-w-.32,z),(c+w+.32,z),(c+w+.32,12.55),(c+w,12.80),(c+w,14.65),(c,15.45),(c-w,14.65),(c-w,12.80),(c-w-.32,12.55)]

def roof_height(d,u,v):
 return d['roof_eave']+(d['roof_top']-d['roof_eave'])*min(u,d['width']-u,v,d['depth']-v,d['roof_inset'])/d['roof_inset']

def attachments(d):
 # Roof shoulders and ridge retain the observed front silhouettes. Rear falls
 # are estimated from obliques; each plane ends at the actual hip, not a box cap.
 # The small roofs have separate falls because their host hip heights differ.
 # See research/measurements.json roof.junction_correction for pixel inputs and
 # uncertainty; these inferred junctions are not a measured roof survey.
 return [("central gable",d['gable_centre'],1.05,.315,14.65,15.45,
          (15.45-d['roof_top']-.07)/(d['gable_depth']-.315)),
         ("small dormer left",1.25,.48,.315,13.40,13.75,.49),
         ("small dormer right",7.35,.48,.315,13.40,13.75,.18)]

def clip_face(poly,distance):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da,db=distance(a),distance(b)
  if da>=-1e-9:out.append(a)
  if (da>1e-9 and db< -1e-9) or (da< -1e-9 and db>1e-9):
   t=da/(da-db);out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
 clean=[]
 for p in out:
  p=tuple(round(x,9) for x in p)
  if not clean or sum((a-b)**2 for a,b in zip(p,clean[-1]))>1e-16:clean.append(p)
 if len(clean)>1 and sum((a-b)**2 for a,b in zip(clean[0],clean[-1]))<1e-16:clean.pop()
 return clean if len(clean)>=3 else []

def plane_height(points,u,v):
 a,b,c=points[:3];x=[b[k]-a[k] for k in range(3)];y=[c[k]-a[k] for k in range(3)]
 n=(x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0])
 return a[2]-(n[0]*(u-a[0])+n[1]*(v-a[1]))/n[2]

def attachment_faces(d,spec):
 name,c,h,v0,e,t,fall=spec;out=[]
 # Intersect each pitched plane with the main roof's plan cells. The underside
 # meets the tile surface at the valley; the 7 cm edge is the roof assembly.
 for side,a,b in [('left',c-h,c),('right',c,c+h)]:
  def height(u,v):return t-abs(u-c)*(t-e)/h-fall*(v-v0)
  p=[(a,v0,height(a,v0)),(b,v0,height(b,v0)),(b,6.,height(b,6.)),(a,6.,height(a,6.))]
  for cell,base in roof_faces(d):
   q=p
   for A,B in zip(base,base[1:]+base[:1]):
    q=clip_face(q,lambda P:(B[0]-A[0])*(P[1]-A[1])-(B[1]-A[1])*(P[0]-A[0]))
   q=clip_face(q,lambda P:P[2]-.07-plane_height(base,P[0],P[1]))
   if q:out.append((name+' '+side+' pitch '+cell,q))
 return out

def attachment_cheeks(d,spec):
 name,c,h,v0,e,t,fall=spec;out=[]
 for side,u in [('left',c-h),('right',c+h)]:
  breaks=sorted({v0,6.,*[v for v in (u,d['width']-u,d['roof_inset'],d['depth']-u,d['depth']-d['width']+u,d['depth']-d['roof_inset']) if v0<v<6.]})
  for a,b in zip(breaks,breaks[1:]):
   def top(v):return e-fall*(v-v0)-.07
   da=top(a)-roof_height(d,u,a);db=top(b)-roof_height(d,u,b)
   if max(da,db)<=1e-8:continue
   if da<0:a=a+(b-a)*(-da)/(db-da)
   elif db<0:b=a+(b-a)*da/(da-db)
   q=[(u,a,roof_height(d,u,a)),(u,b,roof_height(d,u,b)),(u,b,top(b)),(u,a,top(a))]
   q=clip_face(q,lambda P:1.)
   if side=='left':q.reverse()
   if q:out.append((name+' '+side+' cheek',q))
 return out

def hood_faces(d):return attachment_faces(d,attachments(d)[0])
def hood_cheeks(d,underside=False):return attachment_cheeks(d,attachments(d)[0])

def hip_ridge_segments(d):
 """Stop ridge caps where roof intersections replace the exposed hip seam."""
 w,l,e,t,i=(d[k] for k in ('width','depth','roof_eave','roof_top','roof_inset'))
 lines=[((0,0,e),(i,i,t)),((w-.2343,.2343,e+(t-e)*.2343/i),(w-i,i,t)),((w,l,e),(w-i,l-i,t)),((0,l,e),(i,l-i,t))]
 out=[]
 for A,B in lines:
  spans=[(0.,1.)]
  def point(q):return tuple(A[k]+q*(B[k]-A[k]) for k in range(3))
  for _,c,h,v0,eave,peak,fall in attachments(d):
   for side in (-1,1):
    # Include the 65 mm cap radius and 40 mm lift in the joint clearance.
    constraints=[lambda p,c=c,h=h:p[0]-c+h+.07,
                 lambda p,c=c,h=h:c+h+.07-p[0],
                 lambda p,v0=v0:p[1]-v0,
                 lambda p,c=c,side=side:side*(p[0]-c),
                 lambda p,c=c,h=h,peak=peak,eave=eave,fall=fall,v0=v0,side=side:peak-side*(p[0]-c)*(peak-eave)/h-fall*(p[1]-v0)-p[2]+.11]
    lo,hi=0.,1.
    for f in constraints:
     a,b=f(A),f(B)
     if a<0 and b<0:lo,hi=1.,0.;break
     if a<0:lo=max(lo,-a/(b-a))
     elif b<0:hi=min(hi,a/(a-b))
    if lo>=hi:continue
    remaining=[]
    for a,b in spans:
     if b<=lo or a>=hi:remaining.append((a,b));continue
     if a<lo:remaining.append((a,lo))
     if b>hi:remaining.append((hi,b))
    spans=remaining
  out.extend((point(a),point(b)) for a,b in spans if b-a>1e-6)
 return out
