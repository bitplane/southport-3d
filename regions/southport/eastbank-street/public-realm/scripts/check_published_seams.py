"""Post-publication neighbour and internal seam checks for the elevation pilot."""
import json,sys,math
from pathlib import Path
import numpy as np
R=next(p for p in Path(__file__).resolve().parents if (p/'tools/check_lods.py').is_file());sys.path.insert(0,str(R/'tools'));from audit_published_coplanar import primitives
np.seterr(invalid='ignore')
cat=json.loads((R/'dist/catalog.json').read_text());rows=[]
ids=['southport.eastbank-street.public-realm','southport.station-quarter.public-realm','southport.lord-street.corridor-public-realm']
for level in ['detail','walk','district']:
 ts=[];labels=[]
 for asset in cat['assets']:
  if asset['id']not in ids:continue
  for part in asset['parts']:
   if not part.get('ground'):continue
   for t,src in primitives(R/'dist'/part['levels'][level]['uri'],{'position':[0,0,0],'rotationY':0}):
    t=t[:,:,[0,2,1]]*[1,-1,1];ts.append(t);labels +=[asset['id']+'/'+part['id']+'/'+src['node']]*len(t)
 t=np.concatenate(ts);a=t[:,0,:2];u=t[:,1,:2]-a;v=t[:,2,:2]-a;det=u[:,0]*v[:,1]-u[:,1]*v[:,0]
 def hit(x,y):
  q=np.array([x,y])-a
  with np.errstate(divide='ignore',invalid='ignore'):
   bu=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;bv=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det
  mask=(abs(det)>1e-10)&(bu>=-1e-8)&(bv>=-1e-8)&(bu+bv<=1+1e-8)
  z=t[:,0,2]+bu*(t[:,1,2]-t[:,0,2])+bv*(t[:,2,2]-t[:,0,2]);return[(float(z[i]),labels[i])for i in np.flatnonzero(mask)]
 def probe(name,p,q,step=0):
  h1,h2=hit(*p),hit(*q);assert h1 and h2,(name,p,q,h1,h2);z1=max(z for z,l in h1);z2=max(z for z,l in h2);assert abs(abs(z2-z1)-step)<.001,(name,h1,h2,step);rows.append({'level':level,'name':name,'heights':[z1,z2],'owners':[[l for z,l in h1],[l for z,l in h2]]})
 for x in [-261,-258,-255,-250]:probe('Lord north seam',(x,-35.005),(x,-34.995))
 for y in [-670,-580,-450,-300,-180]:
  d=json.loads((R/'regions/southport/eastbank-street/public-realm/research/layout.json').read_text());segments=[(a,b)for r in d['roads']if r['name']=='Eastbank Street'for a,b in zip(r['points'],r['points'][1:])if min(a[1],b[1])<y<max(a[1],b[1])];a0,b0=segments[0];x=a0[0]+(y-a0[1])/(b0[1]-a0[1])*(b0[0]-a0[0]);probe('internal road seam',(x,y-.005),(x,y+.005))
 y=-125;x=-257+(y+108)*3.8/29;probe('Chapel kerb',(x-.005,y),(x+.005,y),.12)
print('Passed',len(rows),'export seam probes');out=R/'build/eastbank-elevation-seams.json';out.write_text(json.dumps(rows,indent=2))
