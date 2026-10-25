"""Profile shape, bounds and breakline regressions independent of Blender."""
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from southport3d.elevation import Elevations


def test_chapel_survey_preserves_relative_entrance_ramp():
    p=Path(__file__).resolve().parents[1]/'regions/southport/elevation/station-approach.json'
    surface=Elevations(p).surface('chapel-pedestrian')
    for x in [-270,-254,-170,-95,-5.301,-5.3,-5.299,-5,-4.301,-4.3,0]:
        assert surface.height(x,-144)==pytest.approx(surface.base.height(x,-144)-.12*max(0,min(1,(x+5.3))))
    with pytest.raises(ValueError,match='outside'):surface.height(surface.bounds[0]-1,-144)


def make_plan(tmp_path):
    controls={k:{'height_m':z,'evidence':'Test geometry','status':'synthetic','uncertainty_m':0} for k,z in [('low',0),('high',4)]}
    common={'bounds':[-1,11,-2,2],'axis_origin':[0,0],'axis_direction':[1,0]}
    d={'schema_version':1,'datum':'test','controls':controls,'surfaces':{
       'deck':dict(common,profile=[{'distance_m':0,'control':'low'},{'distance_m':5,'control':'high'},{'distance_m':10,'control':'low'}]),
       'below':dict(common,profile=[{'distance_m':0,'control':'low'}])}}
    p=tmp_path/'heights.json';p.write_text(json.dumps(d));return p


def test_crest_is_in_mesh_and_layers_remain_distinct(tmp_path):
    e=Elevations(make_plan(tmp_path));s=e.surface('deck')
    assert s.height(5,0)==4 and e.surface('below').height(5,0)==0
    triangles=list(s.lift_triangle([(-1,-1),(11,-1),(5,1)]))
    assert max(p[2] for tri in triangles for p in tri)==4
    for tri in triangles:
        centre=tuple(sum(p[i] for p in tri)/3 for i in range(3))
        assert s.height(*centre[:2])==pytest.approx(centre[2])


def test_includes_share_controls_and_detect_conflicts(tmp_path):
    base=make_plan(tmp_path)
    p=tmp_path/'consumer.json';p.write_text(json.dumps({'schema_version':1,'datum':'test','includes':['heights.json'],'surfaces':{},'controls':{}}))
    assert Elevations(p).surface('deck').height(5,0)==4
    d=json.loads(base.read_text());d['includes']=['consumer.json'];base.write_text(json.dumps(d))
    with pytest.raises(ValueError,match='Cyclic'):Elevations(p)


def test_wall_edge_keeps_crest_in_either_direction(tmp_path):
    s=Elevations(make_plan(tmp_path)).surface('deck')
    points=list(s.edge_points((-1,0),(11,0)))
    assert [p[0] for p in points]==[-1,0,5,10,11]
    assert max(p[2] for p in points)==4
    assert list(s.edge_points((11,0),(-1,0)))==list(reversed(points))
