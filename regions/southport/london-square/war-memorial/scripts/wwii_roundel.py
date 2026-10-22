"""Southwest inscription insert, from the supplied Instagram close photograph.

Transcription is evidenced; metric dimensions, reed count and cutting profiles
remain photographic estimates. The historic erased-state caption is retained
as a source conflict in research/wwii_roundel_study.json.
"""
import math
from mathutils import Vector
from geometry import Mesh, face_matrix

CENTRE_Z = 3.06
WALL = 1.275
FRONT = .035
RADIUS = .515


def build(ns):
    study = ns['SPEC']['wwii_roundel']
    collection = ns['OBELISK']
    origin = (-WALL, 0, CENTRE_Z)
    normal = (-1, 0, 0)
    disc = Mesh('Obelisk SW WWII inscribed circular insert')
    disc.lathe((0, 0), [(-.003, RADIUS-.002), (.031, RADIUS),
                       (FRONT, RADIUS-.002)], 256, 0)
    # One stone slot keeps the Boolean cutter's groove-material index aligned.
    ob = disc.finish([ns['STONE'][3]], collection)
    ob.matrix_world = face_matrix(origin, normal)
    ob['source_detail'] = 'research/wwii_roundel_study.json'
    ob['reconstruction_state'] = 'Legible insert in user-supplied Instagram photograph; capture date unknown'
    ob['inscription_transcript'] = '\n'.join(ns['SPEC']['exterior_inscriptions']['obelisk_SW'])
    matrix = face_matrix(origin, normal)
    for index, row in enumerate(study['lines']):
        point = matrix @ Vector((0, row['centre_v_m'], FRONT))
        ns['engrave'](ob, 'Obelisk WWII line '+str(index+1), row['text'], point,
                      normal, row['height_m'], row['width_m'], collection, fit_bounds=True)
    point = matrix @ Vector((0, -.194, FRONT))
    ns['engrave'](ob, 'Obelisk WWII underline', '—', point, normal,
                  .0025, .20, collection, fit_bounds=True)
    # Continuous annular backing, with small radial reeds between the old
    # moulding and the projecting insert. No masonry joint crosses the insert.
    ring = Mesh('Obelisk SW WWII radial reeding')
    count = study['reed_count_estimate']
    segments = count*6
    vertices = []
    for radius, depth in [(RADIUS-.003, .002), (.596, .002),
                          (.596, .012), (RADIUS-.003, .012)]:
        for i in range(segments):
            angle = 2*math.pi*i/segments
            ridge = .006*(.5+.5*math.cos(count*angle)) if depth>.01 else 0
            vertices.append((radius*math.cos(angle), radius*math.sin(angle), depth+ridge))
    faces = []
    for j in range(4):
        for i in range(segments):
            nxt = (i+1)%segments
            faces.append((j*segments+i, j*segments+nxt,
                          ((j+1)%4)*segments+nxt, ((j+1)%4)*segments+i))
    ring.add(vertices, faces, 3)
    surround = ns['mounted'](ring, origin, normal, collection, smooth=True)
    surround['source_detail'] = 'research/wwii_roundel_study.json'
    surround['reed_count_status'] = 'Estimated repetition count; not measured from a frontal photograph'
    print('WWII_ROUNDEL', len(study['lines']), 'lines and underline', flush=True)


def validate(scene):
    """Probe the exported insert itself for facing, scale and real recesses."""
    ob = next(o for o in scene.objects if o.name.startswith('Obelisk SW WWII inscribed'))
    normal = (ob.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    assert normal.dot(Vector((-1, 0, 0)))>.999, 'WWII insert on wrong face'
    inv = ob.matrix_world.inverted()
    widths = [v.co.x for v in ob.data.vertices]
    assert abs(max(widths)-min(widths)-2*RADIUS)<.001
    groove_slots = {i for i, m in enumerate(ob.data.materials) if m and 'Incised stone' in m.name}
    assert groove_slots and any(p.material_index in groove_slots for p in ob.data.polygons), 'Cut-face material lost'
    results = []
    # Dense horizontal samples cross several letters and their uncut spaces;
    # measure the actual mesh after glTF re-import, not inscription metadata.
    for z in (CENTRE_Z+.396, CENTRE_Z-.008, CENTRE_Z-.422):
        depths = []
        for i in range(241):
            p = Vector((-2, -.49+i*.98/240, z))
            ok, hit, _, _ = ob.ray_cast(inv@p, inv.to_3x3()@Vector((1, 0, 0)))
            if ok:depths.append(WALL+FRONT+(ob.matrix_world@hit).x)
        assert depths and min(depths)<.0002 and max(depths)>.005, ('Missing incised row', z, depths)
        results.append({'height_m':z, 'maximum_cut_m':max(depths), 'samples':len(depths)})
    assert not any(o.name.startswith('Obelisk NE roundel') for o in scene.objects)
    return {'face':'SW', 'diameter_m':2*RADIUS, 'engraving_probes':results,
            'NE_face_plain':True}
