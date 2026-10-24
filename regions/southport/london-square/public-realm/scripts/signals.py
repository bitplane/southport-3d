"""London Square signal family, calibrated to privately supplied snag photograph.

Dimensions remain estimates. No manufacturer or live signal phase is asserted.
Axes: front is -Y; material slots follow southport3d.street.
"""
import math
from mathutils import Matrix
from southport3d.geometry import Mesh


def disc(mesh, x, y, z, radius, material, segments, depth=.008):
    part=Mesh('disc')
    part.lathe((0,0),[(0,radius),(depth,radius)],segments,material)
    part.transform(Matrix.Translation((x,y,z)) @ Matrix.Rotation(math.pi/2,4,'X'))
    mesh.add(part.vertices,part.faces,material)


def visor(mesh,z,radius,steps):
    # Open underneath; tapered circular shell, not a flat rectangular awning.
    vertices=[]
    for i in range(steps+1):
        angle=math.radians(-25+230*i/steps)
        length=.115+.065*max(0,math.sin(angle))
        for r,y in [(radius,-.229),(radius+.008,-.229),(radius,-.229-length),(radius+.008,-.229-length)]:
            vertices.append((r*math.cos(angle),y,z+r*math.sin(angle)))
    faces=[]
    for i in range(steps):
        a=4*i;b=a+4
        faces.extend([(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a,a+1,b+1,b),(a+2,b+2,b+3,a+3)])
    faces.extend([(0,2,3,1),(4*steps,4*steps+1,4*steps+3,4*steps+2)])
    mesh.add(vertices,faces,0)


def person(mesh,z,walking,material,segments):
    # Authored silhouettes: standing red figure and striding green figure.
    points=([(-.016,.037),(.015,.031),(.036,.006),(.055,.001),(.051,-.011),(.027,-.004),(.010,.011),(.009,-.014),(.044,-.058),(.032,-.067),(-.002,-.033),(-.032,-.066),(-.045,-.060),(-.016,-.017),(-.017,.010),(-.036,-.010),(-.047,-.004),(-.027,.024)] if walking else
            [(-.024,.032),(.024,.032),(.035,.016),(.035,-.026),(.024,-.026),(.021,.010),(.019,-.070),(.005,-.070),(0,-.022),(-.005,-.070),(-.019,-.070),(-.021,.010),(-.024,-.026),(-.035,-.026),(-.035,.016)])
    # In the X/Z plane, clockwise order points towards +Y; reverse for front.
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
    if area<0:points.reverse()
    mesh.add([(x,-.241,z+h) for x,h in points],[tuple(range(len(points)))],material)
    disc(mesh,0,-.241,z+.058,.018,material,segments,.003)


def signal(kind,level='detail',name=None,offset=False):
    pedestrian=kind=='pedestrian';fine=level=='detail';coarse=level=='district'
    n={'detail':32,'walk':16,'district':8}[level]
    mesh=Mesh(name or kind)
    centre=2.4 if pedestrian else 3.05
    height=.58 if pedestrian else .90
    profile=[(0,.057),(.12,.057)]
    if offset:profile += [(z,.045) for z in [1.65,1.75,1.85,1.95,2.05,2.15,2.2]]
    profile.append((centre+height/2-.05,.045))
    mesh.lathe((0,0),profile,n,1)
    # Rear brackets attach a separate dark housing to the post.
    for h in [centre-height*.35,centre+height*.35]:
        mesh.box((0,-.065,h),(.065,.15,.045),0)
    if not pedestrian:
        mesh.box((0,-.125,centre),(.43,.025,height+.12),2)
        mesh.box((0,-.143,centre),(.395,.012,height+.085),0)
    mesh.box((0,-.18,centre),(.285,.10,height),0)
    lens_heights=[centre+.135,centre-.135] if pedestrian else [centre+.285,centre,centre-.285]
    for i,z in enumerate(lens_heights):
        disc(mesh,0,-.231,z,.106,8 if pedestrian else 4+i,n)
        visor(mesh,z,.112,{'detail':20,'walk':10,'district':5}[level])
        if pedestrian:person(mesh,z,i==1,4+2*i,max(8,n//2))
        if fine:
            for x in [-.124,.124]:
                disc(mesh,x,-.232,z+.113,.004,1,8,.003)
    if pedestrian:
        mesh.box((0,-.10,1.05),(.16,.14,.27),3)
        mesh.box((0,-.177,1.05),(.125,.016,.225),0)
        disc(mesh,0,-.188,1.0,.022,2,n,.012)
        if not coarse:
            mesh.box((0,-.188,1.105),(.085,.004,.032),2)
    if offset:
        vertices=[]
        for x,y,z in mesh.vertices:
            t=max(0,min(1,(z-1.65)/.55))
            vertices.append((x+.30*t*t*(3-2*t),y,z))
        mesh.vertices=vertices
    return mesh
