from pathlib import Path
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from southport3d import planar

class PlanarTests(unittest.TestCase):
    def test_cutout_preserves_area_without_overlay(self):
        outer=[(0,0),(10,0),(10,10),(0,10)];hole=[(4,4),(6,4),(6,6),(4,6)]
        pieces=planar.subtract(outer,hole)
        self.assertAlmostEqual(sum(map(planar.area,pieces)),96)
        # Applying the same cutter twice must not remove any more surface.
        self.assertAlmostEqual(sum(planar.area(q) for p in pieces for q in planar.subtract(p,hole)),96)
    def test_external_and_covering_cuts(self):
        poly=[(0,0),(2,0),(2,2),(0,2)]
        self.assertEqual(planar.subtract(poly,[(3,3),(4,3),(4,4),(3,4)]),[poly])
        self.assertEqual(planar.subtract(poly,[(-1,-1),(3,-1),(3,3),(-1,3)]),[])
    def test_rotated_cutter(self):
        pieces=planar.subtract([(-3,-3),(3,-3),(3,3),(-3,3)],[(0,-2),(2,0),(0,2),(-2,0)])
        self.assertAlmostEqual(sum(map(planar.area,pieces)),28)

if __name__=='__main__':unittest.main()
