"""Portable stone classes and face-specific tip stains, authored from evidence."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
FAMILY = 'Authored obelisk stone surfaces'
NORMALS = {'SE': (0, -1, 0), 'NW': (0, 1, 0), 'SW': (-1, 0, 0), 'NE': (1, 0, 0)}


def material(key):
    name = 'Obelisk surface — '+key
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    for kind, socket in [('base', 'Base Color'), ('roughness', 'Roughness'), ('normal', 'Normal')]:
        path = ROOT/'textures'/f'obelisk-{key}-{kind}.png'
        assert path.exists(), f'Run python3 scripts/author_obelisk_surfaces.py first: {path}'
        image = bpy.data.images.load(str(path), check_existing=True)
        image.colorspace_settings.name = 'sRGB' if kind == 'base' else 'Non-Color'
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = image
        tex.extension = 'EXTEND' if key.startswith('tip-') else 'REPEAT'
        tex.label = 'Authored numeric '+kind+'; no source photo pixels'
        if kind == 'normal':
            normal = nt.nodes.new('ShaderNodeNormalMap')
            nt.links.new(tex.outputs['Color'], normal.inputs['Color'])
            nt.links.new(normal.outputs['Normal'], bsdf.inputs['Normal'])
        else:
            nt.links.new(tex.outputs['Color'], bsdf.inputs[socket])
    m['portable_surface_family'] = FAMILY
    m['surface_key'] = key
    m['source_detail'] = 'research/obelisk_surface_materials.json'
    m['texture_provenance'] = 'Authored numeric PBR maps; no source photography embedded; physical surface parameters estimated'
    return m


def shaft_palette():
    return [material(k) for k in ('pale', 'aged', 'pitted')]


def block_class(face, row, index, count):
    """Only override blocks for which within-face contrast is evidenced."""
    if face == 'SW':
        if row in (5, 9, 33, 35) and index == 1:
            return 0
        if row in (7, 11, 27, 20, 28) and index == 0:
            return 0
        if row in (21, 23, 30, 32) or (row == 33 and index in (0, count-1)):
            return 2
    if face == 'SE' and ((row == 18 and index == 0) or (row == 34 and index == 1)):
        return 0
    return 1


def apply_pyramid(ob):
    calibration = json.loads((ROOT/'research/obelisk_fixture_calibration.json').read_text())['pyramid']
    z0, z1 = calibration['base_z_m'], calibration['tip_z_m']
    width = calibration['base_width_m']
    ob.data.materials.clear()
    faces = list(NORMALS)
    for face in faces:
        ob.data.materials.append(material('tip-'+face.lower()))
    uv = ob.data.uv_layers.active or ob.data.uv_layers.new(name='Registered pyramid face UV')
    for poly in ob.data.polygons:
        # Includes the boolean recess walls without altering the solid geometry.
        # Cavity polygons are assigned by position on the appropriate face.
        c = poly.center
        radial = Vector((c.x, c.y, 0))
        face = max(faces, key=lambda f: radial.dot(Vector(NORMALS[f])))
        right = Vector((0, 0, 1)).cross(Vector(NORMALS[face]))
        poly.material_index = faces.index(face)
        for li in poly.loop_indices:
            p = ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv = (p.dot(right)/width+.5, (p.z-z0)/(z1-z0))
    ob['authored_surface_uv'] = True
    ob['surface_source_detail'] = 'research/obelisk_surface_materials.json'
    ob['surface_status'] = 'SE/SW yellow and NW grey-green tip streaks interpreted from 2011–2013 views; NE not resolved'


def report():
    return json.loads((ROOT/'research/obelisk_surface_materials.json').read_text())


def validate_assignments(scene):
    """Probe imported mesh materials at pale/pitted landmarks in the evidence."""
    from shaft_masonry import BEDS, joints, radius, point, face_normal
    observations=json.loads((ROOT/'research/shaft_weathering_observations.json').read_text())['observations']
    objects={o['shaft_face']:o for o in scene.objects if o.get('shaft_part')=='face_stones'}
    checked=[]
    for observation in observations:
        if 'courses_top_down' not in observation:
            continue
        face=observation['face']
        ob=objects[face]
        for row in observation['courses_top_down']:
            z=(BEDS[row]+BEDS[row+1])/2
            bonds=[-radius(z)]+joints(face,row)+[radius(z)]
            field=observation['field']
            if field=='wide central stone':
                u=(bonds[1]+bonds[2])/2
            elif field in ('left corner stone','left of central bond'):
                u=(bonds[0]+bonds[1])/2
            else:
                u=.17
            normal=face_normal(face)
            target=point(face,u,z)
            inverse=ob.matrix_world.inverted()
            hit,_,_,index=ob.ray_cast(inverse@(target+normal*.15),inverse.to_3x3()@(-normal))
            assert hit,(face,row,'Missing stone at surface landmark')
            mat=ob.data.materials[ob.data.polygons[index].material_index]
            expected='pale' if 'pale' in observation['finding'] else 'pitted'
            assert mat.get('surface_key')==expected,(face,row,mat.name,expected)
            checked.append({'face':face,'course':row,'u_m':u,'material':expected})
    assert len(checked)==15
    pyramid=next(o for o in scene.objects if o.get('obelisk_part')=='pyramid')
    from obelisk_fixtures import pyramid_frame
    for face in NORMALS:
        frame=pyramid_frame(face)
        normal=frame.to_3x3()@Vector((0,0,1))
        target=frame@Vector((.18,.33,0))
        inverse=pyramid.matrix_world.inverted()
        hit,_,_,index=pyramid.ray_cast(inverse@(target+normal*.15),inverse.to_3x3()@(-normal))
        assert hit,(face,'Missing pyramid surface')
        mat=pyramid.data.materials[pyramid.data.polygons[index].material_index]
        assert mat.get('surface_key')=='tip-'+face.lower(),(face,mat.name)
    return {'shaft_evidence_landmarks':checked,'pyramid_face_materials_verified':4}
