"""Measured main surfaces. Decoration never controls receiver topology."""
import math
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cuts(p,holes):
 out=[p]
 for h in holes:out=[q for poly in out for q in subtract(poly,h)]
 return out

def transform(d,p):
 x,y,z=p
 return(d['front_origin'][0]+x+d['side_shear']*y,d['front_origin'][1]+y+d['front_shear']*x,d['floor_z']+z)

def canopy_profile(d,n=12):
 c=d['canopy'];P=c['projection']
 return [(P*i/n,c['wall_z']+(c['spring_z']-c['wall_z'])*i/n+c['arch_rise']*math.sin(math.pi*i/n)) for i in range(n+1)]

def roofs(d):
 w=d['front_width'];b=d['main_depth'];r=d['ridge_y'];E=d['front_eaves'];H=d['front_ridge'];B=d['rear_eaves'];out=[]
 # Main frontage pitched roof and the rear wings meet at actual valleys.
 out.append(('main front',[(0,0,E),(w,0,E),(w,r,H),(0,r,H)]))
 holes=[]
 for v in d['wings']:
  a,c,end,h,e=v['x0'],v['x1'],v['end'],v['ridge'],v['eaves'];m=(a+c)/2
  join=r+(H-h)*(b-r)/(H-B);holes.append([(a,b),(m,join),(c,b)])
  out += [(v['id']+' west',[(a,b,B),(m,join,h),(m,end,h),(a,end,e)]),(v['id']+' east',[(m,join,h),(c,b,B),(c,end,e),(m,end,h)])]
 for i,p in enumerate(cuts(rect(0,r,w,b),holes)):
  out.append(('main rear '+str(i),[(x,y,H+(B-H)*(y-r)/(b-r)) for x,y in p]))
 if d['kind']=='bank':
  # Three front projecting steep gabled rooflets: main roof skin is clipped beneath.
  main=out[0][1];hs=[]
  for cx in d['bay_centres'][1:]:
   a,c=cx-1.65,cx+1.65;h=10.95;ey=8.65;end=(h-E)*r/(H-E);hs.append([(a,0),(c,0),(cx,end)])
   out += [('bay roof west',[(a,-.68,ey),(cx,-.68,h),(cx,end,h),(a,0,ey)]),('bay roof east',[(cx,-.68,h),(c,-.68,ey),(c,0,ey),(cx,end,h)])]
  out=out[1:]+[('main front '+str(i),[(x,y,E+(H-E)*y/r) for x,y in p])for i,p in enumerate(cuts(rect(0,0,w,r),hs))]
  # Low secondary roof between front range and hall is deliberately not invented.
  h=d['hall'];a,c,y,end=h['x0'],h['x1'],h['y0'],h['y1'];ry=h['ridge_y'];e=h['eaves'];top=h['ridge']
  # Hall roof: large hipped lantern with slate apron; transverse rear gable strip.
  a0,c0,y0,y1=a+2.6,c-2.6,y+3.5,ry-3.0;z=8.75
  out += [('hall apron front',[(a,y,e),(c,y,e),(c0,y0,z),(a0,y0,z)]),('hall apron east',[(c,y,e),(c,ry-2.0,e),(c0,y1,z),(c0,y0,z)]),('hall apron rear',[(c,ry-2,e),(a,ry-2,e),(a0,y1,z),(c0,y1,z)]),('hall apron west',[(a,ry-2,e),(a,y,e),(a0,y0,z),(a0,y1,z)]),('hall rear front',[(a,ry-2,e),(c,ry-2,e),(c,ry,top),(a,ry,top)]),('hall rear back',[(a,ry,top),(c,ry,top),(c,end,e),(a,end,e)])]
  mid=(a0+c0)/2
  out += [('lantern front',[(a0,y0,z),(c0,y0,z),(mid,y0+2.2,10.5)]),('lantern east',[(c0,y0,z),(c0,y1,z),(mid,y1-2.2,10.5),(mid,y0+2.2,10.5)]),('lantern back',[(c0,y1,z),(a0,y1,z),(mid,y1-2.2,10.5)]),('lantern west',[(a0,y1,z),(a0,y0,z),(mid,y0+2.2,10.5),(mid,y1-2.2,10.5)])]
 else:
  # Low glazed service covers evidenced in the rear court.
  out += [('low glass west',[(10.6,16.5,3.5),(15.8,16.5,3.5),(15.8,22.5,3.5),(10.6,22.5,3.5)])]
 if d['kind']=='red' and 'lightwell'in d:
  well=d['lightwell'];hole=rect(well['x0'],well['y0'],well['x1'],well['y1']);new=[]
  from mathutils import Vector
  for name,p in out:
   if not name.startswith('saltrock-gallery'):
    new.append((name,p));continue
   for ti,tri in enumerate([(p[0],p[i],p[i+1])for i in range(1,len(p)-1)]):
    a,b,c=map(Vector,tri);normal=(b-a).cross(c-a)
    for i,poly in enumerate(cuts([(v[0],v[1])for v in tri],[hole])):
     new.append((name+str(ti)+' '+str(i),[(x,y,a.z-(normal.x*(x-a.x)+normal.y*(y-a.y))/normal.z)for x,y in poly]))
  new.append(('low lightwell glass',[(x,y,well['floor'])for x,y in hole]));out=new
 return out

