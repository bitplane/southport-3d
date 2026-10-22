"""Inspect only obelisk fixture geometry without saving the delivered master."""
from pathlib import Path
import json
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/build_memorial.py'
namespace={'__file__':str(source),'__name__':'obelisk_fixture_study'}
exec(compile(source.read_text().split('\nsite_context()\n')[0],str(source),'exec'),namespace)
namespace['build_obelisk']();namespace['setup_render']()
scene=bpy.context.scene
scene.cycles.samples=48
scene.render.resolution_x=1400;scene.render.resolution_y=1200
bpy.context.view_layer.update()
report=namespace['obelisk_fixtures'].validate_fixtures(scene)
pyramid=next(o for o in scene.objects if o.get('obelisk_part')=='pyramid')
bm=bmesh.new();bm.from_mesh(pyramid.data)
report['pyramid_nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges)
bm.free()
assert report['pyramid_nonmanifold_edges']==0,report
sun=bpy.data.objects['Soft afternoon sun']
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
for name,eye,target,scale in [
    ('tip-se',(-2,-5,19.9),(0,0,19.75),2.25),
    ('tip-nw',(-2,5,19.9),(0,0,19.75),2.25),
    ('lights-se',(3,-6,5.5),(0,-.55,4.61),3.7),
    ('lights-sw',(-6,-3,5.5),(-.55,0,4.61),3.7)]:
    if '--no-render' in sys.argv:break
    sun.rotation_euler=Vector((.5,.7 if eye[1]<0 else -.7,-.65)).to_track_quat('-Z','Y').to_euler()
    sun.data.energy=2.8;sun.data.angle=.10
    scene.camera=namespace['camera']('Obelisk '+name,eye,target,scale)
    scene.render.filepath=str(ROOT/f'renders/studies/obelisk-{name}-0.8.png')
    bpy.ops.render.render(write_still=True)
    print('FIXTURE_STUDY_RENDERED',name,flush=True)
(ROOT/'research/obelisk-fixture-study.json').write_text(json.dumps(report,indent=2)+'\n')
print('OBELISK_FIXTURE_STUDY_COMPLETE',json.dumps(report),flush=True)
