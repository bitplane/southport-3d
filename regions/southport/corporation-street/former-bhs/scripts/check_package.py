"""Actual exports, court clearance, budgets and neighbouring coplanarity."""
import argparse,json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args();repo=args.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools')]
from publication import inspect_glb
from audit_published_coplanar import primitives
from coplanar import overlaps
A=json.loads((args.package/'assembly.json').read_text());D=json.loads((args.recipe.parent/'research/layout.json').read_text());cat=json.loads((repo/'dist/catalog.json').read_text());identity={'rotationY':0,'position':[0,0,0]};yaw=math.radians(43.5293);world={'rotationY':yaw,'position':[0,0,0]}
X,Y,Z=D['origin'];W,L,F,AA=D['width'],D['length'],D['front_depth'],D['arcade_wing_width'];B=W-D['corp_range_width']
def point(u,v):
 t=v/L;q=u/W
 return (X+u+t*(2.189*(1-q)+.498*q),Y+v+(1-t)*2.862*(1-q)+t*(-.016+.694*q))
def open_sky(ts,x,y):
 # glTF coordinates are x=east, y=height, z=-north in the site's unrotated frame.
 q=np.array([x,-y]);p=ts[:,:,[0,2]];a,b,c=p[:,0],p[:,1],p[:,2]
 def cross(v,w):return v[:,0]*w[:,1]-v[:,1]*w[:,0]
 den=cross(b-a,c-a);valid=np.abs(den)>1e-10;u=np.zeros(len(ts));v=u.copy();u[valid]=cross(q-a,c-a)[valid]/den[valid];v[valid]=cross(b-a,q-a)[valid]/den[valid]
 return not np.any(valid&(u>1e-6)&(v>1e-6)&(u+v<1-1e-6)&(ts[:,:,1].max(1)>Z+.2))
def roof_rear_hit(ts,u,z):
 # Segment crosses the actual court-facing wall in the unrotated glTF frame.
 def gltf(v):
  x,y=point(u,v);return np.array([x,Z+z,-y])
 origin,end=gltf(F+2),gltf(F-2);direction=end-origin
 a,b,c=ts[:,0],ts[:,1],ts[:,2];e1=b-a;e2=c-a
 p=np.cross(np.broadcast_to(direction,e2.shape),e2);den=np.einsum('ij,ij->i',e1,p)
 valid=np.abs(den)>1e-10;inv=np.zeros_like(den);inv[valid]=1/den[valid]
 delta=origin-a;uu=np.einsum('ij,ij->i',delta,p)*inv;q=np.cross(delta,e1)
 vv=np.einsum('j,ij->i',direction,q)*inv;t=np.einsum('ij,ij->i',e2,q)*inv
 return np.any(valid&(uu>=-1e-7)&(vv>=-1e-7)&(uu+vv<=1+1e-7)&(np.abs(t-.5)<.01))
rows=[]
for level in ['detail','walk','district']:
 files=[args.package/f['path'] for f in A['files'] if f['level']==level];infos=[inspect_glb(f) for f in files];tri=sum(i['triangles']for i in infos);download=sum(i['bytes']for i in infos);gpu=sum(i['gpuBytesEstimate']for i in infos)
 assert tri<={'detail':140000,'walk':120000,'district':1200}[level],(level,tri)
 if level=='district':assert download<=3000000 and gpu<=11000000,(download,gpu)
 if level=='district':
  # A unit-length but inverted tangent map previously made the arcade wall
  # look black despite full bake coverage; sample this specific receiver.
  rear=A['envelope']['parts']['rear'];idx=rear['faces'].index('Chapel arcade return')
  x,y,w,h=rear['rectangles'][str(idx)];atlas=np.asarray(Image.open(args.package/'maps/district/rear/normal.png').convert('RGB'))
  patch=atlas[atlas.shape[0]-y-h+1:atlas.shape[0]-y-1,x+1:x+w-1]
  assert patch.size and np.mean(patch[:,:,2]>200)>.65,('arcade inverted normal map',float(np.mean(patch[:,:,2]>200)))
 groups=[(t,o) for f in files for t,o in primitives(f,identity)];ts=np.concatenate([t for t,o in groups]);labels=[o['node'] for t,o in groups for _ in t];own_hits=overlaps(ts,labels);assert not [r for r in own_hits if r[2]>1e-5],(level,own_hits[:20])
 for u,v in [((AA+B)/2,F+8),((AA+B)/2,L-4)]:assert open_sky(ts,*point(u,v)),(level,'court filled',u,v)
 for u,z in [(20.6,14.8),(22.8,16.2),(25.0,15.5)]:assert roof_rear_hit(ts,u,z),(level,'court-side roof opening',u,z)
 geo=[(t,o)for f in files for t,o in primitives(f,world)];own=np.concatenate([t for t,o in geo]);lo=own.min((0,1))-.1;hi=own.max((0,1))+.1;near=[];neighbours=[]
 for asset in cat['assets']:
  if asset['id']=='southport.corporation-street.former-bhs':continue
  a=asset['rotationY'];R=np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
  for part in asset['parts']:
   if asset['id']=='southport.station-quarter.frontage-placeholders' and part['id'] in ('hugo-frontage','hugo-rear-range'):continue
   bounds=np.array(part['bounds']);corners=np.array([[x,y,z]for x in bounds[:,0] for y in bounds[:,1] for z in bounds[:,2]])@R.T+asset['position']
   if not(np.all(corners.max(0)>=lo) and np.all(corners.min(0)<=hi)):continue
   touched=False
   for t,o in primitives(repo/'dist'/part['levels'][part.get('fixedLevel',level)]['uri'],asset):
    mask=np.all(t.max(1)>=lo,axis=1)&np.all(t.min(1)<=hi,axis=1)
    if mask.any():near.append((t[mask],asset['id']+'/'+part['id']+'/'+o['node']));touched=True
   if touched:neighbours.append(asset['id']+'/'+part['id'])
 merged=np.concatenate([own]+[t for t,n in near]);names=['building']*len(own)+[n for t,n in near for _ in t];hits=overlaps(merged,names);cross=[r for r in hits if (r[0]=='building')!=(r[1]=='building')];assert not [r for r in cross if r[2]>1e-5],(level,cross[:20])
 rows.append({'level':level,'triangles':tri,'download_bytes':download,'gpu_bytes':gpu,'court_sky_probes':2,'neighbours':neighbours,'cross_asset_overlaps':cross,'limits':'Same-facing coplanarity is not a general intersection or visual test; exact geometry and transition require viewer inspection.'})
(args.package/'former-bhs-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print('Former BHS exported checks:',rows)
