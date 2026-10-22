"""Modest authored stone staining, portable as glTF vertex colour multipliers.

Broad darker bases and sheltered cornice/parapet streaking follow the saved
2009/2012 views. Individual marks, hue and intensity are interpretations.
No photograph pixels are sampled or embedded. Shared carvings retain one mesh.
"""
import json
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ATTRIBUTE='Exterior weathering'


def aged_material(source):
    name='Exterior aged — '+source.name
    found=bpy.data.materials.get(name)
    if found:return found
    m=source.copy();m.name=name
    nt=m.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    socket=bsdf.inputs['Base Color'];link=socket.links[0].from_socket
    attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name=ATTRIBUTE
    mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY'
    mix.inputs[0].default_value=1
    a=next(s for s in mix.inputs if s.name=='A' and s.type=='RGBA')
    b=next(s for s in mix.inputs if s.name=='B' and s.type=='RGBA')
    result=next(s for s in mix.outputs if s.type=='RGBA')
    nt.links.new(link,a);nt.links.new(attr.outputs['Color'],b);nt.links.new(result,socket)
    m['weathering_attribute']=ATTRIBUTE
    m['weathering_provenance']='Authored broad staining; source photographs remain references only'
    return m


def apply(scene):
    seen=set();records=[]
    for ob in scene.objects:
        if ob.type!='MESH' or not any(c.name[:2] in ('01','02','03') for c in ob.users_collection):continue
        mesh=ob.data
        if mesh.name in seen:continue
        eligible=[i for i,m in enumerate(mesh.materials) if m and
                  m.name.startswith(('Portland limestone','Damp stone','Incised stone'))]
        if not eligible:continue
        seen.add(mesh.name)
        p=np.empty((len(mesh.vertices),3),dtype=np.float32)
        mesh.vertices.foreach_get('co',p.ravel())
        # World heights, while preserving shared-mesh instances. Repeated
        # columns/ornaments therefore have common broad staining, not surveyed
        # individual patina. Long ashlar meshes have continuous local X fields.
        matrix=np.asarray(ob.matrix_world,dtype=np.float32)
        world=p@matrix[:3,:3].T+matrix[:3,3]
        z=world[:,2];u=p[:,0]
        patch=np.clip(.50+.24*np.sin(u*3.17+.4)*np.sin(u*.71+z*2.9)+
                      .16*np.sin(u*8.3+z*.7),0,1)
        lower=np.exp(-np.maximum(z-.30,0)/.46)*(.15+.10*patch)
        is_colonnade=any(c.name[:2] in ('02','03') for c in ob.users_collection)
        if is_colonnade:
            parapet=np.clip((z-5.11)/.40,0,1)*(.07+.15*patch)
            lip=.10*np.exp(-np.abs(z-4.905)/.055)
            d=np.clip(lower+parapet+lip,0,.29)
        else:
            # Pedestal only: shaft and tip already have their own authored maps.
            d=np.clip(lower+.065*np.exp(-np.abs(z-4.12)/.10)*patch,0,.28)
        color=np.ones((len(p),4),dtype=np.float32)
        color[:,:3]=1-d[:,None]*np.array([.87,.94,1.0],dtype=np.float32)
        attr=mesh.color_attributes.get(ATTRIBUTE) or mesh.color_attributes.new(
            name=ATTRIBUTE,type='BYTE_COLOR',domain='POINT')
        attr.data.foreach_set('color',color.ravel())
        mesh.color_attributes.active_color=attr
        for i in eligible:mesh.materials[i]=aged_material(mesh.materials[i])
        ob['weathering_status']='Broad authored exterior patina; fine marks and current condition unverified'
        records.append({'mesh':mesh.name,'vertices':len(p),'minimum_linear_rgb':color[:,:3].min(axis=0).tolist(),
                        'maximum_linear_rgb':color[:,:3].max(axis=0).tolist()})
    report={'status':'Applied; verify COLOR_0 and retained PBR images in exported GLB',
            'attribute':ATTRIBUTE,'method':'Linear vertex-colour multiplication of baked authored stone maps',
            'source_images':['flickr-7465690872.jpg','commons-columns-1.jpg','commons-columns-2.jpg','wmo-Southport_2.jpg'],
            'evidenced':'Darker lower stone, sheltered cornice bands and irregular parapet streaks',
            'not_evidenced':'Exact stain positions, hue/intensity, individual erosion or present-day condition',
            'reference_rgb_embedded':False,'shared_mesh_patina':'Repeated details share representative broad staining',
            'meshes':records}
    (ROOT/'research/exterior_weathering_materials.json').write_text(json.dumps(report,indent=2)+'\n')
    print('EXTERIOR_WEATHERING',len(records),'unique meshes',flush=True)
    return report
