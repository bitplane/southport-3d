"""Opt-in projection contract; compatible with unittest discovery and pytest."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from publication_schema import action

def recipe():
    return dict(strategy='replace',reason='Straight architectural frame',shape='box',
                uv='box',bake=True,cage_extrusion_m=.4,max_sampled_error_m=.35,
                bake_projection='face-normal')

def test_face_normal_projection_is_explicit():
    action(recipe(),'test')
    original=recipe();del original['bake_projection'];action(original,'legacy')

def test_projection_rejects_typos_and_inapplicable_receivers():
    for change in ({'bake_projection':'face-nromal'},{'bake':False},
                   {'shape':'panel','uv':'planar-xy'},{'strategy':'keep'}):
        value=recipe();value.update(change)
        try:action(value,'invalid')
        except ValueError:continue
        raise AssertionError(change)

def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(fn) for fn in
        (test_face_normal_projection_is_explicit,test_projection_rejects_typos_and_inapplicable_receivers))

if __name__=='__main__':unittest.main()
