"""Export the prepared master without modifying its Blender file or textures.

Material preparation belongs to build_memorial.py, inside the master stage.
The local reference photographs are never embedded in either model format.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import obelisk_surfaces
import exterior_weathering
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
scene=bpy.context.scene
material_count=json.loads((ROOT/'research/portable_materials.json').read_text())['base_color_maps']

# Convert the few small labels for the export only; the .blend retains curves.
bpy.ops.object.select_all(action='DESELECT')
fonts=[o for o in scene.objects if o.type=='FONT']
for o in fonts:o.select_set(True)
if fonts:
    bpy.context.view_layer.objects.active=fonts[0];bpy.ops.object.convert(target='MESH')

def export(path,collections):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in scene.objects:
        if ob.type=='MESH' and any(c.name in collections for c in ob.users_collection):ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,
                             export_extras=True,export_cameras=False,export_lights=False,export_texcoords=True)
    print('EXPORTED',path.name,path.stat().st_size,flush=True)

parts={
 'obelisk.glb':['01 Obelisk exterior'],
 'colonnade-north-east.glb':['02 North-east colonnade exterior'],
 'colonnade-south-west.glb':['03 South-west colonnade exterior'],
 'clustered-lamps.glb':['04 Clustered lamp standards — placement provisional']
}
all_collections=[c.name for c in scene.collection.children if c.name[:2] in ('00','01','02','03','04')]
export(ROOT/'models/london-square-exterior.glb',all_collections)
for filename,collections in parts.items():export(ROOT/'models'/filename,collections)
(ROOT/'research/material_export.json').write_text(json.dumps({
 'base_color_maps':material_count,'normal_map':'textures/portland-micro-normal.png',
 'texture_size':[512,512],'projection':'1 metre box projection',
 'reference_photographs_embedded':False,'blender_textures_packed':True,
 'authored_obelisk_surfaces':obelisk_surfaces.report(),
 'exports':['london-square-exterior.glb']+list(parts),
 'status':'Exterior research study; geometry confidence recorded in modelling_spec.json'
},indent=2)+'\n')
