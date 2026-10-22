"""Render one numeric relief under raking light without changing the scene.

blender -b --factory-startup --threads 12 --python scripts/study_carving.py -- trophy-pelta
"""
import sys,json
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from sculpt_surface import mesh_from_surface,simplify_relief,trim_empty_relief_background
from geometry import Mesh
name=sys.argv[sys.argv.index('--')+1]
checkpoint=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--checkpoint=')),'0.4')
source=ROOT/'research/relief-data'/(name+'.npz')
data=np.load(source);width=float(data['width']);height=float(data['height'])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48
scene.unit_settings.system='METRIC'
mat=bpy.data.materials.new('Carving study limestone');mat.diffuse_color=(.57,.55,.50,1);mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value=(.57,.55,.50,1);bsdf.inputs['Roughness'].default_value=.82
m=mesh_from_surface(source,name+' study')
o=m.finish([mat],scene.collection,smooth=True)
check=simplify_relief(o,source,ratio=.30)
if name in ('cornice-lion','architectural-rosette','frieze-foliage'):
    check['empty_background_faces_removed']=trim_empty_relief_background(o,radial_limit=.087 if name=='architectural-rosette' else None)
(ROOT/'research/relief-data'/(name+'-study-meshcheck.json')).write_text(json.dumps(check,indent=2)+'\n')
back=Mesh('Study backing slab');back.box((0,0,-.018 if name=='architectural-rosette' else -.022),(width+.10,height+.10,.04));back.finish([mat],scene.collection,.002)
camdata=bpy.data.cameras.new('Carving study camera');camdata.type='ORTHO';camdata.ortho_scale=width+.25
cam=bpy.data.objects.new('Carving study camera',camdata);scene.collection.objects.link(cam)
cam.location=(0,0,4);cam.rotation_euler=Vector((0,0,-1)).to_track_quat('-Z','Y').to_euler();scene.camera=cam
sun_data=bpy.data.lights.new('Study raking sun','SUN');sun_data.energy=2.8;sun_data.angle=.10
sun=bpy.data.objects.new('Study raking sun',sun_data);scene.collection.objects.link(sun)
sun.rotation_euler=Vector((.45,-.65,-.8)).to_track_quat('-Z','Y').to_euler()
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1800;scene.render.resolution_y=round(1800*(height+.25)/(width+.25))
scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'renders/studies'/(name+'-'+checkpoint+'.png'))
bpy.ops.render.render(write_still=True)
print('CARVING_STUDY_COMPLETE',name,flush=True)
