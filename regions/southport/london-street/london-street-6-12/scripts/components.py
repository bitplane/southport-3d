"""Local facade components for 6–12 London Street, in elevation coordinates.

X runs along the elevation, Y is height and Z points out. Components remain
separate from site placement so repeated windows share their baked receiver.
"""
import math
from southport3d.geometry import Mesh


def sash(name, width, height, surround=.12, bars=True):
    """White painted surround, stepped reveal and two overlapping sash leaves.

    Materials: white frame, dark reveal, opaque glass, painted sill.
    This is an exterior receiver, not transparent glazing into a fake room.
    """
    mesh = Mesh(name)
    mesh.box((0, 0, -.16), (width, height, .045), 1)
    glass_w = width - 2 * surround - .04
    glass_h = height - 2 * surround - .04
    for x in [-width / 2 + surround / 2, width / 2 - surround / 2]:
        mesh.box((x, 0, -.025), (surround, height, .20), 0)
    for y in [-height / 2 + surround / 2, height / 2 - surround / 2]:
        mesh.box((0, y, -.025), (width - 2 * surround, surround, .20), 0)
    for y, depth in [(-glass_h / 4, -.09), (glass_h / 4, -.12)]:
        mesh.box((0, y, depth), (glass_w, glass_h / 2, .025), 2)
    mesh.box((0, 0, -.025), (glass_w, .065, .12), 0)
    if bars:
        for x in [-glass_w / 2 + .022, glass_w / 2 - .022]:
            mesh.box((x, 0, -.045), (.035, glass_h, .07), 0)
        for y in [-glass_h / 2 + .02, glass_h / 2 - .02]:
            mesh.box((0, y, -.045), (glass_w, .035, .07), 0)
    mesh.box((0, -height / 2 - .055, .02), (width + .15, .11, .32), 3)
    return mesh


def cornice(name, length):
    """Stepped painted eaves: preserve silhouette at every LoD."""
    mesh = Mesh(name)
    for y, height, projection in [(-.10, .08, .10), (0, .12, .17), (.10, .08, .26)]:
        mesh.box((0, y, projection / 2), (length, height, projection))
    return mesh


def rooflight(name, width=2.5, depth=2.1, rise=.65, detailed=True):
    """Observed rear pyramidal glazed rooflight. Materials: lead, opaque glass."""
    mesh = Mesh(name)
    mesh.box((0, 0, .09), (width + .18, depth + .18, .18), 0)
    corners = [(-width / 2, -depth / 2, .18), (width / 2, -depth / 2, .18),
               (width / 2, depth / 2, .18), (-width / 2, depth / 2, .18)]
    apex = (0, 0, .18 + rise)
    mesh.add(corners + [apex], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], 1)
    for corner in corners:
        mesh.tube([corner, apex], .035, 0, 6)
    if detailed:
        for a, b in zip(corners, corners[1:] + corners[:1]):
            mid = tuple((a[i] + b[i]) / 2 for i in range(3))
            mesh.tube([mid, apex], .024, 0, 6)
    return mesh


def casement(name,width,height,columns=1,transom_fraction=.75):
    """Plain service casement with narrow top lights, distinct from street sashes."""
    mesh=Mesh(name);b=.055
    mesh.box((0,0,-.13),(width,height,.025),1)
    mesh.box((0,0,-.09),(width-2*b,height-2*b,.02),2)
    for x in [-width/2+b/2,width/2-b/2]:
        mesh.box((x,0,-.025),(b,height,.11),0)
    for y in [-height/2+b/2,height/2-b/2]:
        mesh.box((0,y,-.025),(width-2*b,b,.11),0)
    th=-height/2+height*transom_fraction
    mesh.box((0,th,-.025),(width-2*b,.038,.10),0)
    for k in range(1,columns):
        x=-width/2+width*k/columns
        for low,high in [(-height/2+b,th-.019),(th+.019,height/2-b)]:
            mesh.box((x,(low+high)/2,-.025),(.045,high-low,.10),0)
    mesh.box((0,-height/2-.04,.015),(width+.12,.08,.25),3)
    return mesh
