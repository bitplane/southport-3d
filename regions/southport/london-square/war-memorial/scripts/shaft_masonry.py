"""Photographically registered obelisk shaft beds and face-specific bonds.

Closed face stones overlap a solid core. The estimated 3 mm seams therefore
have a physical 4 mm backing depth rather than exposing an empty shell.
"""
import json
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector
from geometry import Mesh

ROOT=Path(__file__).resolve().parents[1]
LAYOUT=json.loads((ROOT/'research/shaft_masonry_calibration.json').read_text())
NORMALS={'SE':(0,-1,0),'NW':(0,1,0),'SW':(-1,0,0),'NE':(1,0,0)}
BOUNDS=LAYOUT['metric_envelope']
BEDS=[v['height_m'] for v in LAYOUT['horizontal_beds_top_down']]
SLOPE=(BOUNDS['top_width_m']-BOUNDS['base_width_m'])/2/(BOUNDS['top_z_m']-BOUNDS['base_z_m'])


def radius(z):
    return BOUNDS['base_width_m']/2+SLOPE*(z-BOUNDS['base_z_m'])


def point(face,u,z,inset=0):
    radial=Vector(NORMALS[face]);right=Vector((0,0,1)).cross(radial)
    return radial*(radius(z)-inset)+right*u+Vector((0,0,z))


def face_normal(face):
    return (Vector(NORMALS[face])+Vector((0,0,-SLOPE))).normalized()


def joints(face,row):
    if face not in LAYOUT['faces']:return []
    return LAYOUT['faces'][face]['vertical_joint_rows'][row]['u_m']


