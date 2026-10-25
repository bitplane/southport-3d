"""Check actual float32 exports and fixed District bounds/budgets."""
import argparse,json,sys,subprocess
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args();repo=a.recipe.resolve().parents[4];sys.path.insert(0,str(repo/'tools'))
from publication import inspect_glb
from audit_published_coplanar import primitives
exe=a.package/'bridge-coplanar-scan';subprocess.run(['g++','-O3','-std=c++17',str(repo/'tools/coplanar_scan.cpp'),'-o',str(exe)],check=True)
assembly=json.loads((a.package/'assembly.json').read_text());rows=[]
for level in ['detail','walk','district']:
 fs=[a.package/f['path']for f in assembly['files']if f['level']==level];infos=[inspect_glb(f)for f in fs];n=sum(i['triangles']for i in infos);size=sum(i['bytes']for i in infos);gpu=sum(i['gpuBytesEstimate']for i in infos);assert n<({'detail':150000,'walk':150000,'district':6000}[level]),(level,n)
 if level=='district':assert size<=4000000 and gpu<=16000000,(size,gpu)
 tris=np.concatenate([t for f in fs for t,_ in primitives(f,{'rotationY':0,'position':[0,0,0]})]);assert np.isfinite(tris).all();assert abs(tris[:,:,1].max()-56.6)<.02,(level,'pylon height');
 geo=a.package/('bridge-'+level+'.bin');pairs=a.package/('bridge-'+level+'-pairs.bin');np.asarray(tris,dtype='<f8').tofile(geo);subprocess.run([str(exe),str(geo),str(pairs)],check=True);hits=np.fromfile(pairs,dtype=[('a','<u4'),('b','<u4'),('area','<f8')]);assert len(hits)==0,(level,'exported coplanar conflicts',hits[:8]);rows.append({'coplanar_candidates':len(hits),'level':level,'triangles':n,'bytes':size,'gpu_bytes':gpu,'bounds':[tris.min((0,1)).tolist(),tris.max((0,1)).tolist()]})
(a.package/'bridge-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
