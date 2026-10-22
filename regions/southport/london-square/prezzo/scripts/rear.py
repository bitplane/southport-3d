"""Rear wings and open escape stairs, calibrated from Nov 2020 Street View.

Metres are visual estimates. Exterior only: hidden rooms, ground yards and
neighbours are not inferred from the visible fire escapes.
"""
import math
from mathutils import Matrix,Vector
from southport3d.geometry import Mesh,face_matrix
from components import window,rectangle_frame


def beam(m,a,b,width,depth=None,material=0):
    """Rectangular steel/duct segment between 3-D points."""
    a,b=Vector(a),Vector(b);direction=(b-a).normalized()
    axis=Vector((0,0,1)) if abs(direction.z)<.9 else Vector((1,0,0))
    x=direction.cross(axis).normalized()*width/2
    y=direction.cross(x).normalized()*(depth or width)/2
    v=[tuple(c+sx*x+sy*y) for c in [a,b] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    m.add(v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)


def brick_courses(ob):
    """Keep running-bond beds horizontal on rear and perpendicular returns."""
    uv=ob.data.uv_layers.active.data
    for face in ob.data.polygons:
        if abs(face.normal.y)>.5:continue
        across=0 if abs(face.normal.z)>.5 else 2
        for index in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[index].vertex_index].co
            uv[index].uv=(v[across]/3.6,v.y/1.8)
    return ob


