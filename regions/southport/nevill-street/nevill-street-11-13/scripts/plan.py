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

def hood_faces(d):
 c=d['gable_centre'];a=c-1.05;b=c+1.05;v0=.315;v1=d['gable_depth']
 return [('central gable left pitch',[(a,v0,14.65),(c,v0,15.45),(c,v1,14.70),(a,v1,14.40)]),('central gable right pitch',[(c,v0,15.45),(b,v0,14.65),(b,v1,14.40),(c,v1,14.70)])]

def hood_cheeks(d,underside=False):
 c=d['gable_centre'];v0=.315;v1=d['gable_depth'];out=[];off=.07 if underside else 0
 for side,u in [('left',c-1.05),('right',c+1.05)]:
  def top(v):return 14.65-.25*(v-v0)/(v1-v0)-off
  end=v1
  if roof_height(d,u,end)>top(end):
   lo,hi=v0,end
   for _ in range(40):
    mid=(lo+hi)/2
    if roof_height(d,u,mid)>top(mid):hi=mid
    else:lo=mid
   end=lo
  coords=[(u,v0,roof_height(d,u,v0)),(u,end,roof_height(d,u,end)),(u,end,top(end)),(u,v0,top(v0))]
  if abs(coords[1][2]-coords[2][2])<1e-6:coords.pop(2)
  if side=='left':coords=list(reversed(coords))
  out.append(('central gable '+side+' cheek',coords))
 out.append(('central hood back',[(c+1.05,v1,14.20),(c-1.05,v1,14.20),(c-1.05,v1,14.40-off),(c+1.05,v1,14.40-off)]))
 out.append(('central hood back peak',[(c+1.05,v1,14.40-off),(c-1.05,v1,14.40-off),(c,v1,14.70-off)]))
 return out