def build(collection,materials,surface_materials=None):
    j=LAYOUT['joint_geometry']
    core=Mesh('Tapered obelisk shaft — continuous joint backing')
    core.rect_profile((0,0),[(z,2*(radius(z)-j['depth_m']),2*(radius(z)-j['depth_m']))
                            for z in (BOUNDS['base_z_m'],BOUNDS['top_z_m'])],5)
    ob=core.finish(materials,collection)
    ob['shaft_part']='solid_core'
    ob['source_detail']='research/shaft_masonry_calibration.json'
    result=[ob]
    for face in NORMALS:
        mesh=Mesh('Obelisk shaft '+face+' — registered ashlar faces')
        rng=random.Random(1923+sum(ord(c) for c in face))
        blocks=0
        surface_records=[]
        for row,(top,bottom) in enumerate(zip(BEDS,BEDS[1:])):
            a=bottom+(j['horizontal_width_m']/2 if row<len(BEDS)-2 else 0)
            b=top-(j['horizontal_width_m']/2 if row else 0)
            boundaries=[None]+joints(face,row)+[None]
            for index,(left,right) in enumerate(zip(boundaries,boundaries[1:])):
                def u(value,z,is_left):
                    if value is None:return (-1 if is_left else 1)*radius(z)
                    return value+(1 if is_left else -1)*j['vertical_width_m']/2
                outer=[(u(left,a,True),a),(u(right,a,False),a),
                       (u(right,b,False),b),(u(left,b,True),b)]
                assert all(abs(x)<=radius(z)+1e-8 for x,z in outer)
                assert outer[0][0]<outer[1][0] and outer[3][0]<outer[2][0]
                vertices=[point(face,x,z) for x,z in outer]
                # Only exterior corners are mitered. Interior bond walls keep
                # their u coordinate so the narrow channels do not close or
                # drift sideways before reaching the solid backing surface.
                depth=j['face_slab_depth_m']
                for k,(x,z) in enumerate(outer):
                    corner=(left is None) if k in (0,3) else (right is None)
                    inner_x=x-math.copysign(depth,x) if corner else x
                    vertices.append(point(face,inner_x,z,depth))
                mat=rng.randrange(6)
                if surface_materials:
                    from obelisk_surfaces import block_class
                    mat=block_class(face,row,index,len(boundaries)-1)
                    surface_records.append({'course':row,'block':index,'class':('pale','aged','pitted')[mat]})
                mesh.add(vertices,[(0,1,2,3),(7,6,5,4),(4,5,1,0),
                                   (5,6,2,1),(6,7,3,2),(7,4,0,3)],mat)
                blocks+=1
        ob=mesh.finish(surface_materials or materials,collection)
        ob['shaft_part']='face_stones';ob['shaft_face']=face
        ob['shaft_course_count']=len(BEDS)-1;ob['shaft_face_block_count']=blocks
        ob['source_detail']='research/shaft_masonry_calibration.json'
        ob['status']='Registered joint layout; dimensions/depths estimated; authored surface classes follow evidenced contrasts'
        ob['vertical_bond_evidence']=LAYOUT['faces'][face]['source'] if face in LAYOUT['faces'] else 'Unverified; vertical bonds omitted'
        if surface_materials:
            # Individual stones use different origins in the same metric tile.
            # This avoids conspicuous alignment of identical pits between rows.
            uv=ob.data.uv_layers.new(name='Metre-scale individual stone UV')
            right=Vector((0,0,1)).cross(Vector(NORMALS[face]))
            offsets=random.Random(737+sum(ord(c) for c in face))
            for record in surface_records:
                record['uv_offset_m']=[offsets.random(),offsets.random()]
            for poly in ob.data.polygons:
                offset=surface_records[poly.index//6]['uv_offset_m']
                for li in poly.loop_indices:
                    p=ob.data.vertices[ob.data.loops[li].vertex_index].co
                    uv.data[li].uv=(p.dot(right)+offset[0],p.z+offset[1])
            ob['authored_surface_uv']=True
            ob['stone_surface_assignments']=json.dumps(surface_records)
            ob['surface_source_detail']='research/shaft_weathering_observations.json'
        result.append(ob)
    return result


def validate_shaft(scene):
    """Check actual exported face surfaces, recessed joints and closed backing."""
    core=[o for o in scene.objects if o.get('shaft_part')=='solid_core']
    faces=[o for o in scene.objects if o.get('shaft_part')=='face_stones']
    assert len(core)==1 and {o['shaft_face'] for o in faces}==set(NORMALS)
    objects=core+faces
    vertices=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    assert abs(min(p.z for p in vertices)-BOUNDS['base_z_m'])<.00001
    assert abs(max(p.z for p in vertices)-BOUNDS['top_z_m'])<.00001
    def surface(face,u,z):
        target=point(face,u,z);normal=face_normal(face);hits=[]
        for ob in objects:
            inverse=ob.matrix_world.inverted()
            ok,loc,_,_=ob.ray_cast(inverse@(target+normal*.15),inverse.to_3x3()@(-normal))
            if ok:
                q=ob.matrix_world@loc
                offset=(q-target).dot(normal)
                if offset<.15:hits.append(offset)
        assert hits,(face,u,z,'Open shaft / absent backing')
        return max(hits)
    expected=-LAYOUT['joint_geometry']['depth_m']/math.sqrt(1+SLOPE*SLOPE)
    report={'course_count':len(BEDS)-1,'horizontal_joint_rays':0,'vertical_joint_rays':{},
            'face_surface_rays':0,'depth_range_m':[],
            'unverified_NE_vertical_bonds_omitted':True}
    depths=[]
    for face in NORMALS:
        count=0
        for z in BEDS[1:-1]:
            for u in (-.31,.09,.32):
                q=surface(face,u,z)
                assert abs(q-expected)<.0001,(face,z,q,'Horizontal seam depth')
                depths.append(-q);report['horizontal_joint_rays']+=1
        for row,(a,b) in enumerate(zip(BEDS,BEDS[1:])):
            z=(a+b)/2
            for u in joints(face,row):
                q=surface(face,u,z)
                assert abs(q-expected)<.0001,(face,row,u,q,'Vertical bond depth')
                depths.append(-q);count+=1
            # An off-centre point inside a stone must remain on the outer face.
            q=surface(face,.17,z)
            assert abs(q)<.0001,(face,row,q,'Stone surface displaced')
            report['face_surface_rays']+=1
        report['vertical_joint_rays'][face]=count
    report['depth_range_m']=[min(depths),max(depths)]
    report['face_blocks']={o['shaft_face']:o['shaft_face_block_count'] for o in faces}
    return report
