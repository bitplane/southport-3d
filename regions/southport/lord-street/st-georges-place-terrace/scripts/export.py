from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/st-georges-place-terrace.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/st-georges-place-terrace.glb'),export_format='GLB',use_selection=True,export_tangents=True)
