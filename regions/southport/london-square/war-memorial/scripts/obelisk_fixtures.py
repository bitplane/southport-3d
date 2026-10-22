"""Photographed pyramid openings and cornice light housings.

The source register distinguishes visible features from estimated dimensions.
Pyramid cuts are solid cavities, with bars inset behind the stone face.
"""
import json
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from geometry import Mesh

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = json.loads((ROOT/'research/obelisk_fixture_calibration.json').read_text())
NORMALS = {'SE': (0, -1, 0), 'NW': (0, 1, 0), 'SW': (-1, 0, 0), 'NE': (1, 0, 0)}


def pyramid_frame(face):
    """Orthonormal basis on the sloping triangle, with its true tangent up."""
    p = CALIBRATION['pyramid']
    slope = p['base_width_m']/2/(p['tip_z_m']-p['base_z_m'])
    radial = Vector(NORMALS[face])
    z = p['opening_centre_z_m']
    origin = radial*(slope*(p['tip_z_m']-z))
    origin.z = z
    normal = (radial+Vector((0, 0, slope))).normalized()
    right = Vector((0, 0, 1)).cross(normal).normalized()
    up = normal.cross(right).normalized()
    return Matrix(((right.x, up.x, normal.x, origin.x),
                   (right.y, up.y, normal.y, origin.y),
                   (right.z, up.z, normal.z, origin.z), (0, 0, 0, 1)))


