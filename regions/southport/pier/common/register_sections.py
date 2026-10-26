"""Explicit section origins with millimetre-consistent shared ENU seams.

Use the publication's WGS84 ECEF/ENU conversion, not a metres-per-degree
approximation that accumulates centimetres at every section boundary.
"""
import json,math,sys
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(REPO/'tools'))
from publication import east_north_offset

def origin(station):
    world=json.loads((REPO/'viewer/world.json').read_text())['origin_wgs84_lat_lon']
    base=[53.6506289,-3.0082552];yaw=math.radians(148.06834026980724)
    goal=np.asarray(east_north_offset(world,base))+station*np.array([math.cos(yaw),math.sin(yaw)])
    guess=np.asarray(base,float)
    for _ in range(4):
        actual=np.asarray(east_north_offset(world,guess));jac=np.column_stack([(np.asarray(east_north_offset(world,guess+np.eye(2)[i]*1e-6))-actual)/1e-6 for i in range(2)])
        guess+=np.linalg.solve(jac,goal-actual)
    assert np.linalg.norm(np.asarray(east_north_offset(world,guess))-goal)<1e-5
    return guess.tolist()

if __name__=='__main__':
    for path in (REPO/'regions/southport/pier').glob('section-*/asset.json'):
        a=json.loads(path.read_text());section=json.loads((path.parent/'research/section.json').read_text());a['origin_wgs84_lat_lon']=origin(section['stations'][0]);path.write_text(json.dumps(a,indent=2)+'\n')
