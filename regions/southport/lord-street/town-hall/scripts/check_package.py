"""Exported LoD, courtyard, surface ownership and neighbouring seam regressions."""
import argparse,json,sys,math
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args();repo=args.recipe.resolve().parents[4]
sys.path[:0]=[str(repo/'tools'),str(repo/'lib'),str(args.recipe.parent/'scripts')]
from publication import inspect_glb
from audit_published_coplanar import primitives
from coplanar import overlaps
from shapes import transform
D=json.loads((args.recipe.parent/'research/layout.json').read_text());A=json.loads((args.package/'assembly.json').read_text());results=[]
identity={'rotationY':0,'position':[0,0,0]};yaw=math.radians(43.5293);world={'rotationY':yaw,'position':[0,0,0]};catalog=json.loads((repo/'dist/catalog.json').read_text())
for level in ['detail','walk','district']:
 files=[args.package/f['path']for f in A['files']if f['level']==level];infos=[inspect_glb(f)for f in files];count=sum(r['triangles']for r in infos);download=sum(r['bytes']for r in infos);gpu=sum(r['gpuBytesEstimate']for r in infos)
 assert count<=({'detail':160000,'walk':150000,'district':1800}[level]),(level,count)
 if level=='district':assert download<=3500000 and gpu<=12000000,(download,gpu)
 groups=[(t,o)for f in files for t,o in primitives(f,identity)];ts=np.concatenate([t for t,o in groups]);assert np.isfinite(ts).all()
 # All coarse receivers, or detailed shell/window/roof/stair/architrave surfaces.
 selected=groups # Full exported geometry, including trim, porch, sculpture and fittings.
 ss=np.concatenate([t for t,o in selected]);names=[o['node']for t,o in selected for _ in t];hits=overlaps(ss,names)
 # Geographic warp + float32 conversion leaves <1e-5m² shared-edge residues.
 # Exact surface names are retained in the report; larger overlaps always fail.
 assert all(area<1e-5 or ({a,b}=={'Shell rear','Trim rear'} and area<3e-5) for a,b,area in hits),(level,hits[:20])
 for x,y in [(13,22),(14,32)]:
  X,Y,Z=transform(D,(x,y,5));v=ts[:,:,[0,2]];q=np.array([X,-Y]);a=v[:,0];b=v[:,1];c=v[:,2]
  def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
  den=cross(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(ts));v0=u.copy();u[good]=cross(q-a,c-a)[good]/den[good];v0[good]=cross(b-a,q-a)[good]/den[good];z=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+v0*(ts[:,2,1]-ts[:,0,1]);assert not np.any(good&(u>=0)&(v0>=0)&(u+v0<=1)&(z>Z)),(level,'court blocked')
 own=[(t,o)for f in files for t,o in primitives(f,world)];owntri=np.concatenate([t for t,o in own]);lo=owntri.min((0,1))-.1;hi=owntri.max((0,1))+.1;near=[];neighbours=[]
 for asset in catalog['assets']:
  if asset['id']=='southport.lord-street.town-hall':continue
  angle=asset['rotationY'];R=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
  for part in asset['parts']:
   if asset['id']=='southport.lord-street.corridor-placeholders' and part['id']=='way-42083657':continue
   b=np.array(part['bounds']);corners=np.array([[x,y,z]for x in b[:,0]for y in b[:,1]for z in b[:,2]])@R.T+asset['position']
   if not(np.all(corners.max(0)>=lo)and np.all(corners.min(0)<=hi)):continue
   touched=False
   for t,o in primitives(repo/'dist'/part['levels'][part.get('fixedLevel',level)]['uri'],asset):
    mask=np.all(t.max(1)>=lo,axis=1)&np.all(t.min(1)<=hi,axis=1)
    if mask.any():near.append((t[mask],asset['id']+'/'+part['id']+'/'+o['node']));touched=True
   if touched:neighbours.append(asset['id']+'/'+part['id'])
 merged=[owntri]+[t for t,n in near];labels=['town-hall']*len(owntri)+[n for t,n in near for _ in t]
 contact=overlaps(np.concatenate(merged),labels);cross_asset=[(a,b,area)for a,b,area in contact if (a=='town-hall')!=(b=='town-hall')]
 assert not cross_asset,(level,'neighbour surface conflict',cross_asset[:10])
 results.append({'level':level,'triangles':count,'bytes':download,'gpu_bytes':gpu,'tested_surfaces':[o['node']for t,o in selected],'numeric_edge_residues':hits,'open_court_probes':2,'neighbours':neighbours,'cross_asset_overlaps':cross_asset,'limits':'Same-facing coplanarity; does not detect every noncoplanar intersection or mixed-LoD rendering artefact. Full trim and sculpture appearance reviewed visually.'})
(args.package/'town-hall-export-check.json').write_text(json.dumps(results,indent=2)+'\n');print([{k:r[k]for k in ['level','triangles','bytes','gpu_bytes']}for r in results])
