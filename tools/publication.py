"""Local viewer package contract, georeferencing and GLB inspection."""
import io
import json
import math
from pathlib import Path
import struct

import numpy as np
from PIL import Image
from check_lods import array, matrix, read_glb


def load_publication(path):
    spec = json.loads(Path(path).read_text())
    if spec.get('schema_version') != 1 or set(spec.get('levels', {})) != {'detail','walk','district'}:
        raise ValueError('Publication requires detail, walk and district levels')
    ids = [p['id'] for p in spec['parts']]
    if len(ids) != len(set(ids)) or any(not p or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in p) for p in ids):
        raise ValueError('Part IDs must be unique path-safe names')
    if len({p['collection'] for p in spec['parts']}) != len(ids):
        raise ValueError('Each export collection must belong to exactly one part')
    if spec['coordinates']['frame'] not in {'site','east-north'}:
        raise ValueError('Declare the asset coordinate frame')
    for excluded in spec.get('excluded_collections',[]):
        if not excluded.get('name') or not excluded.get('reason'):
            raise ValueError('Excluded collections require a name and reason')
    for rule in spec['rules']:
        import re
        re.compile(rule['match'])
        for name in ('walk','district'):
            action = rule[name]
            if action.get('strategy') not in {'keep','omit','replace','generator','decimate'} or not action.get('reason'):
                raise ValueError('Every rule/level needs a supported strategy and a reason')
            if action['strategy'] not in {'keep','omit'}:
                if not isinstance(action.get('bake'),bool):
                    raise ValueError('Explicit bake decision required')
                if action['bake']:
                    for key in ('cage_extrusion_m','max_sampled_error_m'):
                        if not math.isfinite(action.get(key,0)) or action.get(key,0)<=0:
                            raise ValueError('Positive projection/error limits required')
    return spec


def east_north_offset(origin, position):
    """WGS84 ECEF projected into a local ENU frame; metres, no map projection drift."""
    def ecef(lat,lon):
        lat,lon=map(math.radians,(lat,lon));a=6378137.;e2=6.69437999014e-3
        n=a/math.sqrt(1-e2*math.sin(lat)**2)
        return np.array([n*math.cos(lat)*math.cos(lon),n*math.cos(lat)*math.sin(lon),n*(1-e2)*math.sin(lat)])
    d=ecef(*position)-ecef(*origin);lat,lon=map(math.radians,origin)
    east=float(d@np.array([-math.sin(lon),math.cos(lon),0]))
    north=float(d@np.array([-math.sin(lat)*math.cos(lon),-math.sin(lat)*math.sin(lon),math.cos(lat)]))
    return east,north


def inspect_glb(path):
    doc,binary=read_glb(Path(path));points=[];placed=0
    unique=sum(doc['accessors'][p['indices']]['count']//3 for m in doc.get('meshes',[]) for p in m['primitives'])
    def visit(index,parent):
        nonlocal placed
        node=doc['nodes'][index];transform=parent@matrix(node)
        if 'mesh' in node:
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                if primitive.get('mode',4)!=4:raise ValueError('Only triangle primitives may be published')
                attrs=primitive['attributes']
                if not {'POSITION','NORMAL'}<=attrs.keys():raise ValueError('Missing positions or normals')
                p=array(doc,binary,attrs['POSITION']);indices=array(doc,binary,primitive['indices']).ravel()
                if len(indices)%3 or (len(indices) and indices.max()>=len(p)):raise ValueError('Bad indices')
                if not np.isfinite(p).all():raise ValueError('Invalid vertex positions')
                placed+=len(indices)//3
                points.append((transform@np.column_stack([p,np.ones(len(p))]).T).T[:,:3])
        for child in node.get('children',[]):visit(child,transform)
    for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,np.eye(4))
    if not points:raise ValueError('Empty published part')
    vertices=np.concatenate(points);sizes=[];image_bytes=0;gpu_images=0
    for image in doc.get('images',[]):
        if 'uri' in image:raise ValueError('Publication GLBs must embed textures')
        view=doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
        with Image.open(io.BytesIO(binary[start:start+view['byteLength']])) as texture:
            sizes.append(list(texture.size));gpu_images+=texture.width*texture.height*4*4/3;texture.verify()
        image_bytes+=view['byteLength']
    return {'bounds':[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()],
            'triangles':int(placed),'uniqueTriangles':int(unique),'textureDimensions':sizes,
            'imageBytes':image_bytes,'gpuBytesEstimate':int(len(binary)-image_bytes+gpu_images),
            'bytes':Path(path).stat().st_size}


def resize_glb_textures(path, maximum):
    """Repack embedded buffers after resizing images; do not retain old image bytes."""
    doc,binary=read_glb(Path(path));replacements={}
    normal_images=set()
    for mat in doc.get('materials',[]):
        if 'normalTexture' in mat:normal_images.add(doc['textures'][mat['normalTexture']['index']]['source'])
    for i,image in enumerate(doc.get('images',[])):
        view=doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
        with Image.open(io.BytesIO(binary[start:start+view['byteLength']])) as original:
            if max(original.size)<=maximum:continue
            size=tuple(max(1,round(n*maximum/max(original.size))) for n in original.size)
            resized=original.resize(size,Image.Resampling.LANCZOS)
            if i in normal_images:
                rgb=np.asarray(resized.convert('RGB'),dtype=float)/127.5-1
                rgb/=np.maximum(np.linalg.norm(rgb,axis=2,keepdims=True),1e-8)
                resized=Image.fromarray(np.clip(np.rint((rgb+1)*127.5),0,255).astype('uint8'))
            stream=io.BytesIO();resized.save(stream,format='PNG')
            replacements[image['bufferView']]=stream.getvalue();image['mimeType']='image/png'
    if not replacements:return
    chunks=bytearray()
    for i,view in enumerate(doc['bufferViews']):
        while len(chunks)%4:chunks.append(0)
        oldstart=view.get('byteOffset',0)
        data=replacements.get(i,binary[oldstart:oldstart+view['byteLength']])
        view['byteOffset']=len(chunks);view['byteLength']=len(data);chunks.extend(data)
    doc['buffers'][0]['byteLength']=len(chunks)
    while len(chunks)%4:chunks.append(0)
    encoded=json.dumps(doc,separators=(',',':')).encode()
    encoded+=b' '*((-len(encoded))%4)
    header=struct.pack('<4sII',b'glTF',2,12+8+len(encoded)+8+len(chunks))
    Path(path).write_bytes(header+struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(chunks),b'BIN\0')+chunks)
