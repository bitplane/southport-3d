"""Closed, intersecting roof volumes with one visible skin at each valley."""
import bpy
import bmesh
from mathutils import Vector
from southport3d.geometry import Mesh


def roof_volume(name, outline, ridge, eave, bottom, finish):
    """A rectangular hip/gable volume; outline and ridge are paired clockwise."""
    m = Mesh(name)
    vertices = [(x, y, bottom) for x, y in outline]
    vertices += [(x, y, eave) for x, y in outline]
    vertices += list(ridge)
    m.add(vertices, [(3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5),
                     (2, 3, 7, 6), (3, 0, 4, 7),
                     (4, 5, 9, 8), (5, 6, 9), (6, 7, 8, 9), (7, 4, 8)])
    ob = finish(m)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def joined_roof(xn, xf, yf, yb, z0, finish, ranges):
    """Union the two ranges and three cross gables; remove all buried sheets."""
    # The street eaves sit inside the masonry and below its top cornice.
    xf -= .04
    yb += .04
    x0, y0 = xn + .30, yf - .30
    xr, xi = xn + ranges["side_width"]/2, xn + ranges["side_width"]
    yr, back = yf-ranges["front_depth"]/2, yf-ranges["front_depth"]
    ze = z0 + 12.35
    zr = z0 + ranges["front_ridge_height"]
    side_zr = z0 + ranges["side_ridge_height"]
    bottom = ze - .18
    volumes = []

    def add(outline, ridge):
        volumes.append(roof_volume('Roof joined slate', outline, ridge, ze, bottom, finish))

    add([(x0, y0), (xf, y0), (xf, back), (x0, back)],
        [(xr, yr, zr), (xf - 2.5, yr, zr)])
    add([(x0, yb), (x0, y0), (xi, y0), (xi, yb)],
        [(xr, yb + 3.4, side_zr), (xr, yr, side_zr)])
    for x in (xf - 3.0, xn + 3.0):
        corner = x < xn + 4
        end = yf-ranges['corner_saddle_depth'] if corner else yr
        peak = z0+ranges['corner_saddle_height'] if corner else zr
        add([(x - 2.7, y0), (x - 2.7, end), (x + 2.7, end), (x + 2.7, y0)],
            [(x, y0, peak), (x, end, peak)])
    y = yf - 8.1
    add([(x0, y - 2.7), (xr, y - 2.7), (xr, y + 2.7), (x0, y + 2.7)],
        [(x0, y, side_zr), (xr, y, side_zr)])
    roof = volumes[0]
    for operand in volumes[1:]:
        bpy.context.view_layer.objects.active = roof
        modifier = roof.modifiers.new('Resolve roof valleys', 'BOOLEAN')
        modifier.operation = 'UNION'
        modifier.solver = 'EXACT'
        modifier.object = operand
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(operand, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(roof.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), 'Roof must be a closed manifold'
    bm.to_mesh(roof.data)
    bm.free()
    roof.data.update()
    # Stable slope-space coordinates: horizontal courses follow every eave.
    uv = roof.data.uv_layers.active
    for face in roof.data.polygons:
        normal = face.normal
        u = Vector((-normal.y, normal.x, 0))
        if u.length < 1e-5:
            u = Vector((1, 0, 0))
        u.normalize()
        v = normal.cross(u)
        for li in face.loop_indices:
            p = roof.data.vertices[roof.data.loops[li].vertex_index].co
            uv.data[li].uv = (p.dot(u) / 1.45, p.dot(v) / 1.6)
    return roof
