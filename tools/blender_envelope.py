"""Bake explicitly authored surface envelopes into bounded, shared part atlases.

Input topology is independent of source detail. Receivers have split corners so
cages project along each face normal rather than rounding building corners.
"""
import importlib
import json
import math
import re
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


def receiver(name,surfaces,size,rects=None):
    rects=pack(surfaces,*size) if rects is None else rects;verts=[];faces=[];uvs=[]
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
    if any(poly.area<1e-10 for poly in mesh.polygons):raise ValueError('Degenerate envelope triangle: '+name)
    return ob,rects


def bake(sources,low,size,rects,dest,cage,faces):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
    scene.render.bake.use_selected_to_active=True;scene.render.bake.use_cage=True
    scene.render.bake.cage_extrusion=cage;scene.render.bake.max_ray_distance=cage*2
    cage_object=None
    if any('cage_m' in face for face in faces):
        cage_mesh=low.data.copy();cage_object=bpy.data.objects.new(low.name+' projection cage',cage_mesh)
        scene.collection.objects.link(cage_object);cage_object.hide_render=True
        for vertex in cage_mesh.vertices:
            distance=faces[vertex.index//4].get('cage_m',cage)
            if not 0<distance<=cage:raise ValueError('Per-face cage must be positive and bounded by the part cage')
            vertex.co+=low.data.vertices[vertex.index].normal*distance
        cage_mesh.update();scene.render.bake.cage_object=cage_object
    else:scene.render.bake.cage_object=None
    scene.render.bake.margin=12;scene.render.bake.use_clear=True
    scene.render.bake.normal_space='TANGENT';scene.render.bake.normal_r='POS_X';scene.render.bake.normal_g='POS_Y';scene.render.bake.normal_b='POS_Z'
    scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
    mat=bpy.data.materials.new(low.name+' atlas');mat.use_nodes=True;low.data.materials.append(mat)
    nt=mat.node_tree;shader=nt.nodes.get('Principled BSDF');shader.inputs['Metallic'].default_value=0
    maps={};checks={}
    mask=np.zeros((size[1],size[0]),dtype=bool)
    for x,y,w,h in rects.values():mask[y+1:y+h-1,x+1:x+w-1]=True
    if not mask.any():raise ValueError('Atlas has no testable receiver pixels')
    for label,kind in [('base-color','DIFFUSE'),('normal','NORMAL'),('roughness','ROUGHNESS')]:
        # Supersample before area averaging: subpixel mullions and glyph strokes
        # must fade consistently rather than disappear according to sample phase.
        supersample=4
        im=bpy.data.images.new(low.name+' '+label,width=size[0]*supersample,height=size[1]*supersample,alpha=True)
        im.colorspace_settings.name='sRGB' if label=='base-color' else 'Non-Color'
        node=nt.nodes.new('ShaderNodeTexImage');node.image=im;nt.nodes.active=node
        for n in nt.nodes:n.select=n==node
        print('ENVELOPE_BAKE',low.name,label,size,flush=True)
        select(*sources,low);bpy.ops.object.bake(type=kind)
        pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
        raw=pixels.reshape(size[1]*supersample,size[0]*supersample,4)
        raw_invalid=0.
        if label=='normal':
            raw_mask=np.repeat(np.repeat(mask,supersample,axis=0),supersample,axis=1)
            lengths=np.linalg.norm(raw[:,:,:3][raw_mask]*2-1,axis=1)
            raw_invalid=float(np.mean(abs(lengths-1)>.2))
            if raw_invalid>.01:
                bad=[]
                for index,(x,y,w,h) in rects.items():
                    patch=raw[(y+1)*supersample:(y+h-1)*supersample,(x+1)*supersample:(x+w-1)*supersample,:3]
                    if patch.size:bad.append((float(np.mean(abs(np.linalg.norm(patch*2-1,axis=2)-1)>.2)),index))
                raise ValueError(f'{low.name}: invalid source normal pixels {raw_invalid:.1%}; worst islands {sorted(bad,reverse=True)[:8]}')
        rgba=raw.reshape(size[1],supersample,size[0],supersample,4).mean(axis=(1,3))
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
            checks[label]['raw_invalid_normal_fraction']=raw_invalid
            lengths=np.linalg.norm(rgba[:,:,:3][mask]*2-1,axis=1)
            invalid=float(np.mean(abs(lengths-1)>.2));checks[label]['invalid_normal_fraction']=invalid
            if invalid>.01:raise ValueError(f'{low.name}: invalid normal pixels {invalid:.1%}')
        im.filepath_raw=str(dest/(label+'.png'));im.file_format='PNG';im.save();maps[label]=node
    nt.links.new(maps['base-color'].outputs['Color'],shader.inputs['Base Color'])
    nt.links.new(maps['roughness'].outputs['Color'],shader.inputs['Roughness'])
    normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map=low.data.uv_layers.active.name
    nt.links.new(maps['normal'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    if cage_object is not None:
        scene.render.bake.cage_object=None
        bpy.data.objects.remove(cage_object,do_unlink=True);bpy.data.meshes.remove(cage_mesh)
    return checks


def build(spec,asset,dest,sources):
    recipe=spec['district_envelope'];sys.path.insert(0,str(asset/'scripts'))
    module,func=recipe['generator'].split(':');surfaces=getattr(importlib.import_module(module),func)(asset)
    expected={p['id'] for p in spec['parts']}
    if set(surfaces)!=expected:raise ValueError('Envelope must replace every streaming part')
    outputs={};report={'reason':recipe['reason'],'parts':{},'source_meshes':sum(len(v) for v in sources.values())}
    report['source_omissions']=[]
    for omission in recipe.get('source_omissions',[]):
        pattern=re.compile(omission['match']);matches=[o.name for objects in sources.values() for o in objects if pattern.search(o.name)]
        if not matches:raise ValueError('Source omission matches no objects: '+omission['match'])
        sources={key:[o for o in objects if not pattern.search(o.name)] for key,objects in sources.items()}
        report['source_omissions'].append(dict(omission,objects=matches))

    # Preflight every receiver and source material before the first costly bake.
    pending=[]
    for part,faces in surfaces.items():
        config=recipe['parts'][part];size=config['atlas']
        selected=[obj for key in config.get('source_parts',[part]) for obj in sources[key]]
        for obj in selected:validate_materials(obj)
        # Repeated surfaces deliberately share one sampled appearance. Bake only
        # their representative, never overlapping UV islands from many instances.
        unique=[];keys={};indices=[]
        for i,face in enumerate(faces):
            key=face.get('atlas_key',f'unique:{i}')
            if key not in keys:keys[key]=len(unique);unique.append(face)
            else:
                original=unique[keys[key]]
                a,b=list(map(Vector,face['vertices'])),list(map(Vector,original['vertices']))
                if any(abs((a[j]-a[k]).length-(b[j]-b[k]).length)>1e-5 for j in range(4) for k in range(j)):
                    raise ValueError('Shared atlas key has incompatible geometry: '+key)
            indices.append(keys[key])
        target,rects=receiver('Bake '+part,unique,size)
        low,all_rects=receiver('District '+part,faces,size,{i:rects[j] for i,j in enumerate(indices)})
        if triangles(low)>config['max_triangles']:raise ValueError('Envelope exceeds fixed triangle budget: '+part)
        pending.append((part,faces,config,selected,unique,target,low,rects,all_rects))

    for part,faces,config,selected,unique,target,low,rects,all_rects in pending:
        size=config['atlas']
        folder=dest/'maps'/'district'/part;folder.mkdir(parents=True)
        checks=bake(selected,target,size,rects,folder,config['cage_m'],unique)
        low.data.materials.append(target.data.materials[0]);data=target.data
        bpy.data.objects.remove(target,do_unlink=True);bpy.data.meshes.remove(data)
        report['parts'][part]={'triangles':triangles(low),'atlas':size,'faces':[f['name'] for f in faces],
            'unique_atlas_surfaces':len(unique),'source_parts':config.get('source_parts',[part]),
            'rectangles':all_rects,'bake_checks':checks}
        outputs[part]=[low]
    return outputs,report


class Surfaces:
    """Small authored-surface helpers; no dependency on detailed source topology."""
    def __init__(self, parts, transform=lambda p:p):
        self.result={p:[] for p in parts};self.part=parts[0];self.transform=transform

    def quad(self,name,points,weight=1,cage=None):
        row={'name':name,'vertices':[self.transform(p) for p in points],'weight':weight}
        if cage is not None:row['cage_m']=cage
        self.result[self.part].append(row)

    def triangle(self,name,points,**kwargs):
        # Three nondegenerate quads give each corner a regular rectangular atlas
        # island, avoiding transparent unused halves of triangular UV islands.
        a,b,c=map(Vector,points);mid=(a+b+c)/3
        for i,(p,q,r) in enumerate(((a,b,c),(b,c,a),(c,a,b))):
            self.quad(name+' '+str(i),[p,(p+q)/2,mid,(r+p)/2],**kwargs)

    def box(self,name,a,b,omit=('bottom',),**kwargs):
        x,y,z=a;X,Y,Z=b
        v=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
        for side,ids in [('bottom',(0,3,2,1)),('rear',(0,1,5,4)),('right',(1,2,6,5)),('front',(2,3,7,6)),('left',(3,0,4,7)),('top',(4,5,6,7))]:
            if side not in omit:self.quad(name+' '+side,[v[i] for i in ids],**kwargs)

    def hip(self,name,x0,x1,y0,y1,eave,ridge,axis='x',**kwargs):
        swap=axis=='y'
        if swap:x0,x1,y0,y1=y0,y1,x0,x1
        h=min((x1-x0)*.28,(y1-y0)*.48);cy=(y0+y1)/2
        v=[(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave),(x0+h,cy,ridge),(x1-h,cy,ridge)]
        for i,ids in enumerate([(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]):
            points=[v[k] for k in ids]
            if swap:points=[(y,x,z) for x,y,z in reversed(points)]
            (self.quad if len(points)==4 else self.triangle)(name+' '+str(i),points,**kwargs)
        # Narrow fascia closes the roof edge against its supporting wall.
        for i in range(4):
            j=(i+1)%4;points=[v[j],v[i],(v[i][0],v[i][1],eave-.18),(v[j][0],v[j][1],eave-.18)]
            if swap:points=[(y,x,z) for x,y,z in reversed(points)]
            self.quad(name+' edge '+str(i),points,**kwargs)
