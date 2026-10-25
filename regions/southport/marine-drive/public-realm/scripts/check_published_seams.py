"""Actual exported three-level ownership, profile, budget and neighbour handovers."""
import json,sys,math,subprocess
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[5];sys.path[:0]=[str(R/'tools'),str(R/'lib')]
from audit_published_coplanar import primitives,audit_level
from southport3d.elevation import Elevations
E=Elevations(R/'regions/southport/elevation/marine-drive.json');D=json.load(open(R/'regions/southport/marine-drive/public-realm/research/layout.json'));cat=json.load(open(R/'dist/catalog.json'));c=math.cos(math.radians(43.5293));s=math.sin(math.radians(43.5293));out=R.parent/'output/marine-drive';out.mkdir(parents=True,exist_ok=True)
ids=['southport.marine-drive.public-realm','southport.marine-drive.frontage-placeholders','southport.promenade.marine-parade-junction','southport.leicester-quarter.public-realm','southport.leicester-quarter.frontage-placeholders','southport.nevill-street.public-realm','southport.nevill-street.frontage-placeholders','southport.stanley-street.public-realm']
selected=dict(cat,assets=[a for a in cat['assets']if a['id']in ids]);exe=out/'coplanar-scan';subprocess.run(['g++','-O3','-std=c++17',str(R/'tools/coplanar_scan.cpp'),'-o',str(exe)],check=True)
np.seterr(invalid="ignore")
rows=[];levels={};baseline={}
for level in ['detail','walk','district']:
 tris=[];labels=[];total_bytes=0;total_triangles=0
 for asset in selected['assets']:
  for part in asset['parts']:
   own=asset['id'].startswith('southport.marine-drive.')
   values=[]
   for tri,src in primitives(R/'dist'/part['levels'][level]['uri'],asset):
    if own:total_triangles+=len(tri)
    values.append(tri)
    if part.get('ground'):tris.append(tri);labels.extend([asset['id']+'/'+part['id']+'/'+src['node']]*len(tri))
   if own:
    total_bytes+=(R/'dist'/part['levels'][level]['uri']).stat().st_size
    v=np.concatenate(values)
    if level=='detail':baseline[(asset['id'],part['id'])]=v
    else:assert np.array_equal(v,baseline[(asset['id'],part['id'])]),(level,asset['id'],part['id'],'geometry changed across levels')
 t=np.concatenate(tris);a=t[:,0][:,[0,2]];u=t[:,1][:,[0,2]]-a;v=t[:,2][:,[0,2]]-a;det=u[:,0]*v[:,1]-u[:,1]*v[:,0];valid=abs(det)>1e-10
 def height(x,y):
  q=np.array([c*x-s*y,-(s*x+c*y)])-a
  with np.errstate(divide='ignore',invalid='ignore'):
   bu=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;bv=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det
  hit=valid&(bu>=-1e-8)&(bv>=-1e-8)&(bu+bv<=1+1e-8)
  assert hit.any(),(level,x,y,'no ground')
  z=t[:,0,1]+bu*(t[:,1,1]-t[:,0,1])+bv*(t[:,2,1]-t[:,0,1]);owners=sorted(set(labels[i]for i in np.flatnonzero(hit)));assert len(owners)==1,(level,x,y,'multiple owners',owners);return float(z[hit].max()),owners
 def probe(x,y,dx,dy):
  h=[height(x-dx,y-dy),height(x+dx,y+dy)];assert abs(h[0][0]-h[1][0])<.001,(level,x,y,h);rows.append({'level':level,'xy':[x,y],'heights':[r[0]for r in h],'owners':[r[1]for r in h]})
 for y in [287,292,296,298,301,304,309,313]:probe(85,y,.01,0)
 for x in [22.25,24,28,30.5,33,37,39]:probe(x,310,0,.01)
 probe(146.82,175,0,.01)
 # Street axes where the existing Leicester ownership boundary crossesY230.
 seen=[]
 for r in D['roads']:
  for aa,bb in zip(r['points'],r['points'][1:]):
   if min(aa[1],bb[1])<230<max(aa[1],bb[1]):
    x=aa[0]+(230-aa[1])/(bb[1]-aa[1])*(bb[0]-aa[0])
    if 86<x<609 and all(abs(x-p)>1 for p in seen):probe(x,230,0,.01);seen.append(x)
 for x in D['tile_cuts'][2:-1]:
  for aa,bb in zip(D['coast_wall_axis'],D['coast_wall_axis'][1:]):
   if aa[0]<x<bb[0]:
    y=aa[1]+(x-aa[0])/(bb[0]-aa[0])*(bb[1]-aa[1]);probe(x,y,.01,0);probe(x,y+5.2,.01,0);break
 assert total_triangles<105000,(level,total_triangles)
 assert total_bytes<14000000,(level,total_bytes)
 levels[level]={'triangles':total_triangles,'bytes':total_bytes}
 # Retain every exported overlap candidate, including older neighbour defects.
 audit_level(selected,R/'dist',level,exe,out)
(out/'seam-probes.json').write_text(json.dumps({'revision':cat['revision'],'probes':rows,'levels':levels,'same_geometry_all_levels':True},indent=2)+'\n');print('Published seam probes passed',len(rows),levels)
