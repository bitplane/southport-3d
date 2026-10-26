from pathlib import Path
import bpy
r=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(r/'models/foreshore.blend'));bpy.context.scene.render.filepath=str(r/'renders/overview.png');bpy.ops.render.render(write_still=True)
