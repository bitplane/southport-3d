"""Build one independently streamed pier section."""
import os,sys,json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from shapes import create
from southport3d.geometry import Mesh

def run(root):
    config=json.loads((root/'research/section.json').read_text())
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC'
    cols={}
    for part in ['deck','structure','fittings']:
        c=bpy.data.collections.new(part);scene.collection.children.link(c);cols[part]=c
    colours={'glass':(.28,.40,.43),'roof':(.25,.31,.29),'gold':(.45,.31,.08),'stone':(.42,.40,.34),'blue':(.035,.07,.12),'ivory':(.78,.76,.62),'yellow':(.70,.57,.08),'dark':(.028,.025,.022),'rail':(.25,.19,.13),'timber':(.20,.18,.14),'plank-long':(.33,.30,.24),'plank-cross':(.35,.31,.25)}
    mats={}
    for key,col in colours.items():
        m=bpy.data.materials.new('Pier '+key);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.8;mats[key]=m
        if key.startswith('plank'):
            n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(root/'textures/deck.png'));n.image.pack();m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
    groups={}
    for row in create(config).items:
        cat='fine' if row['name'].startswith('fine ') else row['name'].split()[0]
        key=(row['part'],row['material'],cat)
        mesh=groups.setdefault(key,Mesh('Pier '+row['part']+' '+cat+' '+row['material']))
        mesh.add(row['vertices'],[tuple(range(len(row['vertices'])))])
    for (part,mat,cat),mesh in groups.items():
        ob=mesh.finish([mats[mat]],cols[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Metric')
        for face in ob.data.polygons:
            axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
            for li in face.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                if mat=='plank-long':uv.data[li].uv=(v.y/1.2,v.x/2.4)
                elif mat=='plank-cross':uv.data[li].uv=(v.x/1.2,v.y/2.4)
                else:uv.data[li].uv=(v[axes[0]],v[axes[1]])
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.world=scene.world or bpy.data.worlds.new('World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.8,1)
    light=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));light.data.energy=2.3;light.rotation_euler=(.5,-.4,-.7);scene.collection.objects.link(light)
    camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
    camera.location=(45,-65,40);camera.rotation_euler=(Vector((45,0,2))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=105
    scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    bpy.ops.wm.save_as_mainfile(filepath=str(root/'models/pier.blend'))
