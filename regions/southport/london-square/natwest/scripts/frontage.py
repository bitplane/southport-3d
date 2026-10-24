"""Bank fittings interpreted from private dated frontage photographs.

Coordinates are facade-local (across, height, outward), in metres. Tiny controls
are Fine geometry, omitted at District; recesses, hoods and slots remain.
"""
import math
from southport3d.geometry import Mesh


def cash_machine(frame, finish, metal, black, glass, white, green):
    def emit(m, mat):
        return finish(m, 'bank-frontage', [mat], frame)
    # Metal perimeter surrounds a genuinely inset working face.
    m=Mesh('ATM metal')
    for x in (-.405,.405):m.box((x,0,.105),(.09,.95,.13))
    for y in (-.435,.435):m.box((0,y,.105),(.72,.08,.13))
    emit(m,metal)
    m=Mesh('ATM recessed face');m.box((0,0,.045),(.72,.82,.04));emit(m,metal)
    m=Mesh('ATM screen hood')
    m.box((-.115,.305,.125),(.53,.07,.16))
    for x in (-.365,.135):m.box((x,.115,.105),(.035,.38,.12))
    m.box((-.115,.115,.077),(.47,.32,.022));emit(m,black)
    m=Mesh('ATM screen');m.box((-.115,.08,.091),(.35,.23,.014));emit(m,glass)
    m=Mesh('ATM cash outlet');m.box((.155,-.235,.09),(.34,.12,.055));emit(m,black)
    m=Mesh('ATM cash flap');m.box((.155,-.23,.124),(.27,.045,.018));emit(m,metal)
    m=Mesh('ATM receipt slot');m.box((.255,.285,.078),(.16,.055,.025));emit(m,black)
    m=Mesh('ATM card bezel');m.ellipsoid((.255,.09,.092),(.073,.073,.025),segments=24,rings=10);emit(m,green)
    m=Mesh('ATM card slot');m.box((.255,.09,.116),(.095,.012,.009));emit(m,black)
    # Sloping keyboard shelf with a turned-down front edge.
    m=Mesh('ATM keyboard shelf')
    verts=[(-.36,-.39,.06),(.36,-.39,.06),(.36,-.31,.06),(-.36,-.31,.06),
           (-.36,-.39,.25),(.36,-.39,.25),(.36,-.35,.25),(-.36,-.35,.25)]
    m.add(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
    emit(m,metal)
    m=Mesh('Fine ATM buttons')
    for x in (-.333,.103):
        for y in (-.025,.035,.095,.155):m.ellipsoid((x,y,.123),(.018,.012,.01),segments=12,rings=6)
    for x in (-.20,-.15,-.10):
        for j in range(4):m.box((x,-.33-j*.009,.11+j*.032),(.035,.012,.024))
    emit(m,white)
    m=Mesh('Fine ATM controls')
    m.box((.255,-.065,.078),(.06,.10,.025))
    for x in (-.405,.405):m.box((x,.26,.18),(.045,.06,.02))
    emit(m,white)


def entrance_steps(frame, finish, stone, black):
    # Four separate treads; radiused outer corners on the lowest two stones.
    for i,(width,front) in enumerate(((3.2,1.16),(2.82,.82),(2.42,.48),(2.20,.14))):
        top=.14*(i+1);r=.12 if i<2 else .035
        plan=[(-width/2,-.24),(width/2,-.24),(width/2,front-r)]
        for j in range(9):
            a=j*math.pi/16;plan.append((width/2-r+r*math.cos(a),front-r+r*math.sin(a)))
        for j in range(9):
            a=math.pi/2+j*math.pi/16;plan.append((-width/2+r+r*math.cos(a),front-r+r*math.sin(a)))
        n=len(plan);v=[(x,z,y) for z in ((-.16 if i==0 else top-.14),top) for x,y in plan]
        m=Mesh('Trim entrance step')
        m.add(v,[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(j,j+n,(j+1)%n+n,(j+1)%n) for j in range(n)])
        finish(m,'bank-frontage',[stone],frame)
    # Keep the graspable rail inside the 1.14 m half-width reveal. Only its
    # short mounting brackets reach the stone; the old slanted X coordinates
    # pushed the rail itself through the jamb.
    for side in (-1,1):
        m=Mesh('Door wall handrail')
        m.tube([(side*1.00,1.04,.66),(side*1.00,1.24,-.04)],.032,sides=12)
        for x,y,z in ((side*1.00,1.04,.66),(side*1.00,1.24,-.04)):
            m.tube([(x,y,z),(x+side*.16,y-.10,min(z,.14))],.022,sides=8)
        finish(m,'bank-frontage',[black],frame)
