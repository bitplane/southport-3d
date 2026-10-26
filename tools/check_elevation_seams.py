#!/usr/bin/env python3
"""Probe neighbouring exported migration packages at their shared road seams.

Runs on isolated packages; does not modify the live catalog. Each probe samples
both sides of an ownership boundary and removes the measured terrain difference,
so a real gradient is not misreported as a crack.
"""
import json
from pathlib import Path
import sys
import numpy as np
from audit_published_coplanar import primitives

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.elevation import Elevations


def triangles(asset,level):
    source=next(p.parent for p in (ROOT/'regions/southport').rglob('asset.json')if json.loads(p.read_text())['id']==asset)
    recipe=json.loads((source/'publication.json').read_text())
    assert recipe['coordinates']['frame']=='site' and recipe['coordinates']['elevation_m']==0
    ground={p['id']for p in recipe['parts']if p.get('ground')}
    package=ROOT/'build'/asset/'package'
    manifest=json.loads((package/'manifest.json').read_text())
    chunks=[]
    for item in manifest['files']:
        if item['level']==level and item['part']in ground:
            for tri,_ in primitives(package/item['path'],{'rotationY':0,'position':[0,0,0]}):
                chunks.append(tri[:,:,[0,2,1]]*np.array([1,-1,1]))
    return np.concatenate(chunks)


def height(tris,x,y):
    a=tris[:,0];u=tris[:,1]-a;v=tris[:,2]-a
    det=u[:,0]*v[:,1]-u[:,1]*v[:,0]
    valid=abs(det)>1e-10
    a,u,v,det=a[valid],u[valid],v[valid],det[valid]
    dx,dy=x-a[:,0],y-a[:,1]
    b=(dx*v[:,1]-dy*v[:,0])/det;c=(u[:,0]*dy-u[:,1]*dx)/det
    hits=(b>=-1e-7)&(c>=-1e-7)&(b+c<=1+1e-7)
    if not np.any(hits):raise AssertionError(('Ground hole at seam',x,y))
    return float(np.max((a[:,2]+b*u[:,2]+c*v[:,2])[hits]))


def main():
    square='southport.london-square.public-realm'
    field=Elevations(ROOT/'regions/southport/elevation/london-square.json').surface('london-square-pavement')
    seams=[('Glebe mouth','southport.glebe-place.public-realm',[((-4.305,y),(-4.295,y))for y in [-68.5,-67,-65,-64.3]]),
           ('Nevill junction','southport.nevill-street.public-realm',[((x,41.005),(x,40.995))for x in [-3,0,2]])]
    results=[]
    for level in ['detail','walk','district']:
        square_tri=triangles(square,level)
        for name,asset,probes in seams:
            other=triangles(asset,level)
            for a,b in probes:
                za,zb=height(other,*a),height(square_tri,*b)
                # Glebe's last 0.8 m is the explicit 0.12 m throat ramp.
                expected=.12*((-4.3-a[0])/.8) if name=='Glebe mouth'else 0
                error=abs((za-field.height(*a))-(zb-field.height(*b))-expected)
                assert error<.001,(level,name,a,b,za,zb,error)
                results.append(dict(level=level,seam=name,a=a,b=b,height_a=za,height_b=zb,residual_m=error))
    out=ROOT.parent/'output/elevation/connected-seams.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2)+'\n')
    print(f'{len(results)} actual exported seam pairs passed; maximum residual {max(r["residual_m"]for r in results):.8f} m')


if __name__=='__main__':main()
