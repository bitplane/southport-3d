"""Run after publication: ground continuity at existing and internal boundaries."""
import json,sys,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[5];sys.path.insert(0,str(R/'tools'));from audit_published_coplanar import primitives
cat=json.load(open(R/'dist/catalog.json'));c=math.cos(math.radians(43.5293));s=math.sin(math.radians(43.5293));rows=[];np.seterr(invalid='ignore')
D=json.load(open(R/'regions/southport/lord-street/christ-church-approach/research/layout.json'))
for level in ['detail','walk','district']:
 tris=[];labels=[]
 for asset in cat['assets']:
  if asset['id'] not in ['southport.lord-street.christ-church-approach','southport.lord-street.church-gardens','southport.station-quarter.public-realm']:continue
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
 # New/old garden north and west/east ownership boundaries.
 for x in [-127.3,-125,-121,-118]:probe(x,-18.0,0,.005)
 for y in [-20,-25,-28]:
  probe(-127.9,y,.005,0);probe(-117.4,y,.005,0)
 for x in [-130.4,-129.2,-116.5]:probe(x,-29.72,0,.005)
 # Station already owns the southern Corporation mouth fromY=-105.
 for x in [-130,-128,-125]:probe(x,-105,0,.005)
 # Internal ground split remains continuous through pedestrian and court routes.
 for x in [-130.4,-128,-125]:probe(x,-70,0,.005)
print('Published GLB seam probes passed:',len(rows))
(R.parent/'output/mapping-sol-trial').mkdir(parents=True,exist_ok=True)
(R.parent/'output/mapping-sol-trial/second-seam-probes.json').write_text(json.dumps({'revision':cat['revision'],'probes':rows},indent=2)+'\n')
