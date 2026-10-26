"""Actual exported geometry: overlaps, degeneracy, deck datum and bounded LoDs."""
import json,subprocess,sys
from pathlib import Path
import numpy as np

def run(package,recipe,repo):
    sys.path.insert(0,str(repo/'tools'))
    from publication import inspect_glb
    from audit_published_coplanar import primitives
    exe=package/'pier-coplanar-scan';subprocess.run(['g++','-O3','-std=c++17',str(repo/'tools/coplanar_scan.cpp'),'-o',str(exe)],check=True)
    assembly=json.loads((package/'assembly.json').read_text());report=[]
    for level in ['detail','walk','district']:
        files=[package/r['path']for r in assembly['files']if r['level']==level]
        infos=[inspect_glb(f)for f in files];count=sum(i['triangles']for i in infos)
        assert count<({'detail':160000,'walk':100000,'district':10200}[level]),(level,count)
        tris=np.concatenate([t for f in files for t,_ in primitives(f,{'rotationY':0,'position':[0,0,0]})])
        assert np.isfinite(tris).all()
        area=np.linalg.norm(np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),axis=1)/2
        assert area.min()>1e-10,(level,'float32 degeneracy',area.min())
        geometry=package/(level+'-triangles.bin');hitsfile=package/(level+'-overlaps.bin');tris.astype('<f8').tofile(geometry)
        subprocess.run([str(exe),str(geometry),str(hitsfile)],check=True)
        hits=np.fromfile(hitsfile,dtype=[('a','<u4'),('b','<u4'),('area','<f8')]);assert len(hits)==0,(level,'coplanar overlaps',hits[:5])
        report.append({'level':level,'triangles':count,'bytes':sum(i['bytes']for i in infos),'gpu_bytes':sum(i['gpuBytesEstimate']for i in infos),'coplanar_pairs':len(hits),'minimum_triangle_area':float(area.min())})
    (package/'pier-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
