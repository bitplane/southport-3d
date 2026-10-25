"""Run after publication: ground continuity at existing and internal boundaries."""
import json,sys,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[5];sys.path.insert(0,str(R/'tools'));from audit_published_coplanar import primitives
cat=json.load(open(R/'dist/catalog.json'));c=math.cos(math.radians(43.5293));s=math.sin(math.radians(43.5293));rows=[];np.seterr(invalid='ignore')
D=json.load(open(R/'regions/southport/leicester-quarter/public-realm/research/layout.json'))
for level in ['detail','walk','district']:
 tris=[];labels=[]
 for asset in cat['assets']:
  if asset['id'] not in ['southport.leicester-quarter.public-realm','southport.stanley-street.public-realm','southport.lord-street.corridor-public-realm']:continue
  for part in asset['parts']:
   if not part.get('ground'):continue
   for tri,src in primitives(R/'dist'/part['levels'][level]['uri'],asset):tris.append(tri);labels += [asset['id']+'/'+part['id']+'/'+src['node']]*len(tri)
 t=np.concatenate(tris);a=t[:,0][:,[0,2]];u=t[:,1][:,[0,2]]-a;v=t[:,2][:,[0,2]]-a;det=u[:,0]*v[:,1]-u[:,1]*v[:,0];valid=abs(det)>1e-10
 def height(x,y):
  q=np.array([c*x-s*y,-(s*x+c*y)])-a
  with np.errstate(divide='ignore',invalid='ignore'):
   bu=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;bv=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det
  hit=valid&(bu>=-1e-8)&(bv>=-1e-8)&(bu+bv<=1+1e-8)
  assert hit.any(),(level,x,y,'no ground')
  z=t[:,0,1]+bu*(t[:,1,1]-t[:,0,1])+bv*(t[:,2,1]-t[:,0,1]);owners=sorted(set(labels[i] for i in np.flatnonzero(hit)));assert len(owners)==1,(level,x,y,'multiple ground owners',owners);return float(z[hit].max()),owners
 def probe(x,y,dx,dy):
  h=[height(x-dx,y-dy),height(x+dx,y+dy)];assert abs(h[0][0]-h[1][0])<.001,(level,x,y,h)
  rows.append({'level':level,'seam_xy':[x,y],'heights':[r[0] for r in h],'owners':[r[1] for r in h]})
 for boundary, road_id in [(65,'23158341'),(65,'23085717')]:
  r=next(r for r in D['roads']if r['id']==road_id)
  aa,bb=next((aa,bb)for aa,bb in zip(r['points'],r['points'][1:])if min(aa[1],bb[1])<boundary<max(aa[1],bb[1]))
  x=aa[0]+(boundary-aa[1])/(bb[1]-aa[1])*(bb[0]-aa[0])
  for dx in [0,-2.2,2.2,-r['width']/2-.6,r['width']/2+.6]:probe(x+dx,boundary,0,.005)
 for r in D['roads'][:2]:
  aa,bb=next((aa,bb)for aa,bb in zip(r['points'],r['points'][1:])if aa[0]<250<bb[0])
  y=aa[1]+(250-aa[0])/(bb[0]-aa[0])*(bb[1]-aa[1])
  for dy in [0,-2.0,2.0,-r['width']/2-.6,r['width']/2+.6]:probe(250,y+dy,.005,0)
 for x in D['tile_cuts'][1:-1]:
  for y in [97.0,164.3]:probe(x,y,.005,0)
print('Published GLB seam probes passed:',len(rows))
(R.parent/'output/mapping-sol-trial').mkdir(parents=True,exist_ok=True)
(R.parent/'output/mapping-sol-trial/first-seam-probes.json').write_text(json.dumps({'revision':cat['revision'],'probes':rows},indent=2)+'\n')
