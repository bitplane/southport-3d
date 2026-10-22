"""Narrow recessed terminal bays, calibrated from exterior views and user review."""
from mathutils import Matrix
from southport3d.geometry import Mesh,face_matrix
from components import window,rectangle_frame


def add_end_bays(finish,instance,z0,mats):
    stone,trim,glass,dark,white=mats
    specifications=[('Lord flats',(-30.4,-23.75),(0,1,0),1.8,15.0,15.25),
                    ('London inset',(-9.92,-41.2),(1,0,0),2.2,15.0,4.3)]
    for label,origin,normal,w,h,depth in specifications:
        frame=face_matrix((*origin,z0),normal);cx=w/2
        wall=Mesh('Envelope end bay '+label)
        wall.box((cx,h/2,-.21),(w,h,.42))
        # Real apertures and reveals: main cornice stops before this plain bay.
        for cy,wh in [(1.55,3.10),(4.05,.90),(6.95,1.95),(10.35,1.85),(13.50,1.75)]:
            ww=1.05 if cy<5 else .78
            wall.cut_box_from_ashlar((cx,cy,-.21),(ww,wh,.60))
        # Side return and plain provisional backing close the narrow wing.
        wall.box((.10,h/2,-depth/2),(.20,h,depth))
        wall.box((w-.10,h/2,-depth/2),(.20,h,depth))
        wall.box((cx,h/2,-depth+.10),(w-.40,h,.20))
        finish(wall,'architecture',[stone],frame)
        for cy,wh in [(6.95,1.95),(10.35,1.85),(13.50,1.75)]:
            instance('terminal-'+str(wh),window(.78,wh,'detail','Window terminal '+label),'architecture',frame@Matrix.Translation((cx,cy,0)),mats)
            surround=Mesh('Dressings terminal '+label)
            rectangle_frame(surround,cx,cy,1.05,wh+.22,.075,.025,.10,0)
            finish(surround,'architecture',[stone],frame)
        door=Mesh('Entrance recessed '+label)
        door.box((cx,1.55,-.30),(1.05,3.10,.06),3)
        rectangle_frame(door,cx,1.55,1.05,3.10,.07,-.25,.08,3)
        for cy in [.55,1.28,2.10,2.70]:
            rectangle_frame(door,cx,cy,.78,.48,.035,-.205,.04,3)
        # Glazed rectangular fanlight above entrance; no invented lettering.
        door.box((cx,4.05,-.24),(1.05,.90,.025),2)
        rectangle_frame(door,cx,4.05,1.05,.90,.07,-.16,.08,1)
        door.box((cx,4.05,-.13),(.035,.76,.035),1)
        finish(door,'shopfront',mats,frame)
        surrounds=Mesh('Dressings entrance '+label)
        rectangle_frame(surrounds,cx,1.55,1.27,3.25,.11,.025,.14,0)
        surrounds.box((cx,3.45,.055),(1.40,.16,.20),0)
        surrounds.box((cx,.04,-.12),(1.17,.08,.50),0)
        finish(surrounds,'architecture',[stone],frame)
        hardware=Mesh('Hardware terminal '+label)
        hardware.box((cx+.34,1.36,-.17),(.055,.21,.035),0)
        hardware.box((cx-.65,1.48,.08),(.12,.25,.045),0)
        finish(hardware,'shopfront',[dark],frame)
        roof=Mesh('Roof terminal '+label)
        roof.box((cx,h+.04,-depth/2),(w+.10,.12,depth+.08))
        finish(roof,'roof',[stone],frame)
