#!/usr/bin/env python3
"""Validate actual exported ground planes, LoD equality and package budgets."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(sys.argv[sys.argv.index('--recipe')+1]).resolve().parents[4]
sys.path[:0]=[str(ROOT/'lib'),str(ROOT/'tools')]
from audit_published_coplanar import primitives
from coplanar import overlaps
from southport3d.elevation import Elevations


def check(package, recipe):
    config=json.loads(recipe.read_text())
    if config['coordinates']['frame']!='site':
        raise ValueError('Terrain package checker expects site coordinates')
    layout=json.loads((recipe.parent/'research/layout.json').read_text())
    plan=Elevations(ROOT/layout['elevation_plan'])
    default_surface=plan.surface(layout['elevation_surface'])
    part_surfaces={key:plan.surface(name)for key,name in layout.get('elevation_surfaces_by_part',{}).items()}
    node_surfaces={key:plan.surface(name)for key,name in layout.get('elevation_surfaces_by_node',{}).items()}
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
            surface=part_surfaces.get(f['part'],default_surface)
            chunks=[]
            for tri,source in primitives(package/f['path'],{'rotationY':0,'position':[0,0,0]}):
                field=next((value for key,value in node_surfaces.items()if key in source['node']),surface)
                xyz=tri[:,:,[0,2,1]]*np.array([1,-1,1]);chunks.append(xyz)
                normal=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0])
                use=abs(normal[:,2])>.7*np.linalg.norm(normal,axis=1)
                centres=xyz[use].mean(axis=1)
                road=any(source['material'].lower().endswith(' '+m)for m in ['asphalt','yellow','white','parking'])
                for x,y,z in centres:
                    if source['node'].startswith('Fountain '):
                        continue  # bounded fountain tiers intentionally differ from road datum
                    err=abs(z-(field.height(float(x),float(y))-(.12 if road else 0)))
                    assert err<1e-4,(level,f['part'],source['node'],x,y,z,err)
                    max_error=max(max_error,err);checked+=1
            values=np.concatenate(chunks)
            if level=='detail':baseline[f['part']]=values
            else:assert np.array_equal(values,baseline[f['part']]),(level,f['part'],'ground changes at LoD transition')
        # The pool is horizontal in every exported LoD and lies within the
        # bounded centre, independent of the street-height lattice.
        pool=[tri for f in files if f['part']=='section-06' for tri,source in primitives(package/f['path'],{'rotationY':0,'position':[0,0,0]}) if source['node'].startswith('Fountain pool')]
        assert pool,(level,'missing fountain pool')
        heights=np.concatenate(pool).reshape(-1,3)[:,1]
        assert float(np.ptp(heights))<1e-5,(level,'pool is not horizontal')
        # Audit representative exported furniture at each level, including a
        # pair of adjacent balustrades.  This catches generator regressions
        # that master-only ownership checks cannot see.
        fixture=next(f for f in files if f['part']=='garden-furniture')
        groups={}
        for tri,source in primitives(package/fixture['path'],{'rotationY':0,'position':[0,0,0]}):
            groups.setdefault(source['node'],[]).append(tri)
        for kind in ('bench','balustrade','globe','column','tree'):
            node=next(n for n in groups if n.startswith('Garden '+kind+' '))
            tris=np.concatenate(groups[node]);errors=overlaps(tris,[node]*len(tris))
            assert not errors,(level,node,errors[:5])
        pair=['Garden balustrade -218 16.4','Garden balustrade -214 16.4']
        tris=np.concatenate([a for node in pair for a in groups[node]])
        errors=overlaps(tris,['adjacent balustrades']*len(tris))
        assert not errors,(level,'balustrade seam',errors[:5])
        totals.update(checked_ground_triangles=checked,max_plane_error_m=max_error)
        rows.append(totals)
    (package/'terrain-check.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Exported terrain checks passed:',rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True)
    args=p.parse_args();check(args.package,args.recipe)
