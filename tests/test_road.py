"""Metric offsets and ownership cuts must agree before meshes are assembled."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from southport3d.road import parallel,clip_segment,marking_segments


class RoadEdges(unittest.TestCase):
    def test_bend_preserves_perpendicular_setback(self):
        kerb=[(0,0),(8,0),(11,7),(20,7)]
        curve=parallel(kerb,.36)
        for a,b,p,q in zip(kerb,kerb[1:],curve,curve[1:]):
            length=math.dist(a,b)
            for point in [p,q]:
                distance=((b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]))/length
                self.assertAlmostEqual(distance,.36)

    def test_adjacent_tiles_share_identical_paint_endpoints(self):
        kerb=[(-4.3,-154),(-4.3,-46),(-6.2,-36),(-6.2,-25.3)]
        for station in [-116,-76,-46,-36]:
            south=list(marking_segments(kerb,-1,(-10,-154,10,station)))
            north=list(marking_segments(kerb,-1,(-10,station,10,-25.3)))
            for offset in [.18,.36]:
                end=[segment[1] for d,segment in south if d==offset][-1]
                start=[segment[0] for d,segment in north if d==offset][0]
                self.assertAlmostEqual(end[0],start[0],places=12)
                self.assertAlmostEqual(end[1],start[1],places=12)

    def test_open_boundary_has_no_return_paint(self):
        for _,segment in marking_segments([(0,21),(80,21)],1,(41,-27,73,41)):
            self.assertEqual(segment[0][0],41)
            self.assertEqual(segment[1][0],73)
            self.assertEqual(segment[0][1],segment[1][1])
        self.assertIsNone(clip_segment((0,0),(1,1),(2,2,3,3)))

    def test_bad_kerb_requires_explicit_geometry(self):
        with self.assertRaises(ValueError):parallel([(0,0),(0,0)],.18)
        with self.assertRaises(ValueError):parallel([(0,0),(1,0),(0,0)],.18)
