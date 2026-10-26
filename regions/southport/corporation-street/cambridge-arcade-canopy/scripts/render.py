from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/canopy.blend'));s=bpy.context.scene;s.camera.location=(-163,-130,3);target=Vector((-160,-90,7));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=30;s.render.filepath=str(R/'renders/arcade.png');bpy.ops.render.render(write_still=True)
