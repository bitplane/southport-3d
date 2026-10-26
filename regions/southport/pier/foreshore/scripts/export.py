from pathlib import Path
import bpy
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'models/foreshore.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'models/foreshore.glb'),export_format='GLB')