def exterior(d):
 w=d['front_width'];b=d['main_depth'];r=d['ridge_y'];E=d['front_eaves'];H=d['front_ridge'];B=d['rear_eaves'];lo=d['foundation_z']-d['floor_z'];out=[]
 out += [('southwest party',[(0,b,lo),(0,r,lo),(0,0,lo),(0,0,E),(0,r,H),(0,b,B)]),('northeast party',[(w,0,lo),(w,r,lo),(w,b,lo),(w,b,B),(w,r,H),(w,0,E)])]
 last=0
 for a,c in sorted([(v['x0'],v['x1'])for v in d['wings']])+[(w,w)]:
  if a>last:out.append(('rear front range',[(a,b,lo),(last,b,lo),(last,b,B),(a,b,B)]))
  last=c
 for v in d['wings']:
  a,c,end,e,h=v['x0'],v['x1'],v['end'],v['eaves'],v['ridge'];m=(a+c)/2
  out += [(v['id']+' west wall',[(a,end,lo),(a,b,lo),(a,b,B),(a,end,e)]),(v['id']+' east wall',[(c,b,lo),(c,end,lo),(c,end,e),(c,b,B)]),(v['id']+' rear gable',[(c,end,lo),(a,end,lo),(a,end,e),(m,end,h),(c,end,e)])]
 if d['kind']=='bank':
  h=d['hall'];a,c,y,end=h['x0'],h['x1'],h['y0'],h['y1'];ry=h['ridge_y'];e=h['eaves'];top=h['ridge']
  out += [('hall front',[(a,y,lo),(c,y,lo),(c,y,e),(a,y,e)]),('hall rear',[(c,end,lo),(a,end,lo),(a,end,e),(c,end,e)]),('hall west',[(a,end,lo),(a,y,lo),(a,y,e),(a,ry-2,e),(a,ry,top),(a,end,e)]),('hall east',[(c,y,lo),(c,end,lo),(c,end,e),(c,ry,top),(c,ry-2,e),(c,y,e)])]
 if d['kind']=='red' and 'lightwell'in d:
  q=d['lightwell']
  for name,poly in roofs(d):
   if not name.startswith('saltrock-gallery'):continue
   for i,(a,b)in enumerate(zip(poly,poly[1:]+poly[:1])):
    boundary=any(abs(a[k]-edge)<1e-6 and abs(b[k]-edge)<1e-6 for k,edge in [(0,q['x0']),(0,q['x1']),(1,q['y0']),(1,q['y1'])])
    if boundary:out.append(('lightwell inward '+name+str(i),[(a[0],a[1],q['floor']),(b[0],b[1],q['floor']),b,a]))
 return out

def bays(d):
 if d['kind']=='red':return [(d['bay_centres'][i],3.05,4.7,11.5,.56)for i in (0,3)]
 return [(d['bay_centres'][0],2.6,7.2,10.0,.65)]+[(x,3.2,4.55,7.1,.64)for x in d['bay_centres'][1:]]


def box_bays(d):
 for cx in d['bay_centres'][1:3]:
  a,b=cx-1.6,cx+1.6
  yield cx, [
   ('front',[(a,-.65,4.8),(b,-.65,4.8),(b,-.65,7.4),(a,-.65,7.4)]),
   ('skirt',[(a,-.43,4.4),(b,-.43,4.4),(b,-.65,4.8),(a,-.65,4.8)]),
   ('left',[(a,0,4.4),(a,-.43,4.4),(a,-.65,4.8),(a,-.65,7.4),(a,0,8.0)]),
   ('right',[(b,-.43,4.4),(b,0,4.4),(b,0,8.0),(b,-.65,7.4),(b,-.65,4.8)]),
   ('roof',[(a,-.65,7.4),(b,-.65,7.4),(b,0,8.0),(a,0,8.0)]),
   ('bottom',[(a,0,4.4),(b,0,4.4),(b,-.43,4.4),(a,-.43,4.4)])]
