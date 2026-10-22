"""Render a replacement relief without overwriting the checkpoint scene."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from sculpt_surface import mesh_from_surface,simplify_relief
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
scene=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
name='victory' if 'victory' in args else 'mourning'
prefix='Victory Britannia' if name=='victory' else 'Mourning figure'
old=next(o for o in bpy.data.objects if o.name.startswith(prefix))
old.hide_render=True
for obj in bpy.data.objects:
    if obj.name.startswith('PATRIA on lion standard'):obj.hide_render=True
m=mesh_from_surface(ROOT/('research/relief-data/'+name+'.npz'),name.title()+' traced continuous sculpt')
obj=m.finish([bpy.data.materials['Portland limestone 1']],old.users_collection[0],smooth=True)
if 'simplify' in args:simplify_relief(obj,ROOT/('research/relief-data/'+name+'.npz'))
obj.matrix_world=old.matrix_world.copy()
for group in ['00 Site registration and approximate paving','01 Obelisk exterior',
              '03 South-west colonnade exterior' if name=='victory' else '02 North-east colonnade exterior']:
    bpy.data.collections[group].hide_render=True
bpy.data.collections['99 Survey guides — hidden in renders'].hide_render=True
scene.camera=bpy.data.objects['Victory close view' if name=='victory' else 'Mourning close view']
# Directional light from upper left on this NW-facing panel exposes shallow cuts.
sun=bpy.data.objects['Soft afternoon sun']
sun.rotation_euler=Vector((.55,-.65,-.52)).to_track_quat('-Z','Y').to_euler()
sun.data.angle=.09;sun.data.energy=2.8
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
scene.cycles.samples=48
scene.render.resolution_x=1800;scene.render.resolution_y=1400
scene.camera.data.ortho_scale=3.9
scene.render.filepath=str(ROOT/('renders/studies/'+name+'-sculpt.png'))
bpy.ops.render.render(write_still=True)
print('STUDY_RENDER_COMPLETE',flush=True)
