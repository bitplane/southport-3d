"""Regression checks for publication typos and competing build processes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_lock import asset_lock
from publication_schema import validate_publication


class PublicationSchemaTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / 'regions/southport/london-square/public-realm/publication.json').read_text())

    def test_all_asset_recipes(self):
        for path in (ROOT / 'regions').rglob('publication.json'):
            with self.subTest(path=path):
                validate_publication(json.loads(path.read_text()))

    def test_invalid_contracts_fail_before_build(self):
        mutations = [
            lambda s: s['parts'][0].update(walkable=True),
            lambda s: s['parts'][0].update(ground='true'),
            lambda s: s['coordinates'].update(elevation_m=float('nan')),
            lambda s: s['walk_spawn'].update(position=[1, 2]),
            lambda s: s['levels']['district'].update(texture_size=1024),
            lambda s: s['rules'][0]['walk'].update(bkae=False),
        ]
        for mutate in mutations:
            spec = copy.deepcopy(self.spec)
            mutate(spec)
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                validate_publication(spec)


class BuildLockTests(unittest.TestCase):
    def test_process_contention_and_exception_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = ('import sys; from pathlib import Path; '
                    'from build_lock import asset_lock; '
                    'with_lock = asset_lock(Path(sys.argv[1]), sys.argv[2]); '
                    'with_lock.__enter__(); with_lock.__exit__(None,None,None)')
            def attempt(name):
                return subprocess.run([sys.executable, '-c', code, directory, name],
                                      cwd=ROOT / 'tools', capture_output=True)
            with self.assertRaises(RuntimeError):
                with asset_lock(root, 'one'):
                    self.assertNotEqual(attempt('one').returncode, 0)
                    self.assertEqual(attempt('two').returncode, 0)
                    raise RuntimeError('failed build')
            self.assertEqual(attempt('one').returncode, 0)


class GroundConformanceTests(unittest.TestCase):
    def test_t_junction_preserves_area_and_shares_exported_edges(self):
        sys.path.insert(0, str(ROOT / 'lib'))
        from southport3d.conform import conform

        class Mesh:
            def __init__(self, name):
                self.name = name
                self.vertices = []
                self.faces = []

            def add(self, vertices, faces):
                offset = len(self.vertices)
                self.vertices.extend(vertices)
                self.faces.extend(tuple(i + offset for i in face) for face in faces)

        left, right = Mesh('left'), Mesh('right')
        left.add([(0, 0, 0), (1, 0, 0), (1, 2, 0), (0, 2, 0)], [(0, 1, 2, 3)])
        for y in (0, 1):
            right.add([(1, y, 0), (2, y, 0), (2, y + 1, 0), (1, y + 1, 0)], [(0, 1, 2, 3)])
        result, report = conform({'left': left, 'right': right})
        self.assertGreater(report['inserted_edge_junctions'], 0)
        boundaries = {}
        for key, mesh in result.items():
            area = 0
            boundaries[key] = set()
            for face in mesh.faces:
                a, b, c = [mesh.vertices[i] for i in face]
                triangle = abs((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])) / 2
                self.assertGreater(triangle, 0)
                area += triangle
                for p, q in ((a, b), (b, c), (c, a)):
                    if p[0] == q[0] == 1:
                        boundaries[key].add(tuple(sorted((p, q))))
            self.assertAlmostEqual(area, 2)
        self.assertEqual(boundaries['left'], boundaries['right'])
        self.assertEqual(len(boundaries['left']), 2)
