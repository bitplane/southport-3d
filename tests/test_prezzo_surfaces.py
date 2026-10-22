"""Regression for exact surface ownership in the detailed architectural meshes."""
from pathlib import Path
import shutil
import subprocess
import unittest


class PrezzoSurfaces(unittest.TestCase):
    @unittest.skipUnless(shutil.which('blender'), 'Blender is required for mesh integration')
    def test_coplanar_cleanup_preserves_union_winding_and_materials(self):
        scripts=Path(__file__).resolve().parents[1]/'regions/southport/london-square/prezzo/scripts'
        code=f'import sys; sys.path.insert(0,{str(scripts)!r})\n'+'''
import bpy
from mathutils import Matrix
from surface_cleanup import clean
for angle in [0, .61]:
    m=bpy.data.meshes.new('overlapping patches')
    vertices=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(.5,0,0),(1.5,0,0),(1.5,1,0),(.5,1,0)]
    m.from_pydata(vertices,[],[(0,1,2,3),(4,5,6,7)])
    for i in range(2):m.materials.append(bpy.data.materials.new('owner'+str(i)))
    m.polygons[1].material_index=1
    m.transform(Matrix.Rotation(angle,4,'X'));m.update()
    assert clean(m)>0
    assert abs(sum(f.area for f in m.polygons)-1.5)<1e-6
    assert abs(sum(f.area for f in m.polygons if f.material_index==0)-1)<1e-6
    assert abs(sum(f.area for f in m.polygons if f.material_index==1)-.5)<1e-6
    assert all(f.normal.z>.8 for f in m.polygons)
    assert clean(m)==0
# Adjacent and opposite-facing surfaces must remain intact.
m=bpy.data.meshes.new('separate ownership')
m.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(2,0,0),(2,1,0)],[],[(0,1,2,3),(1,4,5,2),(3,2,1,0)])
m.update();assert clean(m)==0
assert abs(sum(f.area for f in m.polygons)-3)<1e-6
print('Surface ownership regression passed')
'''
        result=subprocess.run(['blender','-b','--factory-startup','--threads','2','--python-exit-code','1','--python-expr',code],capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
