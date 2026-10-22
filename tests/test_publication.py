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
        self.assertEqual(len(load_publication(source)['parts']),5)
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
