"""Check actual exported ground, Venetian layers and fixed package budgets."""
import json,sys
from pathlib import Path
import numpy as np
recipe=Path(sys.argv[sys.argv.index('--recipe')+1]).resolve()
package=Path(sys.argv[sys.argv.index('--package')+1]).resolve()
repo=recipe.parents[4]
sys.path[:0]=[str(repo/'tools'),str(repo/'lib'),str(recipe.parent/'scripts')]
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations
from venetian_ground import Transition,at
config=json.loads(recipe.read_text());layout=json.loads((recipe.parent/'research/layout.json').read_text())
plan=Elevations(repo/layout['elevation_plan']);base=plan.surface('south-mainland');bridge=plan.surface('south-venetian');water=plan.surface('south-water')
landing=Transition(base,bridge,'landing');lower=Transition(base,bridge,'lower')
manifest=json.loads((package/'manifest.json').read_text());ground={p['id']for p in config['parts']if p.get('ground')};baseline={};rows=[]
for level in ('detail','walk','district'):
 files=[f for f in manifest['files'] if f['level']==level];budgets=layout['budgets']
 totals={'level':level,'triangles':sum(f['triangles']for f in files),'bytes':sum(f['bytes']for f in files),'gpu_bytes':sum(f['gpuBytesEstimate']for f in files)}
 for key,limit in [('triangles','triangles_per_level'),('bytes','download_bytes_per_level'),('gpu_bytes','gpu_bytes_per_level')]:assert totals[key]<=budgets[limit],totals
 bridge_files=[f for f in files if f['part']=='venetian-structure'];bb=layout['venetian_structure_budgets'];assert bridge_files
 assert sum(f['triangles']for f in bridge_files)<=bb[level+'_triangles'],(level,'bridge triangle budget')
 if level=='district':
  assert sum(f['bytes']for f in bridge_files)<=bb['district_download_bytes']
  assert sum(f['gpuBytesEstimate']for f in bridge_files)<=bb['district_gpu_bytes']
 checked=0;custom=0;layers={}
 for f in files:
  if f['part'] not in ground:continue
  chunks=[]
  for tri,source in primitives(package/f['path'],{'rotationY':0,'position':[0,0,0]}):
   xyz=tri[:,:,[0,2,1]]*np.array([1,-1,1]);chunks.append(xyz);name=source['node'];norm=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]);use=abs(norm[:,2])>.7*np.linalg.norm(norm,axis=1)
   selected=xyz[use];road=any(source['material'].lower().endswith(' '+m)for m in ['asphalt','yellow','white','parking'])
   if name.startswith('Ground island '):
    z=selected[:,:,2];assert np.all(z>=water.height(-300,400)-.001) and np.all(z<=water.height(-300,400)+1.551);custom+=len(selected);continue
   if name.startswith('Ground Venetian lower access steps'):
    assert len(selected)>0 and np.isfinite(selected).all();layers.setdefault('stairs',[]).append(selected);custom+=len(selected);continue
   field=bridge if name=='Ground Venetian bridge top' else landing if ' landing ' in name else lower if ' lower ' in name else base
   centres=selected.mean(axis=1);offset=.12 if road else 0
   for x,y,z in centres:
    error=abs(z-(field.height(float(x),float(y))-offset));assert error<(.101 if field in (landing,lower) else .00015),(level,name,x,y,z,error)
    checked+=1
   if name=='Ground Venetian bridge top':layers['deck']=selected
   if ' lower ' in name:layers.setdefault('lower',[]).append(selected)
  assert chunks,(level,f['part'],'missing ground');values=np.concatenate(chunks)
  if level=='detail':baseline[f['part']]=values
  else:assert np.array_equal(values,baseline[f['part']]),(level,f['part'],'ground changes at LoD transition')
 assert layers.get('deck') is not None and layers.get('lower') and layers.get('stairs'),(level,'missing distinct bridge/lower layers')
 def probe(triangles,point):
  tris=np.concatenate(triangles) if isinstance(triangles,list) else triangles
  u=tris[:,1,:2]-tris[:,0,:2];v=tris[:,2,:2]-tris[:,0,:2];q=np.asarray(point)-tris[:,0,:2];det=u[:,0]*v[:,1]-u[:,1]*v[:,0];valid=abs(det)>1e-9
  a=np.divide(q[:,0]*v[:,1]-q[:,1]*v[:,0],det,out=np.zeros_like(det),where=valid);b=np.divide(u[:,0]*q[:,1]-u[:,1]*q[:,0],det,out=np.zeros_like(det),where=valid)
  hit=valid&(a>=-1e-6)&(b>=-1e-6)&(a+b<=1+1e-6)
  return list(tris[hit,0,2]+a[hit]*(tris[hit,1,2]-tris[hit,0,2])+b[hit]*(tris[hit,2,2]-tris[hit,0,2]))
 deck_z=probe(layers['deck'],at(151,0));lower_z=probe(layers['lower'],at(151,0))
 assert deck_z and lower_z and min(deck_z)-.3-max(lower_z)>1.7,(level,deck_z,lower_z,'underpass clearance')
 for j in range(11):assert probe(layers['stairs'],at(151,-2.6-(j+.5)*3.6/11)),(level,j,'missing stair tread')
 totals.update(checked_ground_triangles=checked,checked_custom_triangles=custom);rows.append(totals)
(package/'terrain-check.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Exported terrain levels and budgets:',rows)
