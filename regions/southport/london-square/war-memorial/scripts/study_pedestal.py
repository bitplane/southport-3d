"""Build only the pedestal assembly and render its two carved faces.

This diagnostic never opens or saves the delivered master scene.
"""
from pathlib import Path
import sys,json
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
checkpoint=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--checkpoint=')),'0.7')
source=ROOT/'scripts/build_memorial.py'
namespace={'__file__':str(source),'__name__':'pedestal_study_builder'}
exec(compile(source.read_text().split('\nsite_context()\n')[0],str(source),'exec'),namespace)
namespace['build_obelisk']();namespace['setup_render']()
scene=bpy.context.scene;scene.cycles.samples=48
sun=bpy.data.objects['Soft afternoon sun']
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
for face,normal in [('SE',(0,-1,0)),('NW',(0,1,0))]:
    if '--no-render' in sys.argv:continue
    if '--debug-nw' in sys.argv and face!='NW':continue
    if '--debug-nw' in sys.argv:bpy.data.objects['Salute laurel wreath — traced continuous surface'].hide_render=True
    cam=namespace['camera']('Pedestal '+face,Vector(normal)*9+Vector((0,0,3.06)),(0,0,3.06),2.9)
    scene.camera=cam
    sun.rotation_euler=Vector((.55,-normal[1]*.65,-.52)).to_track_quat('-Z','Y').to_euler()
    sun.data.energy=2.8;sun.data.angle=.10
    scene.render.resolution_x=1800;scene.render.resolution_y=1400
    suffix='-without-wreath' if '--debug-nw' in sys.argv else ''
    scene.render.filepath=str(ROOT/f'renders/studies/pedestal-{face.lower()}{suffix}-{checkpoint}.png')
    bpy.ops.render.render(write_still=True)
report={'border_meshes':{},'pedestal_channels':bpy.data.objects['Square obelisk pedestal']['masonry_channel_count']}
import bmesh
for ob in bpy.data.objects:
    if 'roundel border' not in ob.name:continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    report['border_meshes'][ob.name]={'vertices':len(bm.verts),'faces':len(bm.faces),
       'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)}
    bm.free()
    assert report['border_meshes'][ob.name]['nonmanifold_edges']==0,ob.name
(ROOT/'research/pedestal-study.json').write_text(json.dumps(report,indent=2)+'\n')
print('PEDESTAL_STUDY_COMPLETE',report,flush=True)
