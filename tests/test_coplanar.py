"""Regression cases for the exterior coplanar-surface audit."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from coplanar import overlaps


def test_duplicate_and_partial_overlap():
    a=np.array([[0,0,0],[2,0,0],[0,2,0]],float)
    assert overlaps([a,a+(.2,.2,0)],['front','return'])
    assert overlaps([a,a],['front','duplicate'])


def test_tiled_edge_and_opposite_seam_are_not_overlaps():
    a=np.array([[0,0,0],[1,0,0],[0,1,0]],float)
    b=np.array([[1,0,0],[1,1,0],[0,1,0]],float)
    assert not overlaps([a,b],['tile','tile'])
    assert not overlaps([a,a[::-1]],['internal','internal'])
    assert not overlaps([a,a+(0,0,.005)],['wall','trim'])


def test_rotated_nearly_coplanar_float32_faces():
    a=np.array([[0,0,0],[2,0,0],[0,2,0]],float)
    c,s=np.cos(.73),np.sin(.73)
    r=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    a=(a@r.T+100).astype('float32')
    assert overlaps([a,a+1e-6],['a','b'])
