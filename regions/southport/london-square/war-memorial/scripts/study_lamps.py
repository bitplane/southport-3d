"""Render both lamp types independently, with no master-scene changes."""
from pathlib import Path
import sys,json
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import ornamental_lamps
from geometry import Mesh
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48
scene.cycles.use_denoising=True;scene.unit_settings.system='METRIC'
materials=[]
for name,c,rough in [('Black paint',(.035,.045,.045),.38),('Ivory paint',(.64,.66,.61),.42),
                       ('Opaque globe',(.77,.78,.64),.31),('Study floor',(.20,.22,.23),.85)]:
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*c,1);mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*c,1)
    bsdf.inputs['Roughness'].default_value=rough;materials.append(mat)
items=[]
for name,m,x in [('Single',ornamental_lamps.short_standard(),-1.35),
                  ('Cluster',ornamental_lamps.clustered_standard(),1.25)]:
    ob=m.finish(materials[:3],scene.collection,smooth=True);ob.location.x=x
    items.append({'type':name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),
                  'z_range_m':[min(v.co.z for v in ob.data.vertices),max(v.co.z for v in ob.data.vertices)]})
m=Mesh('Single lamp stone support');m.box((-1.35,0,.235),(1.42,1.06,.49));m.finish([materials[1]],scene.collection,.003)
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(materials[3])
sun_data=bpy.data.lights.new('Sun','SUN');sun_data.energy=2.8;sun_data.angle=.10
sun=bpy.data.objects.new('Sun',sun_data);scene.collection.objects.link(sun)
sun.rotation_euler=Vector((.55,.75,-1)).to_track_quat('-Z','Y').to_euler()
scene.world=bpy.data.worlds.new('Study world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.48
scene.view_settings.view_transform='AgX'
camdata=bpy.data.cameras.new('Study camera');camdata.type='ORTHO'
cam=bpy.data.objects.new('Study camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
views=[('lamps-0.5',(9,-16,7),(.15,0,2.8),7.4,1600,1300),
       ('cluster-head-0.5',(4.8,-6,5.4),(1.25,0,4.67),2.75,1500,1300),
       ('single-lamp-foot-0.5',(.8,-4,1.9),(-1.35,0,.88),1.52,1400,1200)]
for name,pos,target,scale,w,h in views:
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.ortho_scale=scale;scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'renders/studies'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
(ROOT/'research/lamp_study.json').write_text(json.dumps(items,indent=2)+'\n')
print('LAMP_STUDY_COMPLETE',json.dumps(items),flush=True)
