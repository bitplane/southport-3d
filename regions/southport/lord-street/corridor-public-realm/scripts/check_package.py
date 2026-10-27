#!/usr/bin/env python3
"""Validate actual exported ground planes, LoD equality and package budgets."""
import argparse
import json
import math
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
        # Sample both end cross paths and the short central approaches on the
        # actual exported meshes. These points deliberately sit away from cell
        # edges and check continuity, not an internal polygon count.
        samples=[(-221.0,-20.1),(-221.0,-13.1),(-221.0,8.1),(-221.0,14.1),
                 (-160.9,-20.1),(-160.9,-13.1),(-160.9,8.1),(-160.9,14.1),
                 (-185.7,9.1),(-185.7,-20.1),(-205.1,-2.5),(-170.1,-2.5)]
        patterned=[];by_kind={'pattern':[],'pattern-light':[]}
        for f in files:
            if f['part'] not in ('section-05','section-06'):continue
            for tri,source in primitives(package/f['path'],{'rotationY':0,'position':[0,0,0]}):
                if source['node'].startswith(('Ground section-05 pattern','Ground section-06 pattern')):
                    xy=tri[:,:,[0,2]]*np.array([1,-1]);patterned.append(xy)
                    by_kind['pattern-light' if source['node'].endswith('pattern-light') else 'pattern'].append(xy)
        assert patterned,(level,'missing patterned ground')
        tris=np.concatenate(patterned);a,b,c=tris[:,0],tris[:,1],tris[:,2]
        def orient(u,v,p):return (v[:,0]-u[:,0])*(p[1]-u[:,1])-(v[:,1]-u[:,1])*(p[0]-u[:,0])
        for point in samples:
            signs=np.stack([orient(a,b,point),orient(b,c,point),orient(c,a,point)],axis=1)
            covered=((signs>=-1e-6).all(axis=1)|(signs<=1e-6).all(axis=1)).any()
            assert covered,(level,'decorated path interrupted',point)
        # In the centre of a broad curved panel, dark and pale samples must
        # alternate across each double frame. A further pale sample checks the
        # separation between neighbouring panels in the exported geometry.
        samples_on_panel=[(6.55,45,'pattern'),(6.72,45,'pattern-light'),
                          (6.90,45,'pattern'),(7.30,45,'pattern-light'),
                          (8.90,45,'pattern'),(9.07,45,'pattern-light'),
                          (9.22,45,'pattern'),(8.0,25.5,'pattern-light')]
        for radius,degrees,expected in samples_on_panel:
            t=math.radians(degrees);point=(-185.7+radius*math.cos(t),-2.5+radius*math.sin(t))
            tri=np.concatenate(by_kind[expected]);pa,pb,pc=tri[:,0],tri[:,1],tri[:,2]
            signs=np.stack([orient(pa,pb,point),orient(pb,pc,point),orient(pc,pa,point)],axis=1)
            covered=((signs>=-1e-6).all(axis=1)|(signs<=1e-6).all(axis=1)).any()
            assert covered,(level,'fountain panel frame or gap missing',radius,degrees,expected)
        # A point released by the translated south footprint is paved, while
        # a point newly occupied by that footprint has no competing ground.
        section=next(f for f in files if f['part']=='section-05')
        ground_tris=[tri[:,:,[0,2]]*np.array([1,-1]) for tri,source in primitives(package/section['path'],{'rotationY':0,'position':[0,0,0]})
                     if source['node'].startswith('Ground ') and not source['node'].endswith(' kerb')]
        tri=np.concatenate(ground_tris);a,b,c=tri[:,0],tri[:,1],tri[:,2]
        area=abs((b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0]))
        for point,expected in [((-234,-6.5),True),((-224,-2.5),False)]:
            signs=np.stack([orient(a,b,point),orient(b,c,point),orient(c,a,point)],axis=1)
            covered=(((signs>=-1e-6).all(axis=1)|(signs<=1e-6).all(axis=1))&(area>1e-8)).any()
            assert covered==expected,(level,'pavilion ground cutout',point,covered)
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
        pair=['Garden balustrade -214 16.4','Garden balustrade -210 16.4']
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
