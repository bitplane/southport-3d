"""Bake procedural stone into portable PBR maps and export the editable study.

Run after build_memorial.py. Original procedural nodes remain in each material.
The local reference photographs are never embedded in either model format.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import obelisk_surfaces
import exterior_weathering
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
scene=bpy.context.scene
scene.cycles.samples=1
stone_mats=[m for m in bpy.data.materials if m.use_nodes and not m.get('portable_surface_family') and any(n.type=='TEX_NOISE' for n in m.node_tree.nodes)]
material_count=len(stone_mats)
if '--reuse-baked' in sys.argv:stone_mats=[]
textures=ROOT/'textures';textures.mkdir(exist_ok=True)
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,-100))
plane=bpy.context.object;plane.name='Temporary material bake plane'
scene.render.bake.use_clear=True;scene.render.bake.margin=4
normal_image=None

def bake_image(mat,name,kind):
    image=bpy.data.images.new(name,width=512,height=512,alpha=False)
    image.colorspace_settings.name='Non-Color' if kind=='NORMAL' else 'sRGB'
    target=mat.node_tree.nodes.new('ShaderNodeTexImage');target.image=image
    mat.node_tree.nodes.active=target
    for node in mat.node_tree.nodes:node.select=node==target
    plane.data.materials.clear();plane.data.materials.append(mat)
    bpy.context.view_layer.objects.active=plane;plane.select_set(True)
    bpy.ops.object.bake(type=kind)
    image.filepath_raw=str(textures/(name+'.png'));image.file_format='PNG';image.save()
    return image,target

for i,mat in enumerate(stone_mats):
    nt=mat.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    if normal_image is None:
        normal_image,normal_node=bake_image(mat,'portland-micro-normal','NORMAL')
        nt.nodes.remove(normal_node)
    source_link=bsdf.inputs['Base Color'].links[0]
    color_socket=source_link.from_socket
    emission=nt.nodes.new('ShaderNodeEmission');nt.links.new(color_socket,emission.inputs['Color'])
    nt.links.new(emission.outputs[0],out.inputs['Surface'])
    image,node=bake_image(mat,'stone-base-'+str(i+1).zfill(2),'EMIT')
    nt.links.new(bsdf.outputs['BSDF'],out.inputs['Surface']);nt.nodes.remove(emission)
    # Keep editable procedural nodes, but drive the active shader with baked maps.
    nt.links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
    normal_node=nt.nodes.new('ShaderNodeTexImage');normal_node.image=normal_image
    normal_node.label='Baked procedural microrelief, 1 metre tile'
    convert=nt.nodes.new('ShaderNodeNormalMap');convert.inputs['Strength'].default_value=.65
    nt.links.new(normal_node.outputs['Color'],convert.inputs['Color']);nt.links.new(convert.outputs['Normal'],bsdf.inputs['Normal'])
    mat['texture_provenance']='Blender Cycles bake of authored procedural stone; no source photography'
    print('BAKED',mat.name,flush=True)
bpy.data.objects.remove(plane,do_unlink=True)

# Deterministic box projection, in metres. It preserves material continuity
# between ashlar blocks and exports directly as an ordinary glTF UV set.
for ob in scene.objects:
    if ob.type!='MESH':continue
    if ob.get('authored_surface_uv'):continue
    mesh=ob.data
    uv=mesh.uv_layers.active or mesh.uv_layers.new(name='Metre-scale stone UV')
    for poly in mesh.polygons:
        n=poly.normal;axis=max(range(3),key=lambda j:abs(n[j]))
        for li in poly.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co
            if axis==2:u,v=p.x,p.y
            elif axis==1:u,v=p.x,p.z
            else:u,v=p.y,p.z
            if n[axis]<0:u=-u
            uv.data[li].uv=(u,v)

exterior_weathering.apply(scene)
scene.cycles.samples=72
scene['materials']='Portable baked procedural Portland stone PBR maps; original nodes retained'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))

# Convert the few small labels for the export only; the .blend retains curves.
bpy.ops.object.select_all(action='DESELECT')
fonts=[o for o in scene.objects if o.type=='FONT']
for o in fonts:o.select_set(True)
if fonts:
    bpy.context.view_layer.objects.active=fonts[0];bpy.ops.object.convert(target='MESH')

def export(path,collections):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in scene.objects:
        if ob.type=='MESH' and any(c.name in collections for c in ob.users_collection):ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,
                             export_extras=True,export_cameras=False,export_lights=False,export_texcoords=True)
    print('EXPORTED',path.name,path.stat().st_size,flush=True)

parts={
 'obelisk.glb':['01 Obelisk exterior'],
 'colonnade-north-east.glb':['02 North-east colonnade exterior'],
 'colonnade-south-west.glb':['03 South-west colonnade exterior'],
 'clustered-lamps.glb':['04 Clustered lamp standards — placement provisional']
}
all_collections=[c.name for c in scene.collection.children if c.name[:2] in ('00','01','02','03','04')]
export(ROOT/'models/london-square-exterior.glb',all_collections)
for filename,collections in parts.items():export(ROOT/'models'/filename,collections)
(ROOT/'research/material_export.json').write_text(json.dumps({
 'base_color_maps':material_count,'normal_map':'textures/portland-micro-normal.png',
 'texture_size':[512,512],'projection':'1 metre box projection',
 'reference_photographs_embedded':False,'blender_textures_packed':True,
 'authored_obelisk_surfaces':obelisk_surfaces.report(),
 'exports':['london-square-exterior.glb']+list(parts),
 'status':'Exterior research study; geometry confidence recorded in modelling_spec.json'
},indent=2)+'\n')
