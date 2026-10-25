from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/marine-way-bridge.blend'));bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:ob.select_set(ob.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/marine-way-bridge.glb'),export_format='GLB',use_selection=True,export_tangents=True)
