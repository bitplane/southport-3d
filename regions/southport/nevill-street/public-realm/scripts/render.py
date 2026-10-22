from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'));s=bpy.context.scene
views=[('corridor',(125,85,260),(-5,175,0),310),('plan',(0,176,350),(0,176,0),400),('monument-seam',(26,15,28),(0,58,0),70),('middle-junctions',(40,125,75),(-2,150,0),125),('upper-nevill',(25,200,45),(-12,238,1),92),('promenade',(38,235,68),(-12,283,2),95),('paving',(-20,64,9),(-5,71,0),17),('crossing',(-5,235,13),(-18,248,2),28)]
for name,pos,target,scale in views:
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
