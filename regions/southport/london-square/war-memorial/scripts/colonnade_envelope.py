"""Stepped colonnade envelope, authored from the exterior reference photographs.

The central range projects forward as a whole. The window chambers are set
back on both long elevations. All dimensions remain photographic estimates.
Used by both the isolated plan comparison and the checkpoint 0.12 assemblies.
"""
import math
import random


def outline(length, depth, break_x, setback):
    """Counterclockwise twelve-corner outline, centred on the assembly."""
    x, y, b = length / 2, depth / 2, break_x
    assert 0 < b < x and 0 < setback < y
    c = y - setback
    return [(-x, -c), (-b, -c), (-b, -y), (b, -y), (b, -c),
            (x, -c), (x, c), (b, c), (b, y), (-b, y), (-b, c), (-x, c)]


def profile(mesh, rings, break_x, setback, material=0):
    """Closed swept moulding: rings are (z, overall length, maximum depth)."""
    vertices = [(x, y, z) for z, length, depth in rings
                for x, y in outline(length, depth, break_x, setback)]
    n = 12
    faces = [tuple(reversed(range(n)))]
    for row in range(len(rings) - 1):
        for i in range(n):
            a, b = row*n+i, row*n+(i+1) % n
            faces.append((a, b, b+n, a+n))
    faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    mesh.add(vertices, faces, material)


def ring(mesh, length, depth, break_x, setback, thickness, z0, z1, material=0):
    """A closed hollow ring with properly offset returns at the roof steps."""
    outer = outline(length, depth, break_x, setback)
    inner = outline(length-2*thickness, depth-2*thickness,
                    break_x-thickness, setback)
    n = len(outer)
    vertices = [(x,y,z) for z in (z0,z1) for path in (outer,inner) for x,y in path]
    faces = []
    for i in range(n):
        j = (i+1) % n
        faces.extend([(i,j,j+2*n,i+2*n), (i+n,i+3*n,j+3*n,j+n),
                      (i+2*n,j+2*n,j+3*n,i+3*n), (i,i+n,j+n,j)])
    mesh.add(vertices,faces,material)


def parapet(mesh, length, depth, break_x, setback, thickness, z0, z1):
    """Separate narrow-jointed stones; corner mitres share no coplanar faces."""
    outer = outline(length,depth,break_x,setback)
    inner = outline(length-2*thickness,depth-2*thickness,break_x-thickness,setback)
    rng = random.Random(19231221)
    for i in range(len(outer)):
        j = (i+1) % len(outer)
        edge_length = max(math.dist(outer[i],outer[j]), math.dist(inner[i],inner[j]))
        count = max(1, math.ceil(edge_length / 1.25))
        gap = .0015 / edge_length
        def point(path,t):
            return tuple(a+(b-a)*t for a,b in zip(path[i],path[j]))
        for k in range(count):
            a, b = k/count+gap, (k+1)/count-gap
            mesh.outline([point(outer,a),point(outer,b),point(inner,b),point(inner,a)],
                         z0,z1,rng.randrange(6))


ARCHITRAVE_PROFILE = [
    (4.142,24.22,4.64), (4.220,24.22,4.64),
    (4.220,24.30,4.70), (4.350,24.30,4.70),
    (4.350,24.37,4.78), (4.397,24.37,4.78),
    (4.397,24.36,4.74), (4.420,24.36,4.74),
]

# Estimated rounded/lipped contour within the published maximum envelope.
# The exact small fillets are not claimed as a measured moulding section.
CORNICE_PROFILE = [
    (4.900,24.36,4.74), (4.912,24.38,4.76),
    (4.936,24.44,4.82), (4.952,24.52,4.88),
    (4.968,24.56,4.90), (4.985,24.56,4.90),
    (4.985,24.50,4.84), (4.990,24.48,4.82),
    (5.005,24.52,4.86), (5.025,24.54,4.88),
    (5.045,24.50,4.84), (5.060,24.48,4.82),
    (5.075,24.55,4.89), (5.095,24.60,4.90),
    (5.110,24.58,4.88), (5.130,24.40,4.78),
]


def pier_end_surface_count(mesh, sign, side, inner_tip=6.85):
    """Count coincident end faces at a point inside the former 40 mm overlap.

    A normal ray returns only the first coincident face and misses z-fighting.
    Count triangulated surfaces at an interior point of this exposed end cap.
    The sample is deliberately off stone beds and triangle diagonals.
    """
    mesh.calc_loop_triangles()
    x=sign*(inner_tip+.002)  # Ashlar's 4 mm joint leaves 2 mm at each end.
    py,pz=side*2.1813,2.4191
    count=0
    for tri in mesh.loop_triangles:
        a,b,c=(mesh.vertices[i].co for i in tri.vertices)
        if max(abs(p.x-x) for p in (a,b,c))>.0001:continue
        det=(b.y-a.y)*(c.z-a.z)-(b.z-a.z)*(c.y-a.y)
        if abs(det)<1e-12:continue
        u=((py-a.y)*(c.z-a.z)-(pz-a.z)*(c.y-a.y))/det
        v=((b.y-a.y)*(pz-a.z)-(b.z-a.z)*(py-a.y))/det
        if u>1e-7 and v>1e-7 and u+v<1-1e-7:count+=1
    return count
