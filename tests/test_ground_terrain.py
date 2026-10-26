"""Relative pavement and vertical-kerb lifts preserve authored offsets/winding."""
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.elevation import Elevations
spec=importlib.util.spec_from_file_location('square_terrain_mesh',ROOT/'regions/southport/london-square/public-realm/scripts/terrain_mesh.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def field(tmp_path):
    path=tmp_path/'profile.json'
    path.write_text(json.dumps({'schema_version':1,'datum':'test','controls':{
        str(z):{'height_m':z,'uncertainty_m':0,'status':'test','evidence':'synthetic'}for z in [0,2]},
        'surfaces':{'v':{'bounds':[-2,2,-2,2],'axis_origin':[0,0],'axis_direction':[1,0],
            'profile':[{'distance_m':x,'control':str(z)}for x,z in [(-2,2),(0,0),(2,2)]]}}}))
    return Elevations(path).surface('v')


@pytest.mark.parametrize('reverse',[False,True])
def test_sloped_pavement_keeps_relative_ramp_and_winding(tmp_path,reverse):
    surface=field(tmp_path)
    tri=[(-2,-1,2.04),(2,-1,2.12),(1,1,1.10)]
    if reverse:tri.reverse()
    result=list(module.lift_relative_triangle(tri,surface))
    assert len(result)>1
    for output in result:
        a,b,c=np.asarray(output)
        assert np.cross(b-a,c-a)[2]*( -1 if reverse else 1)>0
        x,y,z=np.mean(output,axis=0)
        assert z==pytest.approx(surface.height(x,y)+.08+.02*x,abs=1e-9)


def test_vertical_kerb_includes_terrain_valley(tmp_path):
    surface=field(tmp_path)
    result=list(module.lift_relative_triangle([(-2,0,1.88),(2,0,1.88),(2,0,2)],surface))
    assert len(result)>1
    points=[p for triangle in result for p in triangle]
    assert any(abs(x)<1e-10 and z<0 for x,y,z in points)
    assert all(-.120000001<=z-surface.height(x,y)<=1e-9 for x,y,z in points)
    assert all(np.cross(np.subtract(t[1],t[0]),np.subtract(t[2],t[0]))[1]<0 for t in result)
