from pathlib import Path
import bpy,math,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
s=bpy.context.scene
selected=set(sys.argv[sys.argv.index('--final')+1:]) if '--final' in sys.argv else set()
for name,x,scale in [('duke',-660,330),('south',-380,390),('garden',-185,150),('central',-20,410),('north',405,400)]:
 for angle in ['plan','oblique']:
  if selected and name+'-'+angle not in selected:continue
  target=Vector((x,15,0));pos=Vector((x,15,500)) if angle=='plan' else Vector((x-125,-225,260))
  s.camera.location=pos;s.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
  s.render.filepath=str(ROOT/'renders'/(name+'-'+angle+'.png'));bpy.ops.render.render(write_still=True)
# Optional assembled comparisons use the independently built pavilion master.
# Build both assets first; the normal ground-only views still work without it.
combined={'garden-matched-plan','garden-fountain-detail','garden-3d-a','garden-3d-b','garden-street','garden-gate'}
if not selected or selected.intersection(combined):
 source=ROOT.parents[1]/'build/southport.lord-street.town-hall-gardens-pavilions/models/pavilions.blend'
 if source.exists():
  with bpy.data.libraries.load(str(source),link=False) as (contents,loaded):
   loaded.collections=[n for n in ('north','south') if n in contents.collections]
  for collection in loaded.collections:s.collection.children.link(collection)
  centre=Vector((-185.7,-2.5,0))
  for name,pos,scale in [('garden-matched-plan',(-185.7,-2.5,400),115),('garden-fountain-detail',(-185.7,-2.5,400),27),('garden-3d-a',(-255,-75,115),115),('garden-3d-b',(-117,70,115),115),('garden-street',(-160,3,2.2),0),('garden-gate',(-160.9,28.5,1.7),0)]:
   if selected and name not in selected:continue
   s.camera.location=pos
   if name in ('garden-matched-plan','garden-fountain-detail'):
    s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;s.camera.rotation_euler=(0,0,-math.radians(43.5293))
   else:
    target=Vector((-160.9,16.4,1.9) if name=='garden-gate' else (-185.7,-2.5,1 if name=='garden-street' else 0))
    s.camera.rotation_euler=(target-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    s.camera.data.type='PERSP' if name in ('garden-street','garden-gate') else 'ORTHO'
    if name in ('garden-street','garden-gate'):s.camera.data.lens=35
    else:s.camera.data.ortho_scale=scale
   s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
