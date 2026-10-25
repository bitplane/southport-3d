"""Authored metric envelopes and roof valleys, independent of decorative topology."""
import math
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cuts(p,holes):
 out=[p]
 for h in holes:out=[q for poly in out for q in subtract(poly,h)]
 return out

def transform(d,p):
 x,y,z=p
 return (d['front_origin'][0]+x+d['side_shear']*y,d['front_origin'][1]+y+d['front_shear']*x,d['floor_z']+z)

def main_roof_z(d,y):
 k=d['ridge_y']
 if y<=k:return d['front_eaves']+(d['front_ridge']-d['front_eaves'])*y/k
 return d['front_ridge']+(d['rear_eaves']-d['front_ridge'])*(y-k)/(d['main_depth']-k)

def roofs(d):
 w=d['front_width'];r=d['ridge_y'];b=d['main_depth'];E=d['front_eaves'];H=d['front_ridge'];B=d['rear_eaves']
 faces=[('front slate',[(0,0,E),(w,0,E),(w,r,H),(0,r,H)])]
 holes=[]
 for wing in d['wings']:
  a,c=wing['x0'],wing['x1'];m=(a+c)/2;h=wing['ridge'];y=r+(H-h)*(b-r)/(H-B)
  holes.append([(a,b),(m,y),(c,b)])
  end=wing['end']
  faces += [(wing['id']+' west slate',[(a,b,B),(m,y,h),(m,end,h),(a,end,B)]),(wing['id']+' east slate',[(m,y,h),(c,b,B),(c,end,B),(m,end,h)])]
 for i,p in enumerate(cuts(rect(0,r,w,b),holes)):
  faces.append(('back slope '+str(i),[(x,y,main_roof_z(d,y)) for x,y in p]))
 for ex in d['low_extensions']:
  faces.append((ex['id']+' extension membrane',[(ex['x0'],ex['y0'],ex['top']),(ex['x1'],ex['y0'],ex['top']),(ex['x1'],ex['y1'],ex['top']),(ex['x0'],ex['y1'],ex['top'])]))
 return faces

def exterior(d):
 """Exterior non-front walls, with no internal faces at wing/extension joins."""
 w=d['front_width'];b=d['main_depth'];E=d['front_eaves'];H=d['front_ridge'];B=d['rear_eaves'];r=d['ridge_y'];lo=d['foundation_z']-d['floor_z']
 faces=[('southwest party',[(0,0,lo),(0,r,lo),(0,b,lo),(0,b,B),(0,r,H),(0,0,E)]),('northeast party',[(w,b,lo),(w,r,lo),(w,0,lo),(w,0,E),(w,r,H),(w,b,B)])]
 intervals=sorted([(v['x0'],v['x1']) for v in d['wings']]);last=0
 for i,(a,c) in enumerate(intervals+[(w,w)]):
  if a>last:faces.append(('main rear court '+str(i),[(a,b,lo),(last,b,lo),(last,b,B),(a,b,B)]))
  last=c
 for v in d['wings']:
  a,c,end,h=v['x0'],v['x1'],v['end'],v['ridge'];m=(a+c)/2;ex=next((e for e in d['low_extensions'] if e['id']==v['id']),None);rearbase=ex['top'] if ex else lo
  faces.extend([(v['id']+' west return',[(a,b,lo),(a,end,lo),(a,end,B),(a,b,B)]),(v['id']+' east return',[(c,end,lo),(c,b,lo),(c,b,B),(c,end,B)]),(v['id']+' rear gable',[(c,end,rearbase),(a,end,rearbase),(a,end,B),(m,end,h),(c,end,B)])])
 for ex in d['low_extensions']:
  a,c,y,end,h=ex['x0'],ex['x1'],ex['y0'],ex['y1'],ex['top']
  faces.extend([(ex['id']+' low west',[(a,y,lo),(a,end,lo),(a,end,h),(a,y,h)]),(ex['id']+' low east',[(c,end,lo),(c,y,lo),(c,y,h),(c,end,h)]),(ex['id']+' low back',[(c,end,lo),(a,end,lo),(a,end,h),(c,end,h)])])
 return [(name,list(reversed(p)) if any(k in name for k in ('party','west return','east return','low west','low east')) else p) for name,p in faces]

def canopy_profile(d,n=12):
 c=d['canopy'];P=c['projection']
 # Segmental curved glass, high rear spring and lower street spring.
 return [(P*i/n,c['wall_z']+(c['spring_z']-c['wall_z'])*i/n+c['arch_rise']*math.sin(math.pi*i/n)) for i in range(n+1)]
