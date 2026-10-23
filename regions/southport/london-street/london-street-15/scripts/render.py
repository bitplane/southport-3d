"""Review the street front, gable, north bay, side alley and estimated rear."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'models/london-street-15.blend'))
s = bpy.context.scene
for name, position, target, scale in [
        ('front', (-20, -47.2, 6), (7.5, -47.2, 6), 13),
        ('overview', (-12, -30, 22), (14, -48, 4), 30),
        ('alley', (-8, -62, 3), (12, -50.5, 3.5), 14),
        ('roof', (-6, -66, 26), (13, -46, 6), 26),
        ('shop', (-12, -44, 2.4), (7.5, -47.4, 2.2), 8)]:
    s.camera.location = position
    s.camera.rotation_euler = (Vector(target) - s.camera.location).to_track_quat('-Z', 'Y').to_euler()
    s.camera.data.ortho_scale = scale
    s.render.filepath = str(ROOT / 'renders' / (name + '.png'))
    bpy.ops.render.render(write_still=True)
