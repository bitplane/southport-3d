"""Contract failures that would silently publish wrong or incomplete assets."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
from southport3d.lod import load_recipe

spec = importlib.util.spec_from_file_location('check_lods', ROOT / 'tools/check_lods.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads((ROOT / 'regions/southport/london-square/war-memorial/lod.json').read_text())

    def load(self, recipe):
        with tempfile.TemporaryDirectory() as folder:
            relief = Path(folder) / 'research/relief-data'
            relief.mkdir(parents=True)
            shutil.copy(ROOT / 'regions/southport/london-square/war-memorial/research/relief-data/victory.npz', relief / 'victory.npz')
            path = Path(folder) / 'lod.json'
            path.write_text(json.dumps(recipe))
            return load_recipe(path)

    def test_current_recipe(self):
        self.assertEqual(self.load(self.recipe)['scope'], 'component-pilot')

    def test_bad_recipes_rejected(self):
        for mutation in ('path', 'duplicate', 'reversed', 'texture', 'distance', 'method', 'missing-action', 'reason', 'source-path'):
            with self.subTest(mutation=mutation):
                recipe = copy.deepcopy(self.recipe)
                if mutation == 'path': recipe['targets'][0]['id'] = '../other'
                if mutation == 'duplicate': recipe['targets'].append(recipe['targets'][0])
                if mutation == 'reversed': recipe['levels'].reverse()
                if mutation == 'texture': recipe['levels'][0]['texture_size'] = 1000
                if mutation == 'distance': recipe['targets'][0]['cage_extrusion_m'] = -1
                if mutation == 'method': recipe['targets'][0]['actions']['lod1']['strategy'] = 'unimplemented'
                if mutation == 'missing-action': del recipe['targets'][0]['actions']['lod2']
                if mutation == 'reason': recipe['targets'][0]['actions']['lod1']['reason'] = ''
                if mutation == 'source-path': recipe['targets'][1]['actions']['lod1']['source_npz'] = '../outside.npz'
                with self.assertRaises(ValueError): self.load(recipe)

    def test_truncated_glb_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.glb'
            path.write_bytes(struct.pack('<4sII', b'glTF', 2, 99))
            with self.assertRaises(ValueError): checks.read_glb(path)

    def test_translation_rotation_scale(self):
        import numpy as np
        matrix = checks.matrix({'translation': [1, 2, 3], 'rotation': [0, 0, 2**-.5, 2**-.5], 'scale': [2, 2, 2]})
        np.testing.assert_allclose(matrix @ [1, 0, 0, 1], [1, 4, 3, 1], atol=1e-8)


if __name__ == '__main__':
    unittest.main()
