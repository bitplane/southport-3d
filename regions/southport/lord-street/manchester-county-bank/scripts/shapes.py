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
 if d['kind']=='bank' and 'registered_footprint'in d['hall'] and y>=d['hall']['y0']-1e-6:
  h=d['hall'];u=(x-h['x0'])/(h['x1']-h['x0']);v=(y-h['y0'])/(h['y1']-h['y0']);a,b,c,e=h['registered_footprint'];X=(1-v)*((1-u)*a[0]+u*b[0])+v*((1-u)*e[0]+u*c[0]);Y=(1-v)*((1-u)*a[1]+u*b[1])+v*((1-u)*e[1]+u*c[1]);return(X,Y,d['floor_z']+z)
 return(d['front_origin'][0]+x+d['side_shear']*y,d['front_origin'][1]+y+d['front_shear']*x,d['floor_z']+z)

def canopy_profile(d,n=12):
 c=d['canopy'];P=c['projection']
 return [(P*i/n,c['wall_z']+(c['spring_z']-c['wall_z'])*i/n+c['arch_rise']*math.sin(math.pi*i/n)) for i in range(n+1)]

def bank_roof_height(d,y):
 E,H,B=d['front_eaves'],d['front_ridge'],d['rear_eaves'];r,b=d['ridge_y'],d['main_depth']
 by,bh=d['front_roof_break_y'],d['front_roof_break_height']
 if y<=by:return E+(bh-E)*y/by
 if y<=r:return bh+(H-bh)*(y-by)/(r-by)
 return H+(B-H)*(y-r)/(b-r)

def tower_upstand(d):
 t=d['tower'];w=t['width'];i=t['pediment_inset'];z=t['eaves'];s=t['pediment_shoulder'];p=t['pediment_peak']
 return [(i,z),(i,s),(w/2,p),(w-i,s),(w-i,z)]

