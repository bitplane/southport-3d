from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bhf.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('building',(-42,3,22),(-64,-34,6.5),43),('front',(-63.74,4,7),(-63.74,-24,6.5),29),('entrance',(-58,-13,5),(-62.7,-24.2,2.8),10),('roof',(-38,-10,49),(-64,-46,12),56),('roof-rear',(-36,-86,37),(-62,-59,13),30),('roof-plant',(-44,-79,24),(-58,-65,14),15),('roof-plan',(-63.7,-47,70),(-63.7,-47,13),72),('upper-windows',(-60,-16,11),(-63,-23.6,9.1),7),('entrance-detail',(-59,-18,2.9),(-62.7,-24.5,3.2),7)]:
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
