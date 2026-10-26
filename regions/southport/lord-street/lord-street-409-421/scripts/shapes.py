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
 if d.get('cafe'):out=cafe_roofs(d,out)
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
 if d.get('cafe'):out=cafe_exterior(d,out)
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


def facade_x(d,x):
 c=d.get('cafe',{}).get('width',0)
 return c+x*(d['front_width']-c)/d['front_width']

def cafe_roofs(d,out):
 c=d['cafe'];w=c['width'];b=d['main_depth'];r=d['ridge_y'];E=d['front_eaves'];H=d['front_ridge'];B=d['rear_eaves']
 end=(c['gable_top']-E)*r/(H-E)
 updated=[]
 for name,p in out:
  if name=='main front':
   for i,q in enumerate(cuts(rect(0,0,d['front_width'],r),[[(0,0),(w,0),(w/2,end)]])):
    updated.append(('main front '+str(i),[(x,y,E+(H-E)*y/r)for x,y in q]))
  elif name.startswith('main rear'):
   join=r+(H-c['strip_ridge'])*(b-r)/(H-B)
   for i,q in enumerate(cuts([(x,y)for x,y,z in p],[[(0,b),(c['rear_strip_width']/2,join),(c['rear_strip_width'],b)]])):
    updated.append((name+' cafe join '+str(i),[(x,y,H+(B-H)*(y-r)/(b-r))for x,y in q]))
  else:updated.append((name,p))
 updated += [('cafe front gable left',[(0,0,E),(w/2,0,c['gable_top']),(w/2,end,c['gable_top'])]),('cafe front gable right',[(w/2,0,c['gable_top']),(w,0,E),(w/2,end,c['gable_top'])])]
 a=c['rear_strip_width'];ys=c['rear_arm_start'];ye=c['rear_arm_end'];aw=c['rear_arm_width'];e=c['rear_eaves'];sr=c['strip_ridge'];ar=c['arm_ridge'];ym=(ys+ye)/2
 join=r+(H-sr)*(b-r)/(H-B);vj=ys+(sr-e)*(ym-ys)/(ar-e)
 updated += [('cafe strip west',[(0,b,B),(a/2,join,sr),(a/2,vj,sr),(0,ys,e)]),('cafe strip east',[(a/2,join,sr),(a,b,B),(a,ys,e),(a/2,vj,sr)])]
 for i,q in enumerate(cuts(rect(0,ys,aw,ym),[[(0,ys),(a,ys),(a/2,vj)]])):
  updated.append(('cafe rear arm front '+str(i),[(x,y,e+(ar-e)*(y-ys)/(ym-ys))for x,y in q]))
 updated += [('cafe rear arm back',[(0,ym,ar),(aw,ym,ar),(aw,ye,e),(0,ye,e)]),('cafe court low glass',[(a,b,3.5),(10.3,b,3.5),(10.3,ys,3.5),(a,ys,3.5)])]
 return updated

def cafe_exterior(d,out):
 c=d['cafe'];a=c['rear_strip_width'];b=d['main_depth'];B=d['rear_eaves'];ys=c['rear_arm_start'];ye=c['rear_arm_end'];aw=c['rear_arm_width'];e=c['rear_eaves'];ar=c['arm_ridge'];lo=d['foundation_z']-d['floor_z'];new=[]
 for name,p in out:
  if name=='rear front range':
   # The narrow cafe wing shares the main-range wall at y=b.
   for q in cuts([(x,z)for x,y,z in p],[rect(0,lo,a,B)]):new.append((name,[(x,b,z)for x,z in q]))
  else:new.append((name,p))
 new += [('cafe strip west wall',[(0,ys,lo),(0,b,lo),(0,b,B),(0,ys,e)]),('cafe strip east wall',[(a,b,lo),(a,ys,lo),(a,ys,e),(a,b,B)]),('cafe rear arm front wall',[(a,ys,lo),(aw,ys,lo),(aw,ys,e),(a,ys,e)]),('cafe rear arm back wall',[(aw,ye,lo),(0,ye,lo),(0,ye,e),(aw,ye,e)]),('cafe rear arm west gable',[(0,ye,lo),(0,ys,lo),(0,ys,e),(0,(ys+ye)/2,ar),(0,ye,e)]),('cafe rear arm east gable',[(aw,ys,lo),(aw,ye,lo),(aw,ye,e),(aw,(ys+ye)/2,ar),(aw,ys,e)])]
 return new

def cafe_front_envelope(d):
 c=d['cafe'];w=c['width'];a=(w-c['bay_width'])/2;b=w-a;p=c['projection'];lo=4.45;hi=11.65
 out=[]
 for poly in cuts(rect(0,0,w,d['front_eaves']),[rect(a,lo,b,hi)]):out.append(('wall',[(x,0,z)for x,z in poly]))
 out += [('bay front',[(a,-p,lo),(b,-p,lo),(b,-p,hi),(a,-p,hi)]),('bay left',[(a,0,lo),(a,-p,lo),(a,-p,hi),(a,0,hi)]),('bay right',[(b,-p,lo),(b,0,lo),(b,0,hi),(b,-p,hi)]),('bay top',[(a,-p,hi),(b,-p,hi),(b,0,hi),(a,0,hi)]),('bay bottom',[(a,0,lo),(b,0,lo),(b,-p,lo),(a,-p,lo)]),('gable',[(0,0,d['front_eaves']),(w,0,d['front_eaves']),(w/2,0,c['gable_top'])])]
 return out