def tower_oculus(d,n=20):
 t=d['tower'];x=t['width']/2;z=t['oculus_z'];r=t['oculus_radius']
 return [(x+r*math.cos(math.tau*i/n),z+r*math.sin(math.tau*i/n))for i in range(n)]

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
  # Steep front mansard, shallower upper slope and three dormer roofs. Split
  # each valley at the pitch change so neither roof is drawn under the other.
  t=d['tower'];tw,td,te,tt=[t[k]for k in ['width','depth','eaves','top']];inset=t['top_inset']
  by,bh=d['front_roof_break_y'],d['front_roof_break_height'];out=[];end=by+(10.95-bh)*(r-by)/(H-bh)
  for cx in d['bay_centres'][1:]:
   a,c=cx-1.65,cx+1.65;h=10.95;f=1.65*(bh-E)/(h-E)
   out += [('bay roof west',[(a,-.68,E),(cx,-.68,h),(cx,end,h),(a+f,by,bh),(a,0,E)]),
           ('bay roof east',[(cx,-.68,h),(c,-.68,E),(c,0,E),(c-f,by,bh),(cx,end,h)])]
  tower_cut=rect(0,0,tw+t['return_thickness'],td)
  for section,lo,hi in [('lower',0,by),('upper',by,r),('rear',r,b)]:
   holes=[tower_cut]
   if section=='rear':
    for v in d['front_rooflights']+d['front_roof_stacks']:
     holes.append(rect(v['x']-v['width']/2,v['y0'],v['x']+v['width']/2,v['y1']))
   if lo<end:
    q=min(hi,end);f0=1.65*(bank_roof_height(d,lo)-E)/(10.95-E);f1=1.65*(bank_roof_height(d,q)-E)/(10.95-E)
    for cx in d['bay_centres'][1:]:
     a,c=cx-1.65,cx+1.65
     holes.append([(a+f0,lo),(c-f0,lo),(cx,q)] if abs(q-end)<1e-7 else [(a+f0,lo),(c-f0,lo),(c-f1,q),(a+f1,q)])
   for i,p in enumerate(cuts(rect(0,lo,w,hi),holes)):
    out.append(('main '+section+' '+str(i),[(x,y,bank_roof_height(d,y))for x,y in p]))
  # Visible rear-slope rooflights are true clipped openings with recessed glass;
  # the low masonry stacks also meet the roof along their sloping foot lines.
  for i,v in enumerate(d['front_rooflights']):
   a,c=v['x']-v['width']/2,v['x']+v['width']/2;y0,y1=v['y0'],v['y1']
   ring=[(a,y0),(c,y0),(c,y1),(a,y1)]
   out.append(('rooflight glazing '+str(i),[(x,y,bank_roof_height(d,y)-.045)for x,y in ring]))
   for j,(p,q)in enumerate(zip(ring,ring[1:]+ring[:1])):
    out.append(('rooflight reveal '+str(i)+' '+str(j),[(p[0],p[1],bank_roof_height(d,p[1])),(q[0],q[1],bank_roof_height(d,q[1])),(q[0],q[1],bank_roof_height(d,q[1])-.045),(p[0],p[1],bank_roof_height(d,p[1])-.045)]))
  for i,v in enumerate(d['front_roof_stacks']):
   a,c=v['x']-v['width']/2,v['x']+v['width']/2;y0,y1,top=v['y0'],v['y1'],v['top'];ring=[(a,y0),(c,y0),(c,y1),(a,y1)]
   for j,(p,q)in enumerate(zip(ring,ring[1:]+ring[:1])):
    out.append(('front chimney '+str(i)+' side '+str(j),[(p[0],p[1],bank_roof_height(d,p[1])),(q[0],q[1],bank_roof_height(d,q[1])),(q[0],q[1],top),(p[0],p[1],top)]))
   out.append(('front chimney '+str(i)+' cap',[(x,y,top)for x,y in ring]))
  base=[(0,0,te),(tw,0,te),(tw,td,te),(0,td,te)]
  top=[(inset,inset,tt),(tw-inset,inset,tt),(tw-inset,td-inset,tt),(inset,td-inset,tt)]
  for i in range(4):out.append(('tower hip '+str(i),[base[i],base[(i+1)%4],top[(i+1)%4],top[i]]))
  ci=t['crown_inset'];cr=t['crown_rise'];upper=[(inset+ci,inset+ci,tt+cr),(tw-inset-ci,inset+ci,tt+cr),(tw-inset-ci,td-inset-ci,tt+cr),(inset+ci,td-inset-ci,tt+cr)]
  for i in range(4):out.append(('tower shallow crown '+str(i),[top[i],top[(i+1)%4],upper[(i+1)%4],upper[i]]))
  out.append(('tower crown top',upper))
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
 return out