def build_pyramid(collection, stone, metal, dark):
    p = CALIBRATION['pyramid']
    r = p['base_width_m']/2
    z, tip = p['base_z_m'], p['tip_z_m']
    mesh = Mesh('Obelisk pyramid with two recessed barred openings')
    mesh.add([(-r, -r, z), (r, -r, z), (r, r, z), (-r, r, z), (0, 0, tip)],
             [(3, 2, 1, 0), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
    pyramid = mesh.finish([stone], collection)
    pyramid['obelisk_part'] = 'pyramid'
    pyramid['source_detail'] = 'research/obelisk_fixture_calibration.json'
    pyramid['opening_faces'] = 'SE, NW; SW observed plain, NE unverified'
    w, h, depth = p['opening_width_m'], p['opening_height_along_face_m'], p['recess_depth_normal_to_face_m']
    template = None
    for face in p['confirmed_opening_faces']:
        frame = pyramid_frame(face)
        cutter = Mesh('Temporary pyramid opening cutter')
        cutter.box((0, 0, (.02-depth)/2), (w, h, depth+.02))
        cutter = cutter.finish([stone], collection)
        cutter.matrix_world = frame
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action='DESELECT')
        pyramid.select_set(True)
        bpy.context.view_layer.objects.active = pyramid
        mod = pyramid.modifiers.new('Actual '+face+' opening', 'BOOLEAN')
        mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
        if template is None:
            grille = Mesh('Recessed pyramid grille — spacing estimated')
            # Dark cavity backing and a thin inset metal surround.
            grille.box((0, 0, -depth+.004), (w-.002, h-.002, .004), 1)
            for side in (-1, 1):
                grille.box((0, side*(h/2-.002), -.013), (w-.002, .003, .008))
                grille.box((side*(w/2-.002), 0, -.013), (.003, h-.002, .008))
            for j in range(p['bar_count_modelled']):
                u = -w/2+(j+1)*w/(p['bar_count_modelled']+1)
                grille.box((u, 0, -.015), (p['bar_width_m'], h-.004, .012))
            ob = grille.finish([metal, dark], collection)
            template = ob
        else:
            ob = template.copy(); ob.data = template.data; collection.objects.link(ob)
        ob.name = 'Obelisk '+face+' recessed pyramid grille'
        ob.matrix_world = frame
        ob['obelisk_part'] = 'pyramid_grille'; ob['face'] = face
        ob['bar_count_estimated'] = p['bar_count_modelled']
        ob['source'] = p['confirmed_opening_faces'][face]['source']
        ob['status'] = 'Opening evidenced; dimensions, bars and hidden depth estimated; purpose unverified'
    return pyramid


def build_linear_lights(collection, pale, dark):
    p = CALIBRATION['linear_lights']
    length, radius = p['housing_length_m'], p['housing_radius_m']
    # Native +Y is outward, native +Z up, native -X screen-right.
    mesh = Mesh('Obelisk linear light housing with feet and collar')
    depth, height = p['centre_outward_from_axis_m'], p['centre_z_m']
    mesh.tube([(-length/2, depth, height), (length/2, depth, height)], radius,
              sides=32, depth_scale=p['housing_vertical_radius_factor'])
    for end in (-1, 1):
        a = end*(length/2-.001); b = end*(length/2+.008)
        mesh.tube([(a, depth, height), (b, depth, height)], radius+.001, 1,
                  sides=32, depth_scale=p['housing_vertical_radius_factor'])
        mesh.tube([(b, depth, height), (b+end*.001, depth, height)], radius*.78, 0,
                  sides=32, depth_scale=p['housing_vertical_radius_factor'])
        mesh.tube([(b+end*.001, depth, height), (b+end*.002, depth, height)], .007, 1, sides=12)
    # Narrow longitudinal seams follow the curved outward face.
    for dz in (.008, .022):
        y = depth+radius*math.sqrt(1-(dz/(radius*p['housing_vertical_radius_factor']))**2)
        mesh.tube([(-length/2+.015, y, height+dz), (length/2-.015, y, height+dz)],
                  .0013, 1, sides=6)
    collar = Mesh('Light housing collar')
    collar.lathe((0, 0), [(-.009, radius+.002), (-.006, radius+.005),
                           (.006, radius+.005), (.009, radius+.002)], segments=32)
    collar.transform(Matrix.Translation((-p['collar_u_m'], depth, height)) @ Matrix.Rotation(math.pi/2, 4, 'Y'))
    mesh.add(collar.vertices, collar.faces)
    for x in p['foot_u_m']:
        mesh.box((x, depth, p['cornice_top_z_m']+.004), p['foot_size_m'], 1)
        mesh.box((x, depth, p['cornice_top_z_m']+.025), (.025, .045, .036), 1)
    template = None
    for face in p['confirmed_faces']:
        angle = math.atan2(NORMALS[face][1], NORMALS[face][0])-math.pi/2
        if template is None:
            ob = mesh.finish([pale, dark], collection)
            template = ob
        else:
            ob = template.copy(); ob.data = template.data; collection.objects.link(ob)
        # Use rotation only, retaining outward seams and positive mesh scale.
        ob.matrix_world = Matrix.Rotation(angle, 4, 'Z')
        ob.name = 'Obelisk '+face+' cornice linear light'
        ob['obelisk_part'] = 'cornice_linear_light'; ob['face'] = face
        ob['source'] = ', '.join(p['confirmed_faces'][face])
        ob['status'] = 'Photographed exterior; size and cross-section estimated; NE arrangement unresolved'
    return template


def validate_fixtures(scene):
    """Probe imported surface depth and actual cornice contact, not metadata alone."""
    p = CALIBRATION['pyramid']
    pyramid = next(o for o in scene.objects if o.get('obelisk_part') == 'pyramid')
    grilles = [o for o in scene.objects if o.get('obelisk_part') == 'pyramid_grille']
    lights = [o for o in scene.objects if o.get('obelisk_part') == 'cornice_linear_light']
    assert {o['face'] for o in grilles} == {'SE', 'NW'}
    assert {o['face'] for o in lights} == {'SE', 'SW', 'NW'}
    assert len({o.data.name for o in grilles}) == 1
    assert len({o.data.name for o in lights}) == 1
    def offset(ob, point, normal):
        inverse = ob.matrix_world.inverted()
        hit, loc, _, _ = ob.ray_cast(inverse@(point+normal*.20), inverse.to_3x3()@(-normal))
        assert hit, (ob.name, 'Missing ray intersection', tuple(point))
        return (ob.matrix_world@loc-point).dot(normal)
    report = {'opening_depth_samples_m': {}, 'grille_bar_samples_m': {}, 'plain_faces': {}, 'cornice_supports': 0}
    for grille in grilles:
        frame = pyramid_frame(grille['face']); normal = frame.to_3x3()@Vector((0, 0, 1))
        assert abs(frame.to_3x3().determinant()-1) < 1e-6
        bars, gaps = [], []
        pitch = p['opening_width_m']/(p['bar_count_modelled']+1)
        for j in (2, 8, 15, 21):
            u = -p['opening_width_m']/2+(j+1)*pitch
            point = frame@Vector((u, 0, 0))
            bars.append(offset(grille, point, normal))
            gap = frame@Vector((u+pitch/2, 0, 0))
            cavity = offset(pyramid, gap, normal)
            assert abs(cavity+p['recess_depth_normal_to_face_m']) < .0001, cavity
            gaps.append(cavity)
            back = offset(grille, gap, normal)
            assert -.076 < back < -.072, back
        assert all(-.010 < v < -.008 for v in bars), bars
        # Stone immediately above and beside the cut must remain on its plane.
        for u, v in [(0, .045), (0, -.045), (.33, 0), (-.33, 0)]:
            assert abs(offset(pyramid, frame@Vector((u, v, 0)), normal)) < .0001
        report['opening_depth_samples_m'][grille['face']] = gaps
        report['grille_bar_samples_m'][grille['face']] = bars
    for face in ('SW', 'NE'):
        frame = pyramid_frame(face); normal = frame.to_3x3()@Vector((0, 0, 1))
        report['plain_faces'][face] = offset(pyramid, frame.translation, normal)
        assert abs(report['plain_faces'][face]) < .0001
    cornice = bpy.data.objects['Obelisk pedestal cornice']
    lp = CALIBRATION['linear_lights']
    for ob in lights:
        verts = [ob.matrix_world@v.co for v in ob.data.vertices]
        assert abs(min(v.z for v in verts)-lp['cornice_top_z_m']) < .0001
        for x in lp['foot_u_m']:
            for dx in (-.06, .06):
                for dy in (-.05, .05):
                    point = ob.matrix_world@Vector((x+dx, lp['centre_outward_from_axis_m']+dy, lp['cornice_top_z_m']))
                    assert abs(offset(cornice, point, Vector((0, 0, 1)))) < .0002
                    report['cornice_supports'] += 1
    return report
