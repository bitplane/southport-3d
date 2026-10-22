from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
bpy.context.scene.render.filepath=str(ROOT/'renders/overview.png');bpy.ops.render.render(write_still=True)