def exterior(d,party_roof=None):
 w=d['front_width'];b=d['main_depth'];r=d['ridge_y'];E=d['front_eaves'];H=d['front_ridge'];B=d['rear_eaves'];lo=d['foundation_z']-d['floor_z'];out=[]
 if d['kind']=='bank':
  by,bh=d['front_roof_break_y'],d['front_roof_break_height']
  out += [('southwest party',[(0,b,lo),(0,r,lo),(0,0,lo),(0,0,E),(0,by,bh),(0,r,H),(0,b,B)]),('northeast party',[(w,0,lo),(w,r,lo),(w,b,lo),(w,b,B),(w,r,H),(w,by,bh),(w,0,E)])]
 else:
  out += [('southwest party',[(0,b,lo),(0,r,lo),(0,0,lo),(0,0,E),(0,r,H),(0,b,B)]),('northeast party',[(w,0,lo),(w,r,lo),(w,b,lo),(w,b,B),(w,r,H),(w,0,E)])]
 last=0
 for a,c in sorted([(v['x0'],v['x1'])for v in d['wings']])+[(w,w)]:
  if a>last:out.append(('rear front range',[(a,b,lo),(last,b,lo),(last,b,B),(a,b,B)]))
  last=c
 for v in d['wings']:
  a,c,end,e,h=v['x0'],v['x1'],v['end'],v['eaves'],v['ridge'];m=(a+c)/2
  out += [(v['id']+' west wall',[(a,end,lo),(a,b,lo),(a,b,B),(a,end,e)]),(v['id']+' east wall',[(c,b,lo),(c,end,lo),(c,end,e),(c,b,B)]),(v['id']+' rear gable',[(c,end,lo),(a,end,lo),(a,end,e),(m,end,h),(c,end,e)])]
 if d['kind']=='bank':
  t=d['tower'];tw,td,te=t['width'],t['depth'],t['eaves']
  rear=bank_roof_height(d,td);by=d['front_roof_break_y'];bh=d['front_roof_break_height'];th=t['return_thickness'];upper=t['return_profile']
  # The adjoining red range owns the common party skin. Only the narrow
  # tower wedge above its front roof is visible on this side. The neighbour
  # layout is a declared input so a profile change cannot silently overlap.
  if party_roof is None:raise ValueError('Bank party ownership needs the declared adjoining roof layout')
  p=party_roof;front=transform(p,(p['front_width'],0,0));here=transform(d,(0,0,0))
  assert max(abs(front[i]-here[i])for i in (0,1))<1e-4 and abs(p['side_shear']-d['side_shear'])<1e-8
  redbase=p['floor_z']+p['front_eaves']-d['floor_z'];slope=(p['front_ridge']-p['front_eaves'])/p['ridge_y']
  assert slope>0 and p['ridge_y']>=td and redbase>bank_roof_height(d,0) and redbase+slope*td>=te
  end=max(0,min(td,(te-redbase)/slope))
  if end>1e-6:out.append(('tower exposed left wedge',[(0,0,redbase),(0,0,te),(0,end,te)]))
  out += [('tower right sandstone return',[(tw+th,0,E),(tw+th,by,bh),(tw+th,r,H),(tw+th,td,rear)]+[(tw+th,y,z)for y,z in upper[::-1]]),
          ('tower inner parapet',[(tw,0,te),(tw,td,te)]+[(tw,y,z)for y,z in upper[::-1][:-1]]),
          ('tower rear return',[(0,td,rear),(tw,td,rear),(tw,td,te),(0,td,te)]),
          ('tower parapet front end',[(tw,0,E),(tw+th,0,E),(tw+th,0,te),(tw,0,te)]),
          ('tower parapet rear end',[(tw,td,rear),(tw+th,td,rear),(tw+th,td,upper[-1][1]),(tw,td,upper[-1][1])])]
  for i,((a,z),(c,q)) in enumerate(zip(upper,upper[1:])):
   # Projected sandstone coping owns the top; no coincident wall-top face.
   cap=th+t['return_coping_projection'];h=t['return_coping_height']
   out += [('tower parapet coping top '+str(i),[(tw,a,z+h),(tw+cap,a,z+h),(tw+cap,c,q+h),(tw,c,q+h)]),
           ('tower parapet coping outer '+str(i),[(tw+cap,a,z),(tw+cap,c,q),(tw+cap,c,q+h),(tw+cap,a,z+h)]),
           ('tower parapet coping inner '+str(i),[(tw,c,q),(tw,a,z),(tw,a,z+h),(tw,c,q+h)]),
           ('tower parapet coping underside '+str(i),[(tw+th,a,z),(tw+th,c,q),(tw+cap,c,q),(tw+cap,a,z)])]
  out += [('tower parapet coping front',[(tw,0,te),(tw+cap,0,te),(tw+cap,0,te+h),(tw,0,te+h)]),
          ('tower parapet coping rear',[(tw,td,upper[-1][1]),(tw,td,upper[-1][1]+h),(tw+cap,td,upper[-1][1]+h),(tw+cap,td,upper[-1][1])])]
  h=d['hall'];a,c,y,end=h['x0'],h['x1'],h['y0'],h['y1'];ry=h['ridge_y'];e=h['eaves'];top=h['ridge']
  out += [('hall front',[(a,y,lo),(c,y,lo),(c,y,e),(a,y,e)]),('hall rear',[(c,end,lo),(a,end,lo),(a,end,e),(c,end,e)]),('hall west',[(a,end,lo),(a,y,lo),(a,y,e),(a,ry-2,e),(a,ry,top),(a,end,e)]),('hall east',[(c,y,lo),(c,end,lo),(c,end,e),(c,ry,top),(c,ry-2,e),(c,y,e)])]
 return out

def bays(d):
 if d['kind']=='red':return [(d['bay_centres'][i],3.05,4.7,11.5,.56)for i in (0,3)]
 return [(d['bay_centres'][0],2.6,7.2,10.0,.65)]+[(x,3.2,4.55,7.1,.64)for x in d['bay_centres'][1:]]
