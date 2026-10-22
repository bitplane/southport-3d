"""Export the exterior master without camera or lights."""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'models/london-street-18.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(ROOT / 'models/london-street-18.glb'),
    export_format='GLB', use_selection=True, export_tangents=True,
)
