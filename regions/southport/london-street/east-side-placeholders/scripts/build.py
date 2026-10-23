"""11–21 London Street: staged replacements of the three context boxes."""
import json
import os
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.unit_settings.system='METRIC'
sys.path.insert(0,str(ROOT/'scripts'))
from facades import Facade
import william_hill, kba, myers
for block,module,part in zip(D['blocks'],[william_hill,kba,myers],['william-hill','kba','myers']):
    collection=bpy.data.collections.new(part);s.collection.children.link(collection)
    module.build(Facade(block,D['ground_z'],collection))
s.render.engine='CYCLES'
s.cycles.samples=16
s.world=s.world or bpy.data.worlds.new('World')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'))
sun.data.energy=2.5
sun.rotation_euler=(.6,-.4,-.7)
s.collection.objects.link(sun)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
cam.data.type='ORTHO'
s.collection.objects.link(cam)
s.camera=cam
s.render.resolution_x=1400
s.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/east-side-placeholders.blend'))