def add_rear(finish,instance,z0,mats,whitebrick,paint,steel,lead,duct):
    stone,trim,glass,dark,white=mats
    rear_mats=[stone,trim,glass,dark,white]
    # x limits / rear face / parapet: retain the two genuine stair recesses.
    wings=[('west',-32.2,-26.2,-43.7,18.55),
           ('central',-22.6,-19.3,-44.0,20.35),
           ('east',-14.4,-9.92,-41.2,15.10)]
    for label,left,right,rear,height in wings:
        width=right-left;frame=face_matrix((left,rear,z0),(0,-1,0))
        wall=Mesh('Envelope rear wing '+label)
        wall.box((width/2,height/2,-.17),(width,height,.34))
        side_depth=-37.1-rear
        wall.box((.17,height/2,-side_depth/2),(.34,height,side_depth))
        wall.box((width-.17,height/2,-side_depth/2),(.34,height,side_depth))
        if label=='west':
            apertures=[(u,y,w,2.02,cols,2) for y in [5.75,9.25,12.75,16.25] for u,w,cols in [(2.05,1.20,3),(4.22,.78,2)]]
        elif label=='central':
            apertures=[(u,y,1.02,1.27,3,1) for y in [5.8,9.3,12.8,16.3] for u in [width/2]]
            # One small high opening on the return, not a guessed fifth full row.
        else:
            apertures=[(2.2,y,1.48,1.80,3,2) for y in [5.75,9.25,12.75]]
        for u,y,w,h,cols,rows in apertures:
            wall.cut_box_from_ashlar((u,y,-.17),(w,h,.60))
            key=f'rear-{w}-{h}-{cols}-{rows}'
            instance(key,window(w,h,'detail','Window rear '+label,columns=cols,rows_per_sash=rows),'architecture',frame@Matrix.Translation((u,y,0)),rear_mats)
            dress=Mesh('Dressings rear lintel '+label)
            dress.box((u,y+h/2+.085,.015),(w+.16,.13,.12),0)
            dress.box((u,y-h/2-.055,.055),(w+.20,.10,.20),1)
            finish(dress,'architecture',[stone,lead],frame)
        if label=='central':
            # The apparent second column in the photograph belongs to the
            # perpendicular west return, not another row on the flat rear face.
            wall.cut_box_from_ashlar((.17,18.65,-3.60),(.60,.92,.92))
            return_frame=face_matrix((left-.01,-42.65,z0),(-1,0,0))
            for y in [5.8,9.3,12.8,16.3]:
                wall.cut_box_from_ashlar((.17,y,-1.35),(.60,1.27,1.02))
                instance('rear-return-sixlight',window(1.02,1.27,'detail','Window rear central return',columns=3,rows_per_sash=1),'architecture',return_frame@Matrix.Translation((0,y,0)),rear_mats)
                lintel=Mesh('Dressings rear return lintel')
                lintel.box((0,y+.72,.015),(1.18,.13,.12),0)
                lintel.box((0,y-.69,.055),(1.22,.10,.20),1)
                finish(lintel,'architecture',[stone,lead],return_frame)
        # The existing London terminal elevation owns this end of the return.
        if label=='east':wall.cut_box_from_ashlar((width-.17,height/2,-1.10),(.60,height+.10,2.21))
        wall.box((width/2,height/2,-side_depth+.17),(width-.68,height,.34))
        if label=='central':
            for u in [.85,width-.85]:wall.cut_box_from_ashlar((u,19.25,-side_depth+.17),(.90,1.40,.65))
            front=face_matrix((right,-37.1,z0),(0,1,0))
            for u in [.85,width-.85]:instance('rear-headhouse-front',window(.90,1.40,'detail','Window rear headhouse front'),'roof',front@Matrix.Translation((width-u,19.25,0)),rear_mats)
        brick_courses(finish(wall,'architecture',[whitebrick],frame))
        roof=Mesh('Roof rear wing '+label)
        roof.box((width/2,height-.08,-side_depth/2),(width-.04,.15,side_depth-.04))
        for u in [.08,width-.08]:roof.box((u,height+.02,-side_depth/2),(.20,.12,side_depth+.10))
        roof.box((width/2,height+.02,0),(width+.10,.12,.24))
        finish(roof,'roof',[lead],frame)
        # Painted downpipes have warm weathered collars, not arbitrary dirt decals.
        pipes=Mesh('Hardware rear pipes '+label)
        for u in [.38,width-.35]:
            pipes.tube([(u,1.2,.11),(u,height-.45,.11),(u-.10,height-.20,.11)],.045,0,8)
            for y in [2.0,5.5,9.0,12.5,16.0]:
                if y<height-.3:pipes.box((u,y,.11),(.12,.055,.14),1)
        finish(pipes,'architecture',[paint,duct],frame)
        if label=='west':
            # The terminal party face is visibly plain render; no false rear brick
            # course grid is projected onto that broad unfenestrated side.
            plain=Mesh('Envelope rear rendered west return')
            plain.box((-.015,height/2,-side_depth/2),(.025,height,side_depth-.02))
            finish(plain,'architecture',[stone],frame)
            roof_rail(finish,frame,width,side_depth,height,steel)
            antenna=Mesh('Hardware rear television aerials')
            for u in [1.0,3.7]:
                antenna.tube([(u,height,.4),(u,height+1.25,.4)],.018,0,6)
                antenna.tube([(u-.6,height+1.15,.4),(u+.6,height+1.15,.4)],.014,0,6)
                for j in range(7):
                    x=u-.5+j/6
                    antenna.tube([(x,height+1.15,.17),(x,height+1.15,.63)],.009,0,5)
            finish(antenna,'roof',[steel],frame)
        if label=='east':roof_rail(finish,frame,width,side_depth,height,steel)
    # Recess walls sit behind the two stair flights. The old flat rear wall is gone.
    for label,left,right,rear,height in [('west',-26.2,-22.6,-40.55,18.45),('east',-19.3,-14.4,-38.70,15.00)]:
        frame=face_matrix((left,rear,z0),(0,-1,0));width=right-left
        wall=Mesh('Envelope rear stair recess '+label)
        wall.box((width/2,height/2,-.16),(width,height,.32))
        levels=[4.9,8.4,11.9,15.4] if label=='west' else [4.9,8.4,11.9]
        for i,y in enumerate(levels):
            u=.65;h=2.25
            wall.cut_box_from_ashlar((u,y+h/2,-.16),(.90,h,.55))
            door=Mesh('Entrance rear escape '+label)
            door.box((u,y+h/2,-.18),(.90,h,.04),1)
            rectangle_frame(door,u,y+h/2,.9,h,.07,-.12,.08,0)
            # Glazed upper half, solid painted lower panel; no interior content.
            door.box((u,y+1.55,-.125),(.69,1.10,.02),2)
            for cy in [y+1.3,y+1.8]:door.box((u,cy,-.08),(.69,.035,.05),0)
            door.box((u,y+1.55,-.08),(.035,1.10,.05),0)
            if label=='west' and i==len(levels)-1:
                # The upper recess opening has a round-headed light in the
                # supplied close view; retain its outline, not a square substitute.
                spring=y+1.8;r=.45
                arc=[(u+r*math.cos(j*math.pi/32),spring+r*math.sin(j*math.pi/32),-.07) for j in range(33)]
                door.tube(arc,.025,0,8)
                for side in [-1,1]:
                    angles=[math.pi/2+side*j*math.pi/64 for j in range(33)]
                    points=[(u+r*math.cos(t),spring+r*math.sin(t)) for t in angles]
                    points.append((u-side*r,spring+r))
                    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))<0:points.reverse()
                    door.outline(points,-.14,-.025,1)
            finish(door,'architecture',[trim,stone,glass],frame)
        brick_courses(finish(wall,'architecture',[whitebrick],frame))
        stairs(finish,frame,width,levels,steel,lead)
        # Services alongside the recessed doors, with offsets at landings.
        service=Mesh('Hardware rear recess services '+label)
        service.tube([(width-.23,1.0,.12),(width-.23,height-.5,.12)],.065,0,8)
        for y in levels:
            service.tube([(.17,y+1.8,.13),(.17,y+.2,.13),(.34,y-.05,.13)],.035,0,8)
        finish(service,'architecture',[paint],frame)
    # The retained street mansard finishes against a vertical rendered end above
    # the lower eastern rear roof. Without this closure the old deck was open.
    end=Mesh('Envelope rear east upper gable')
    # A vertical closure shares only its edge with the deck; a solid top cap
    # would duplicate the deck's horizontal face and cause distant flicker.
    end.add([(x,y,0) for x,y in [(-19.3,15.00),(-9.6,15.00),(-9.6,15.70),(-11.4,18.30),(-19.3,18.30)]],[(0,1,2,3,4)])
    # Recess wall is 300 mm behind this plane. Close the underside of that
    # offset at its actual 15 m top; no open 100 mm band or see-through soffit.
    end.add([(-19.3,15.0,0),(-19.3,15.0,-.30),(-14.4,15.0,-.30),(-14.4,15.0,0)],[(0,1,2,3)])
    finish(end,'roof',[stone],face_matrix((0,-39,z0),(0,-1,0)))
    # Central wing's top return window and the conspicuous angular white duct.
    frame=face_matrix((-22.6,-44,z0),(0,-1,0))
    m=Mesh('Envelope rear angular duct')
    for a,b in [((2.85,20.12,.24),(2.85,17.05,.24)),((2.85,17.05,.24),(3.62,16.15,.95)),((3.62,16.15,.95),(3.62,15.60,.95))]:beam(m,a,b,.60,.54)
    finish(m,'architecture',[duct],frame)
    dish=Mesh('Hardware rear satellite dish')
    dish.ellipsoid((.13,15.68,.40),(.24,.24,.045),0,20,10)
    dish.tube([(.13,15.48,.15),(.13,15.48,.60),(.13,15.63,.70)],.022,0,8)
    finish(dish,'architecture',[steel],frame)
    # Small high return opening, on west side of the projecting central wing.
    return_frame=face_matrix((-22.61,-40.4,z0),(-1,0,0))
    # Actual opening through the west return wall; dark backing closes the view.
    m=Mesh('Dressings rear high return reveal')
    rectangle_frame(m,0,18.65,1.12,1.12,.10,.025,.10,0)
    finish(m,'architecture',[stone],return_frame)
    instance('rear-high-return',window(.92,.92,'detail','Window rear high return',columns=3,rows_per_sash=1),'architecture',return_frame@Matrix.Translation((0,18.65,0)),rear_mats)


