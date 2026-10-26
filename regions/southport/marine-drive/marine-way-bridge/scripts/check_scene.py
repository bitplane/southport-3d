"""Actual exported bridge/ground integration at all levels, including layered support."""
import json,math,sys,subprocess
from pathlib import Path
import numpy as np
np.seterr(invalid="ignore")
REPO=Path(__file__).resolve().parents[5];sys.path.insert(0,str(REPO/'tools'));sys.path.insert(0,str(REPO/'lib'))
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations
D=json.load(open(Path(__file__).resolve().parents[1]/'research/layout.json'));E=Elevations(REPO/'regions/southport/elevation/marine-drive.json');grade=E.surface('marine-bridge-measured-reference');cat=json.load(open(REPO/'dist/catalog.json'));ground=E.surface('marine-mainland');out=REPO.parent/'output/marine-way-bridge';out.mkdir(exist_ok=True,parents=True)
u=np.array(D['axis']);u/=np.linalg.norm(u);n=np.array([-u[1],u[0]]);c=math.cos(math.radians(43.5293));s=math.sin(math.radians(43.5293))
if '--packages' in sys.argv:
 package=REPO/'build/southport.marine-drive.public-realm/package'
 manifest=json.loads((package/'manifest.json').read_text())
 recipe=json.loads((REPO/'regions/southport/marine-drive/public-realm/publication.json').read_text())
 parts=[]
 for part in recipe['parts']:
  parts.append(dict(part,levels={item['level']:{'uri':str(package/item['path'])}for item in manifest['files']if item['part']==part['id']}))
 cat={'revision':'isolated-'+manifest['build_signature'],'assets':[{'id':'southport.marine-drive.public-realm','rotationY':0,'position':[0,0,0],'parts':parts}]};c=1.;s=0.
def xy(st,t):return np.array(D['origin'])+u*st+n*t
def world(p):x,y=p;return np.array([c*x-s*y,-s*x-c*y])
rows=[]
for level in ['detail','walk','district']:
 ts=[];labels=[]
 for asset in cat['assets']:
  if asset['id']!='southport.marine-drive.public-realm':continue
  assert not any(p['id']=='bridge-structure'for p in asset['parts']),'provisional structure still published'
  for part in asset['parts']:
   if not part.get('ground'):continue
   for tri,owner in primitives(REPO/'dist'/part['levels'][level]['uri'],asset):ts.append(tri);labels.extend([part['id']]*len(tri))
 ts=np.concatenate(ts);a=ts[:,0][:,[0,2]];b=ts[:,1][:,[0,2]]-a;v=ts[:,2][:,[0,2]]-a;den=b[:,0]*v[:,1]-b[:,1]*v[:,0];good=abs(den)>1e-10
 def hits(st,t):
  p=xy(st,t);q=world(p)-a
  with np.errstate(divide='ignore',invalid='ignore'):
   bu=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/den;bv=(b[:,0]*q[:,1]-b[:,1]*q[:,0])/den
  mask=good&(bu>=-1e-7)&(bv>=-1e-7)&(bu+bv<=1+1e-7);z=ts[:,0,1]+bu*(ts[:,1,1]-ts[:,0,1])+bv*(ts[:,2,1]-ts[:,0,1]);return sorted(set((labels[i],round(float(z[i]),5))for i in np.flatnonzero(mask)))
 # Upper road, cycle strip, pedestrian path: identical named profiles in exports.
 for st in [2.3,17.3,35.3,60.3,85.3,110.3,135.3,148.3]:
  for t in [0.17,-3.8,3.8,-6.2,6.2]:
   h=hits(st,t);p=xy(st,t);expected=grade.height(*p)-(.12 if abs(t)<3.2 else 0);upper=[z for _,z in h if abs(z-expected)<.001];assert upper,(level,st,t,h,expected);rows.append({'level':level,'station':st,'transverse':t,'hits':h,'expected_upper':expected})
 # Eastern lower promenade is intentionally a second support plane below deck.
 lower=[]
 for st in [4.3,8.3,12.3,16.3]:
  h=hits(st,.17)
  if any(owner=='lower-promenade-ground'for owner,z in h):
   expected=ground.height(*xy(st,.17));assert any(abs(z-expected)<.001 for owner,z in h),(level,h,expected);assert max(z for _,z in h)-expected>2.8,(level,h,'insufficient layered clearance');lower.append(st)
 assert lower,(level,'no layered lower support')
 # Crossing the rail boundary below the deck must retain the mainland level.
 seams=[]
 for st in lower:
  for side in [-1,1]:
   inner=hits(st,side*7.99);outer=hits(st,side*8.01)
   if any(abs(z-ground.height(*xy(st,side*7.99)))<.001 for _,z in inner)and any(abs(z-ground.height(*xy(st,side*8.01)))<.001 for _,z in outer):seams.append([st,side])
 assert seams,(level,'no lower promenade lateral seam')
 rows.append({'level':level,'layered_stations':lower,'lower_seams':seams})
(out/'support-check.json').write_text(json.dumps({'catalog':cat['revision'],'checks':rows},indent=2)+'\n');print('Bridge upper/lower support and float32 ground checks passed:',len(rows))
