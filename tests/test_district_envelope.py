"""The pilot's coarse topology must not scale with detailed facade features."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from publication_schema import validate_publication
ASSET=ROOT/'regions/southport/london-square/lord-street-116'
spec=importlib.util.spec_from_file_location('bhf_envelope',ASSET/'scripts/district.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_envelope_has_fixed_budget_independent_of_window_detail(tmp_path):
    (tmp_path/'research').mkdir()
    for path in (ASSET/'research').glob('*layout.json'):
        (tmp_path/'research'/path.name).write_bytes(path.read_bytes())
    original=module.surfaces(tmp_path)
    p=tmp_path/'research/layout.json';layout=json.loads(p.read_text())
    layout['upper_bays']=1300;layout['window_moulding_subdivisions']=100
    p.write_text(json.dumps(layout))
    assert module.surfaces(tmp_path)==original
    recipe=json.loads((ASSET/'publication.json').read_text())['district_envelope']
    assert sum(len(f)*2 for f in original.values())<500
    for part,faces in original.items():
        assert len(faces)*2<=recipe['parts'][part]['max_triangles']
        for face in faces:
            assert len(face['vertices'])==4


def test_envelope_schema_requires_complete_parts_and_bounded_atlases():
    recipe=json.loads((ASSET/'publication.json').read_text());validate_publication(recipe)
    bad=copy.deepcopy(recipe);del bad['district_envelope']['parts']['roof']
    with pytest.raises(ValueError):validate_publication(bad)
    bad=copy.deepcopy(recipe);bad['district_envelope']['parts']['roof']['atlas']=[4096,4096]
    with pytest.raises(ValueError):validate_publication(bad)
    bad=copy.deepcopy(recipe);bad['district_envelope']['max_gpu_bytes']=0
    with pytest.raises(ValueError):validate_publication(bad)


def test_memorial_preserves_column_count_with_shared_fixed_topology(tmp_path):
    asset=ROOT/'regions/southport/london-square/war-memorial'
    s=importlib.util.spec_from_file_location('memorial_envelope',asset/'scripts/district.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    (tmp_path/'research').mkdir()
    for name in ('modelling_spec.json','site_layout.json','shaft_masonry_calibration.json'):
        (tmp_path/'research'/name).write_bytes((asset/'research'/name).read_bytes())
    before=m.surfaces(tmp_path)
    p=tmp_path/'research/modelling_spec.json';d=json.loads(p.read_text())
    d['dimensions']['column_flute_count']['value']=200
    p.write_text(json.dumps(d))
    assert m.surfaces(tmp_path)==before
    recipe=json.loads((asset/'publication.json').read_text());validate_publication(recipe)
    for part,faces in before.items():
        assert 2*len(faces)<=recipe['district_envelope']['parts'][part]['max_triangles']
    for part in ('north-east','south-west'):
        faces=before[part]
        shafts=[f for f in faces if f.get('atlas_key','').startswith('column ')]
        assert len(shafts)==16*3*8
        assert len({f['atlas_key'] for f in shafts})==3*8
        # The two lateral window openings are split wall envelopes, not solid boxes.
        assert sum(f['name'].startswith('chamber wall ') for f in faces)==2*2*4*4