def roof_rail(finish,frame,width,depth,height,steel):
    main=Mesh('Envelope rear roof rails');fine=Mesh('Hardware rear roof crossbars')
    # Front and two returns; photograph shows an open X-braced parapet railing.
    for a,b in [((.10,0),(width-.10,0)),((.10,0),(.10,-depth+.2)),((width-.10,0),(width-.10,-depth+.2))]:
        length=math.dist(a,b);n=max(1,math.ceil(length/1.4))
        for y in [height+.12,height+.95]:beam(main,(a[0],y,a[1]),(b[0],y,b[1]),.035)
        for i in range(n+1):
            t=i/n;u=a[0]+(b[0]-a[0])*t;d=a[1]+(b[1]-a[1])*t
            beam(main,(u,height+.06,d),(u,height+.99,d),.04)
        for i in range(n):
            p=[(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t) for t in [i/n,(i+1)/n]]
            for lo,hi in [(.16,.90),(.90,.16)]:beam(fine,(p[0][0],height+lo,p[0][1]),(p[1][0],height+hi,p[1][1]),.018)
    finish(main,'roof',[steel],frame);finish(fine,'roof',[steel],frame)


def stairs(finish,frame,width,levels,steel,lead):
    """Parallel depth-wise flights with open wells and a separate return lane.

    The visible photo supports narrow flights and small projecting landings.
    Exact plan dimensions and the concealed lower continuation are estimated.
    """
    structure=Mesh('Envelope rear escape structure')
    fine=Mesh('Hardware rear escape balusters')
    grate=Mesh('Ornament rear escape grating')
    u0=width-2.05;flight_width=.85;divider=u0+.94;outer=u0+1.90
    near,far=.95,4.25;front=5.10
    # The extra lower half-landing resolves the previously suspended 1.4 m end.
    floors=[0.0,levels[0]/2,*levels]

    def rail(a,b,y):
        for height in [.48,1.00]:beam(structure,(a[0],y+height,a[1]),(b[0],y+height,b[1]),.028)
        n=max(1,math.ceil(math.dist(a,b)/.85))
        for j in range(n+1):
            t=j/n;u=a[0]+t*(b[0]-a[0]);d=a[1]+t*(b[1]-a[1])
            beam(fine,(u,y+.04,d),(u,y+1.01,d),.023)

    def deck(x0,x1,d0,d1,y):
        structure.box(((x0+x1)/2,y-.035,(d0+d1)/2),(x1-x0,.07,d1-d0))
        # Narrow surface strips stop at each deck edge; none span the open well.
        n=max(1,math.ceil((d1-d0)/.12))
        for i in range(n):
            d=d0+(i+.5)*(d1-d0)/n
            grate.box(((x0+x1)/2,y+.004,d),(x1-x0-.02,.008,.012))

    # Slender posts extend to the building datum instead of ending in midair.
    for u in [u0-.04,outer]:
        for d in [.12,front]:
            beam(structure,(u,0,d),(u,floors[-1]+1.02,d),.055)
            structure.box((u,.025,d),(.18,.05,.18))
    for y in floors:
        if y==0:
            # Open wall-side edge is the estimated exit to the concealed rear yard.
            deck(u0-.08,outer,.02,near,y)
            rail((u0-.08,.02),(u0-.08,near),y)
            rail((outer,.02),(outer,near),y)
            continue
        # U-shaped level surface: doorway bridge, return lane and outer landing.
        # The stair lane between near/far stays empty so flights pass through it.
        deck(.18,outer,.02,near,y)
        deck(divider,outer,near,far,y)
        deck(u0-.08,outer,far,front,y)
        # No rail crosses either mouth of the stair lane. The side rail of the
        # well protects the return walkway without blocking access at its ends.
        rail((u0-.08,near),(u0-.08,front),y)
        rail((divider,near),(divider,far),y)
        rail((outer,.12),(outer,front),y)
        rail((u0-.08,front),(outer,front),y)
        if u0-.08>.18:rail((.18,near),(u0-.08,near),y)
    for bottom,top in zip(floors,floors[1:]):
        n=math.ceil((top-bottom)/.20);run=(far-near)/n;rise=(top-bottom)/n
        for i in range(n):
            d=near+(i+.5)*run;y=bottom+(i+1)*rise
            structure.box((u0+flight_width/2,y-.025,d),(flight_width,.05,run+.006))
            if i%3==0:
                for u in [u0-.025,u0+flight_width+.025]:
                    beam(fine,(u,y,d),(u,y+.98,d),.020)
        for u in [u0-.025,u0+flight_width+.025]:
            beam(structure,(u,bottom-.03,near),(u,top-.03,far),.085,.045)
            for h in [.48,1.00]:beam(structure,(u,bottom+h,near),(u,top+h,far),.028)
    ob=finish(structure,'architecture',[steel],frame)
    ob['stair_floor_levels']=floors
    ob['stair_lane_u']=u0+flight_width/2
    ob['return_lane_u']=(divider+outer)/2
    ob['stair_well_near']=near;ob['stair_well_far']=far
    finish(fine,'architecture',[steel],frame)
    finish(grate,'architecture',[lead],frame)
