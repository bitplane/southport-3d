"""Isolated shaft inspection; does not overwrite the delivered master."""
from pathlib import Path
import json
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/build_memorial.py'
namespace={'__file__':str(source),'__name__':'shaft_study_builder'}
exec(compile(source.read_text().split('\nsite_context()\n')[0],str(source),'exec'),namespace)
objects=namespace['shaft_masonry'].build(namespace['OBELISK'],namespace['STONE'])
namespace['setup_render']()
scene=bpy.context.scene;scene.cycles.samples=48
bpy.context.view_layer.update()
report=namespace['shaft_masonry'].validate_shaft(scene)
report['nonmanifold_edges']={}
for ob in objects:
    bm=bmesh.new();bm.from_mesh(ob.data)
    count=sum(not e.is_manifold for e in bm.edges);bm.free()
    assert count==0,(ob.name,count)
    report['nonmanifold_edges'][ob.name]=count
sun=bpy.data.objects['Soft afternoon sun']
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.40
for face,position,target,scale in [
    ('se',(0,-8,12.3),(0,-.8,12.3),3.25),
    ('sw',(-8,0,8.5),(-.8,0,8.5),3.25),
    ('corner',(-5,-8,12.0),(0,0,12.0),3.25)]:
    if '--no-render' in sys.argv:break
    scene.camera=namespace['camera']('Shaft '+face,position,target,scale)
    sun.rotation_euler=Vector((.6,.65,-.6)).to_track_quat('-Z','Y').to_euler()
    sun.data.energy=2.8;sun.data.angle=.08
    scene.render.resolution_x=1200;scene.render.resolution_y=1600
    scene.render.filepath=str(ROOT/f'renders/studies/shaft-{face}-0.9.png')
    bpy.ops.render.render(write_still=True)
    print('SHAFT_STUDY_RENDERED',face,flush=True)
(ROOT/'research/shaft-masonry-study.json').write_text(json.dumps(report,indent=2)+'\n')
print('SHAFT_STUDY_COMPLETE',json.dumps(report),flush=True)
