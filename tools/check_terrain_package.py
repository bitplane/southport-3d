#!/usr/bin/env python3
"""Validate actual exported ground planes, LoD equality and package budgets."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations


def check(package, recipe):
    config=json.loads(recipe.read_text())
    if config['coordinates']['frame']!='site':
        raise ValueError('Terrain package checker expects site coordinates')
    layout=json.loads((recipe.parent/'research/layout.json').read_text())
    surface=Elevations(ROOT/layout['elevation_plan']).surface(layout['elevation_surface'])
    manifest=json.loads((package/'manifest.json').read_text())
    ground={p['id']for p in config['parts']if p.get('ground')}
    baseline={};rows=[]
    for level in ['detail','walk','district']:
        files=[f for f in manifest['files']if f['level']==level]
        budget=layout['budgets']
        totals={'level':level,'triangles':sum(f['triangles']for f in files),
                'bytes':sum(f['bytes']for f in files),'gpu_bytes':sum(f['gpuBytesEstimate']for f in files)}
        assert totals['triangles']<=budget['triangles_per_level'],totals
        assert totals['bytes']<=budget['download_bytes_per_level'],totals
        assert totals['gpu_bytes']<=budget['gpu_bytes_per_level'],totals
        checked=0;max_error=0.
        for f in files:
            if f['part']not in ground:continue
            chunks=[]
            for tri,source in primitives(package/f['path'],{'rotationY':0,'position':[0,0,0]}):
                xyz=tri[:,:,[0,2,1]]*np.array([1,-1,1]);chunks.append(xyz)
                normal=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0])
                use=abs(normal[:,2])>.7*np.linalg.norm(normal,axis=1)
                centres=xyz[use].mean(axis=1)
                road=any(source['material'].lower().endswith(' '+m)for m in ['asphalt','yellow','white','parking'])
                for x,y,z in centres:
                    err=abs(z-(surface.height(float(x),float(y))-(.12 if road else 0)))
                    assert err<1e-4,(level,f['part'],source['node'],x,y,z,err)
                    max_error=max(max_error,err);checked+=1
            values=np.concatenate(chunks)
            if level=='detail':baseline[f['part']]=values
            else:assert np.array_equal(values,baseline[f['part']]),(level,f['part'],'ground changes at LoD transition')
        totals.update(checked_ground_triangles=checked,max_plane_error_m=max_error)
        rows.append(totals)
    (package/'terrain-check.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Exported terrain checks passed:',rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True)
    args=p.parse_args();check(args.package,args.recipe)
