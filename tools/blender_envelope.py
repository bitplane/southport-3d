"""Bake explicitly authored surface envelopes into bounded, shared part atlases.

Input topology is independent of source detail. Receivers have split corners so
cages project along each face normal rather than rounding building corners.
"""
import importlib
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from blender_lod import select, validate_materials, triangles


def pack(surfaces, width, height, padding=3):
    """Deterministic shelf packing with aspect-correct rectangles and fixed budget."""
    sizes=[]
    for face in surfaces:
        v=list(map(Vector,face['vertices']))
        w=(v[1]-v[0]).length;h=(v[3]-v[0]).length
        if min(w,h)<1e-6:raise ValueError('Degenerate envelope face: '+face['name'])
        sizes.append((w*face.get('weight',1),h*face.get('weight',1)))
    order=sorted(range(len(sizes)),key=lambda i:(-sizes[i][1],-sizes[i][0],i))
    def attempt(scale):
        x=y=row=0;rects={}
        for i in order:
            w,h=[max(2,math.ceil(n*scale)) for n in sizes[i]]
            W,H=w+2*padding,h+2*padding
            if W>width or H>height:return None
            if x+W>width:x=0;y+=row;row=0
            if y+H>height:return None
            rects[i]=(x+padding,y+padding,w,h);x+=W;row=max(row,H)
        return rects
    lo,hi=0.,max(width,height)
    if attempt(lo) is None:raise ValueError('Too many envelope faces for atlas')
    for _ in range(40):
        mid=(lo+hi)/2
        if attempt(mid) is None:hi=mid
        else:lo=mid
    return attempt(lo)


def receiver(name,surfaces,size):
    rects=pack(surfaces,*size);verts=[];faces=[];uvs=[]
    for i,face in enumerate(surfaces):
        n=len(verts);verts.extend(face['vertices']);faces.append(tuple(range(n,n+4)))
        x,y,w,h=rects[i]
        uvs.extend([(x/size[0],y/size[1]),((x+w)/size[0],y/size[1]),((x+w)/size[0],(y+h)/size[1]),(x/size[0],(y+h)/size[1])])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='Envelope atlas')
    for poly in mesh.polygons:
        for loop in poly.loop_indices:uv.data[loop].uv=uvs[mesh.loops[loop].vertex_index]
    ob=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    return ob,rects


def bake(sources,low,size,rects,dest,cage):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
    scene.render.bake.use_selected_to_active=True;scene.render.bake.use_cage=True
    scene.render.bake.cage_extrusion=cage;scene.render.bake.max_ray_distance=cage*2
    scene.render.bake.margin=12;scene.render.bake.use_clear=True
    scene.render.bake.normal_space='TANGENT';scene.render.bake.normal_r='POS_X';scene.render.bake.normal_g='POS_Y';scene.render.bake.normal_b='POS_Z'
    scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
    mat=bpy.data.materials.new(low.name+' atlas');mat.use_nodes=True;low.data.materials.append(mat)
    nt=mat.node_tree;shader=nt.nodes.get('Principled BSDF');shader.inputs['Metallic'].default_value=0
    maps={};checks={}
    mask=np.zeros((size[1],size[0]),dtype=bool)
    for x,y,w,h in rects.values():mask[y+1:y+h-1,x+1:x+w-1]=True
    for label,kind in [('base-color','DIFFUSE'),('normal','NORMAL'),('roughness','ROUGHNESS')]:
        # Supersample before area averaging: subpixel mullions and glyph strokes
        # must fade consistently rather than disappear according to sample phase.
        supersample=4
        im=bpy.data.images.new(low.name+' '+label,width=size[0]*supersample,height=size[1]*supersample,alpha=True)
        im.colorspace_settings.name='sRGB' if label=='base-color' else 'Non-Color'
        node=nt.nodes.new('ShaderNodeTexImage');node.image=im;nt.nodes.active=node
        for n in nt.nodes:n.select=n==node
        select(*sources,low);bpy.ops.object.bake(type=kind)
        pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
        rgba=pixels.reshape(size[1],supersample,size[0],supersample,4).mean(axis=(1,3))
        if label=='normal':
            vectors=rgba[:,:,:3]*2-1;lengths=np.linalg.norm(vectors,axis=2,keepdims=True)
            rgba[:,:,:3]=(vectors/np.maximum(lengths,1e-8)+1)*.5
        im.scale(*size);im.pixels.foreach_set(rgba.ravel())
        if not np.isfinite(rgba).all():raise ValueError('Non-finite envelope bake')
        covered=rgba[:,:,3]>.5
        coverage=float(covered[mask].mean())
        checks[label]={'receiver_coverage':coverage,'covered_pixels':int(covered.sum())}
        if coverage<.97:raise ValueError(f'{low.name} {label}: missed projection rays ({coverage:.1%} receiver coverage)')
        if label=='normal':
            lengths=np.linalg.norm(rgba[:,:,:3][mask]*2-1,axis=1)
            invalid=float(np.mean(abs(lengths-1)>.2));checks[label]['invalid_normal_fraction']=invalid
            if invalid>.01:raise ValueError(f'{low.name}: invalid normal pixels {invalid:.1%}')
        im.filepath_raw=str(dest/(label+'.png'));im.file_format='PNG';im.save();maps[label]=node
    nt.links.new(maps['base-color'].outputs['Color'],shader.inputs['Base Color'])
    nt.links.new(maps['roughness'].outputs['Color'],shader.inputs['Roughness'])
    normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map=low.data.uv_layers.active.name
    nt.links.new(maps['normal'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    return checks


def build(spec,asset,dest,sources):
    recipe=spec['district_envelope'];sys.path.insert(0,str(asset/'scripts'))
    module,func=recipe['generator'].split(':');surfaces=getattr(importlib.import_module(module),func)(asset)
    expected={p['id'] for p in spec['parts']}
    if set(surfaces)!=expected:raise ValueError('Envelope must replace every streaming part')
    for obj in sources:validate_materials(obj)
    outputs={};report={'reason':recipe['reason'],'parts':{},'source_meshes':len(sources)}
    for part,faces in surfaces.items():
        config=recipe['parts'][part];size=config['atlas'];low,rects=receiver('District '+part,faces,size)
        if triangles(low)>config['max_triangles']:raise ValueError('Envelope exceeds fixed triangle budget: '+part)
        folder=dest/'maps'/'district'/part;folder.mkdir(parents=True)
        checks=bake(sources,low,size,rects,folder,config['cage_m'])
        report['parts'][part]={'triangles':triangles(low),'atlas':size,'faces':[f['name'] for f in faces],'rectangles':rects,'bake_checks':checks}
        outputs[part]=[low]
    return outputs,report
