from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/building.blend'));s=bpy.context.scene
views=[('entrance',(455,20,5),(455,-10,2.5),12),('service',(403,-89,11),(450,-89,4),38),('roof',(500,20,62),(455,-22,19),50),('garden-oblique',(520,-55,12),(462,-89,4),42),('garden',(520,-89,7),(462,-89,4),38),('front-oblique',(408,38,15),(455,-15,10),45),('street',(455,65,14),(455,-10,10),40),('orbit',(520,28,80),(455,-48,9),100),('rear',(390,-160,65),(455,-63,8),100)]
# Review-only neutral plane makes the estimated pavement contact visible.
bpy.ops.mesh.primitive_plane_add(size=250,location=(455,-55,.48));ground=bpy.context.object;ground.name='Review only ground'
mat=bpy.data.materials.new('Review pavement');mat.diffuse_color=(.36,.36,.34,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.36,.36,.34,1);ground.data.materials.append(mat)
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 ground.location.z=.72 if name=='garden' else .48
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;(ROOT/'renders').mkdir(exist_ok=True);s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
