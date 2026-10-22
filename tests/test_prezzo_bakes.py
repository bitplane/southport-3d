"""Regression for dark window borders from a too-short projection cage."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prezzo_checks',ROOT/'regions/southport/london-square/prezzo/scripts/check_package.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class WindowBakeCoverage(unittest.TestCase):
    def test_missed_colour_rays_fail_even_with_valid_normals(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);recipe=root/'recipe.json'
            recipe.write_text(json.dumps({'levels':{'district':{'texture_size':256}}}))
            row={'rule':'windows','level':'district','source_object':'window','bake_checks':{'base-color':{'covered_pixels':55094},'roughness':{'covered_pixels':55094},'normal':{'covered_pixels':65536,'invalid_normal_fraction':0}}}
            report=root/'assembly.json';report.write_text(json.dumps({'prototypes':[row]}))
            with self.assertRaisesRegex(ValueError,'coverage'):module.check(root,recipe)
            for channel in ['base-color','roughness']:row['bake_checks'][channel]['covered_pixels']=64468
            report.write_text(json.dumps({'prototypes':[row]}));module.check(root,recipe)
