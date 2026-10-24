"""Overview and oblique checks of the expanded public realm."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
scene=bpy.context.scene
import sys
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,position,target,scale in [
    ('post-office-mouth',(60,-32,12),(68,-18,0),20),
    ('posting-footway',(50,-84,3),(48,-77,1),12),
    ('posting-wall',(37,-81,2.6),(38.2,-76.5,1.7),5),
    ('lord-seam',(-43,-37,18),(-41,-15,0),22),
    ('st-georges-return',(170,-27,17),(146,3,0),50),
    ('sainsbury-crossing',(125,-40,13),(118,-18,0),25),
    ('london-seam',(13,-82,14),(0,-76,0),25),
    ('lord-street-furniture',(-76,-32,12),(-51,-14,1),40),
    ('garden-globe',(-65,-17,3.8),(-62,-12.3,1.8),5),
    ('overview',(205,-242,220),(25,-48,0),285),
    ('gardens',(86,-60,48),(85,0,0),115),
    ('london-street',(45,-175,70),(0,-100,0),130),
    ('crossing-landing',(10,-142,6),(0,-133,0),20),
]:
    if selected and name not in selected:continue
    cam=scene.camera;cam.location=position
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale
    scene.render.filepath=str(ROOT/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
