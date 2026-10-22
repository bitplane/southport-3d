"""Isolated surface preflight; leaves delivered master and views untouched."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/build_memorial.py'
namespace={'__file__':str(source),'__name__':'surface_study_builder'}
exec(compile(source.read_text().split('\nsite_context()\n')[0],str(source),'exec'),namespace)
namespace['shaft_masonry'].build(namespace['OBELISK'],namespace['STONE'],namespace['obelisk_surfaces'].shaft_palette())
pyramid=namespace['obelisk_fixtures'].build_pyramid(namespace['OBELISK'],namespace['STONE'][3],namespace['GRILLE_METAL'],namespace['BLACK_IRON'])
namespace['obelisk_surfaces'].apply_pyramid(pyramid)
namespace['setup_render']()
scene=bpy.context.scene
scene.cycles.samples=48
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
sun=bpy.data.objects['Soft afternoon sun']
sun.rotation_euler=Vector((.55,.65,-.52)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=2.8
sun.data.angle=.09
for name,position,target,scale,x,y in [
    ('shaft-sw',(-8,0,6.4),(-.8,0,6.4),3.25,1200,1600),
    ('shaft-se',(0,-8,12.3),(0,-.8,12.3),3.25,1200,1600),
    ('tip-se',(-2,-5,19.9),(0,0,19.75),2.25,1200,1200),
    ('tip-sw',(-5,-2,19.9),(0,0,19.75),2.25,1200,1200)]:
    scene.camera=namespace['camera']('Surface '+name,position,target,scale)
    scene.render.resolution_x=x;scene.render.resolution_y=y
    scene.render.filepath=str(ROOT/f'renders/studies/surface-{name}-0.10.png')
    bpy.ops.render.render(write_still=True)
    print('SURFACE_STUDY_RENDERED',name,flush=True)
print('SURFACE_STUDY_COMPLETE',flush=True)
