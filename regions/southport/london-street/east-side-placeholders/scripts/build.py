"""Placeholder massing on London Street's east side, NatWest to Anchor Street.

Footprints follow map outlines; heights are estimates. These are context
volumes to be replaced by real buildings, not models of them.
"""
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
massing=bpy.data.collections.new('massing')
s.collection.children.link(massing)


def material(name,colour):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    shader=mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value=(*colour,1)
    shader.inputs['Roughness'].default_value=.9
    return mat


# Alternating neutral tones keep neighbouring placeholders distinguishable.
tones=[material('Placeholder massing light',(.55,.53,.50)),material('Placeholder massing dark',(.44,.43,.41))]
for i,block in enumerate(D['blocks']):
    (x0,x1),(y0,y1)=block['x'],block['y']
    # Bury the base slightly so gaps in adjoining ground never show a floating edge.
    bottom,top=D['bury_z'],D['ground_z']+block['height']
    mesh=Mesh('Envelope placeholder '+block['name'])
    mesh.box(((x0+x1)/2,(y0+y1)/2,(bottom+top)/2),(x1-x0,y1-y0,top-bottom))
    obj=mesh.finish([tones[i%2]],massing)
    uv=obj.data.uv_layers.new(name='Metric')
    for face in obj.data.polygons:
        axes=sorted(sorted(range(3),key=lambda k:abs(face.normal[k]))[:2])
        for loop in face.loop_indices:
            v=obj.data.vertices[obj.data.loops[loop].vertex_index].co
            uv.data[loop].uv=(v[axes[0]]/4,v[axes[1]]/4)
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
