import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from publication import east_north_offset, load_publication


class PublicationTests(unittest.TestCase):
    def test_geographic_origin_and_cardinal_directions(self):
        origin=[53.6486555,-3.0043401]
        self.assertEqual(east_north_offset(origin,origin),(0,0))
        east,north=east_north_offset(origin,[origin[0]+.001,origin[1]])
        self.assertAlmostEqual(east,0,places=5)
        self.assertGreater(north,110);self.assertLess(north,112)
        east,north=east_north_offset(origin,[origin[0],origin[1]+.001])
        self.assertGreater(east,65);self.assertLess(east,67);self.assertLess(abs(north),.01)

    def test_recipe_has_complete_level_decisions(self):
        source=ROOT/'regions/southport/london-square/war-memorial/publication.json'
        self.assertEqual(len(load_publication(source)['parts']),4)
        ground=load_publication(ROOT/'regions/southport/london-square/public-realm/publication.json')
        self.assertTrue(any(p.get('ground',False) for p in ground['parts']))
        for part in ground['parts']:
            expected=part['id'].endswith('-ground') or part['id'] in {'roads','perimeter'}
            self.assertEqual(bool(part.get('ground',False)),expected,part['id'])
        self.assertFalse(any(p['id']=='ground' for p in load_publication(source)['parts']))
        data=json.loads(source.read_text())
        del data['rules'][0]['walk']['reason']
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'publication.json';path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_publication(path)

    def test_duplicate_streaming_parts_rejected(self):
        data=json.loads((ROOT/'regions/southport/london-square/war-memorial/publication.json').read_text())
        data['parts'].append(data['parts'][0])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'publication.json';path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_publication(path)


if __name__=='__main__':unittest.main()


def test_envelope_budget_rejects_texture_floor_before_baking():
    import copy
    import pytest
    from publication_schema import validate_publication
    spec=json.loads((ROOT/'regions/southport/london-square/war-memorial/publication.json').read_text())
    envelope=spec['district_envelope']
    floor=sum(p['atlas'][0]*p['atlas'][1]*16 for p in envelope['parts'].values())
    for cap in (floor-1,floor):
        trial=copy.deepcopy(spec);trial['district_envelope']['max_gpu_bytes']=cap
        with pytest.raises(ValueError,match='atlas memory floor'):
            validate_publication(trial)
    # This is only a necessary lower bound. Export still checks actual buffers.
    spec['district_envelope']['max_gpu_bytes']=floor+1
    validate_publication(spec)


def test_terrace_envelope_guard_checks_coverage_and_normals(tmp_path):
    import copy
    import pytest
    script=ROOT/'regions/southport/london-square/lord-street-118-122/scripts/check_package.py'
    loader=importlib.util.spec_from_file_location('terrace_appearance_check',script)
    module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
    recipe=tmp_path/'recipe.json';recipe.write_text(json.dumps({'district_envelope':{'parts':{'architecture':{}}}}))
    checks={channel:{'receiver_coverage':1.0} for channel in ('base-color','normal','roughness')}
    checks['normal'].update(raw_invalid_normal_fraction=0.0,invalid_normal_fraction=0.0)
    report={'prototypes':[],'envelope':{'parts':{'architecture':{'bake_checks':checks}}}}
    assembly=tmp_path/'assembly.json';assembly.write_text(json.dumps(report))
    module.check(tmp_path,recipe)
    for channel,key,value in [('base-color','receiver_coverage',.5),('normal','raw_invalid_normal_fraction',.1),('normal','invalid_normal_fraction',float('nan'))]:
        broken=copy.deepcopy(report);broken['envelope']['parts']['architecture']['bake_checks'][channel][key]=value
        assembly.write_text(json.dumps(broken))
        with pytest.raises(ValueError):module.check(tmp_path,recipe)
    report['envelope']['parts']={};assembly.write_text(json.dumps(report))
    with pytest.raises(ValueError,match='Missing District'):module.check(tmp_path,recipe)


def test_named_support_surfaces_require_walkable_parts():
    import pytest
    from publication_schema import validate_publication
    p=ROOT/'regions/southport/station-quarter/public-realm/publication.json'
    spec=json.loads(p.read_text());validate_publication(spec)
    spec['parts'][0]['ground']=False
    with pytest.raises(ValueError,match='support_surface requires'):validate_publication(spec)
