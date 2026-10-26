"""Actual threelevel exports, complete selected-neighbour scan and handovers."""
import sys,json,math,subprocess
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[5];sys.path[:0]=[str(R/'tools'),str(R/'lib')]
from audit_published_coplanar import primitives,audit_level
from southport3d.elevation import Elevations
cat=json.load(open(R/'dist/catalog.json'));own={'southport.marine-lake-south.public-realm','southport.marine-lake-south.frontage-placeholders'}
ids=own|{'southport.marine-drive.public-realm','southport.marine-drive.frontage-placeholders','southport.marine-drive.marine-way-bridge','southport.promenade.marine-parade-junction','southport.west-street.public-realm','southport.west-street.frontage-placeholders','southport.nevill-street.public-realm','southport.nevill-street.frontage-placeholders','southport.stanley-street.public-realm','southport.lord-street.corridor-public-realm','southport.lord-street.corridor-placeholders'}
selected=dict(cat,assets=[a for a in cat['assets']if a['id']in ids]);out=R.parent/'output/lake-south';out.mkdir(exist_ok=True);exe=out/'coplanar-scan';subprocess.run(['g++','-O3','-std=c++17',str(R/'tools/coplanar_scan.cpp'),'-o',str(exe)],check=True)
assert own.issubset({a['id']for a in selected['assets']})
c,s=math.cos(math.radians(43.5293)),math.sin(math.radians(43.5293));baseline={};summaries={};probes=[]
for level in ['detail','walk','district']:
 tris=[];labels=[];metrics={'triangles':0,'bytes':0,'gpu_bytes':0,'parts':0}
 for asset in selected['assets']:
  for part in asset['parts']:
   values=[]
   for tri,meta in primitives(R/'dist'/part['levels'][level]['uri'],asset):
    values.append(tri)
    if part.get('ground'):
     tris.append(tri);labels.extend([(asset['id'],part['id'],meta['node'])]*len(tri))
   if asset['id']in own:
    values=np.concatenate(values)
    if part.get('ground'):
     if level=='detail':baseline[(asset['id'],part['id'])]=values
     else:assert np.array_equal(values,baseline[(asset['id'],part['id'])]),(level,asset['id'],part['id'],'different ground geometry')
    data=part['levels'][level];metrics['triangles']+=data['triangles'];metrics['bytes']+=data['bytes'];metrics['gpu_bytes']+=data['gpuBytesEstimate'];metrics['parts']+=1
 t=np.concatenate(tris);xy=np.stack([t[:,:,0]*c-t[:,:,2]*s,-t[:,:,0]*s-t[:,:,2]*c],axis=2);u=xy[:,1]-xy[:,0];v=xy[:,2]-xy[:,0];det=u[:,0]*v[:,1]-u[:,1]*v[:,0];valid=abs(det)>1e-8
 def height(x,y):
  q=np.array([x,y])-xy[:,0]
  with np.errstate(invalid='ignore',divide='ignore'):
   U=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;V=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det
  hit=valid&(U>=-1e-7)&(V>=-1e-7)&(U+V<=1+1e-7)
  if not hit.any():return None
  z=t[:,0,1]+U*(t[:,1,1]-t[:,0,1])+V*(t[:,2,1]-t[:,0,1]);high=float(z[hit].max());owners=sorted(set(labels[i]for i in np.flatnonzero(hit& (abs(z-high)<1e-4))))
  return high,owners
 def probe(x,y,dx,dy,strict=True):
  h=[height(x-dx,y-dy),height(x+dx,y+dy)]
  if None in h:return
  owners=[set(a[0]for a in r[1])for r in h]
  if not(any(o&own for o in owners)and any(o-own for o in owners)):return
  diff=abs(h[0][0]-h[1][0]);probes.append({'level':level,'xy':[x,y],'height_difference_m':diff,'heights':[r[0]for r in h],'owners':[r[1]for r in h]})
  assert diff<(.002 if strict else .125),(level,x,y,diff,h)
 for y in [75,85,100,110,125,135,140,145,150,165,180,200,220,230]:probe(-172,y,.01,0)
 for x in [-160,-150,-120,-110,-100,-95,-85,-70,-55,-40,-25]:probe(x,235,0,.01)
 for x in [-825,-800,-775,-750,-700,-650,-600,-550,-500,-450,-400,-350,-300,-250,-200,-175]:probe(x,65,0,.01)
 for y in [815,820,825,830,833,840,850,875,900,925]:probe(-190,y,.01,0)
 # Diagonal oldMarine study seam, land and same-level lake water are distinct.
 for a,b in zip([[-190,810],[-140,810],[-80,500],[22,310]],[[-140,810],[-80,500],[22,310],[85,310]]):
  dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy);nx,ny=-dy/L*.01,dx/L*.01
  for v0 in [.1,.25,.5,.75,.9]:probe(a[0]+dx*v0,a[1]+dy*v0,nx,ny)
 assert metrics['triangles']<170000 and metrics['bytes']<21000000 and metrics['gpu_bytes']<45000000,metrics
 summaries[level]=metrics
 audit_level(selected,R/'dist',level,exe,out)
(out/'export-summary.json').write_text(json.dumps({'catalog_revision':cat['revision'],'levels':summaries,'all_new_geometry_identical_across_levels':True,'seam_probes':probes},indent=2)+'\n');print('export summary',summaries,'seamprobes',len(probes))
