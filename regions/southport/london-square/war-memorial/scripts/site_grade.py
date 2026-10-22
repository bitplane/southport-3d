"""Estimated NW fall and level colonnade foundations; see ground_grade_study.json."""
import math
from mathutils import Vector

GRADIENT = -.022                 # dz / d(site Y); +Y points northwest
FOUNDATION_BOTTOM = -.60
LAMP_CAP = .35
LAMP_SHIFT = LAMP_CAP - .48


def offset(y):
    return GRADIENT*y


def ground(y):
    return -.07 + offset(y)


def colonnade_base(ns, code, collection):
    Mesh, finish = ns['Mesh'], ns['finish']
    # A level portico, with three broad treads. The lowest riser disappears
    # into the ascending pavement at the southeast end, as in the photographs.
    m = Mesh(code+' central entrance steps')
    for bottom, top, depth in [(FOUNDATION_BOTTOM,-.04,5.90),(-.04,.14,5.38),(.14,.32,4.90)]:
        # Physical narrow vertical joints in the large tread stones.
        width=13.70; count=12; pitch=width/count
        for i in range(count):
            m.box((-width/2+(i+.5)*pitch,0,(bottom+top)/2),
                  (pitch-.003,depth,top-bottom),1+(i%3))
    ob=finish(m,collection,.003)
    ob['base_part']='portico_steps';ob['top_z_m']=.32
    for sign in (-1,1):
        m=Mesh(code+' chamber vertical plinth '+str(sign))
        centre=sign*9.50
        # End chambers have upright bases, not a staircase wrapped around
        # their exterior. The broad cap covers the formerly exposed low jambs.
        for bottom,top,w,d in [(FOUNDATION_BOTTOM,.10,5.36,4.78),
                                (.10,.52,5.30,4.70),(.52,.58,5.34,4.74)]:
            m.box((centre,0,(bottom+top)/2),(w,d,top-bottom),1)
        ob=finish(m,collection,.003)
        ob['base_part']='chamber_plinth'
        ob['base_status']='Vertical base and narrow foot/cap evidenced; dimensions estimated'


def lamp_plinth(ns,x,y,collection):
    m=ns['Mesh']('Bromsgrove lamp stone plinth')
    m.box((x,y,(FOUNDATION_BOTTOM+.21)/2),(1.40,1.04,.21-FOUNDATION_BOTTOM),1)
    m.box((x,y,(.21+LAMP_CAP)/2),(1.42,1.06,LAMP_CAP-.21),1)
    ob=ns['finish'](m,collection,.003)
    ob['base_part']='single_lamp_plinth'
    ob['ground_datum_status']='Footing extends below estimated NW-falling pavement'
    return ob


def apply_to_site(context,lamps,guides):
    """Slope paving; keep lamp shafts and bollards upright."""
    for ob in context.objects:
        if ob.type!='MESH':continue
        if ob.name.startswith('Island bollards'):
            # Each bollard is a separate connected profile in this mesh.
            # Its vertices retain the horizontal cross sections.
            for v in ob.data.vertices:
                y=min(range(-11,12,3),key=lambda q:abs(v.co.y-q))
                v.co.z+=offset(y)
        elif ob.name.startswith('Continuous paving beneath clustered lamps'):
            for v in ob.data.vertices:v.co.z+=offset(9 if v.co.y>0 else -9)
        else:
            for v in ob.data.vertices:v.co.z+=offset(v.co.y)
        ob['ground_grade_dz_dy']=GRADIENT
    for ob in lamps.objects:
        ob.location.z+=offset(ob.location.y)
        ob['ground_grade_dz_dy']=GRADIENT
    for ob in guides.objects:
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co.z+=offset(v.co.y)
        else:ob.location.z+=offset(ob.location.y)


def inspection_floor(floor,focus):
    floor.rotation_euler.x=math.atan(GRADIENT) if focus in ('NE','SW','lamps') else 0
    floor.location.z=-.0075 if focus in ('NE','SW','lamps') else -.003
