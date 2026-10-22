"""Authored Prezzo joinery and Ionic pilasters, with explicit detail controls.

Local XY is the elevation, +Z outward. Joined bars have disjoint front faces:
intersecting coplanar boxes previously flickered at sash and frame junctions.
"""
import math,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(os.environ.get('SOUTHPORT_REPO_ROOT',Path(__file__).resolve().parents[5]))/'lib'))
from southport3d.geometry import Mesh


def rectangle_frame(m,cx,cy,width,height,border,out,depth,material=1):
    for y in [cy-height/2+border/2,cy+height/2-border/2]:
        m.box((cx,y,out),(width,border,depth),material)
    for x in [cx-width/2+border/2,cx+width/2-border/2]:
        m.box((x,cy,out),(border,height-2*border,depth),material)


def window(width,height,level='detail',name='Window',shop_override=False,raised_shop=False,apron_window=False,columns=3,rows_per_sash=2):
    m=Mesh(name);w=width/2;h=height/2;shop=shop_override or (width>2.2 and height>3)
    # The backing extends under sill/architrave so distant receivers are covered.
    m.box((0,-.06,-.205),(width+.27,height+.12,.025),0)
    # Street photographs show slender painted joinery inside the masonry reveal.
    border=.065
    rectangle_frame(m,0,0,width,height,border,-.035,.09)
    if not apron_window:m.box((0,-h-.06,.055),(width+.27,.12,.13),0)
    iw=width-2*border;ih=height-2*border
    if raised_shop:
        # Two separate glazing registers with a broad stone spandrel between.
        # Heights are calibrated from the oblique property photograph.
        m.box((0,.25,-.015),(width-.20,.90,.12),0)
        for lo,hi in [(-h,-.20),(.70,h)]:
            cy=(lo+hi)/2;hh=hi-lo
            m.box((0,cy,-.12),(width-.20,hh-.14,.025),2)
            rectangle_frame(m,0,cy,width,hh,border,-.035,.09)
            for x in [-width/6,width/6]:
                m.box((x,cy,-.035),(.040,hh-.13,.08),1)
            if lo<0:
                m.box((0,cy+.30,-.033),(width-.13,.045,.08),1)
        return m
    if shop:
        m.box((0,0,-.12),(iw,ih,.025),2)
        transom=h-.67
        m.box((0,transom,-.035),(iw,.045,.08),1)
        # Side lights and tall central pane, divided at the transom, not overlapped.
        for x in [-width*.32,width*.32]:
            for a,b in [(-h+border,transom-.0225),(transom+.0225,h-border)]:
                m.box((x,(a+b)/2,-.035),(.040,b-a,.08),1)
        if level=='detail':
            # Fine glazing beads on the outside reveal; no shared face with frame.
            rectangle_frame(m,0,0,iw,ih,.014,-.067,.025)
    else:
        # Three lights across, two rows in each sash (six-over-six).
        for a,b,out in [(-h+border,-.025,-.075),(.025,h-border,-.105)]:
            sh=b-a;cy=(a+b)/2
            m.box((0,cy,out-.045),(iw,sh,.02),2)
            rectangle_frame(m,0,cy,iw,sh,.032,out,.06)
            innerw=iw-.064;innerh=sh-.064
            if rows_per_sash>1:m.box((0,cy,out+.002),(innerw,.018,.035),1)
            for x in [-innerw/2+innerw*i/columns for i in range(1,columns)]:
                for lo,hi in ([(cy-innerh/2,cy-.009),(cy+.009,cy+innerh/2)] if rows_per_sash>1 else [(cy-innerh/2,cy+innerh/2)]):
                    m.box((x,(lo+hi)/2,out+.002),(.018,hi-lo,.035),1)
            if level=='detail':
                rectangle_frame(m,0,cy,innerw,innerh,.009,out-.012,.018)
        m.box((0,0,-.045),(iw,.05,.08),1)
        if level=='detail':
            # Sash lifts on lower meeting rail, kept inside window bounds.
            for x in [-iw*.28,iw*.28]:
                m.box((x,-.07,.04),(.10,.035,.025),3)
    return m


def pilaster(level='detail',name='Pilaster'):
    m=Mesh(name);fine=level=='detail';walk=level=='walk'
    m.box((0,-.06,.18),(.70,.12,.36))
    # Profiled bases, neck and abacus at the same dimensions at all levels.
    for y,w,h,d in [(.09,.70,.18,.38),(.20,.64,.04,.35),(.255,.57,.07,.30),(.315,.54,.05,.29),
                      (3.82,.55,.07,.31),(3.88,.61,.05,.34),(4.02,.67,.13,.36),(4.13,.79,.075,.40),(4.19,.82,.045,.42)]:
        m.box((0,y,d/2),(w,h,d))
    # Flat side/back shell, with the front authored as concave flutes.
    bottom,top=.34,3.78;half=.24
    m.add([(-half,bottom,0),(half,bottom,0),(half,top,0),(-half,top,0),
           (-half,bottom,.23),(half,bottom,.23),(half,top,.23),(-half,top,.23)],
          [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    nx,ny=(112,36) if fine else (28,8) if walk else (1,1)
    verts=[]
    for j in range(ny+1):
        y=bottom+(top-bottom)*j/ny
        for i in range(nx+1):
            x=-half+2*half*i/nx;depth=0
            if fine or walk:
                for c in [-.18,-.12,-.06,0,.06,.12,.18]:
                    dx=(x-c)/.022;end=max(0,(.43-y)/.07,(y-3.68)/.07)
                    d=1-dx*dx-end*end
                    if d>0:depth=.035*math.sqrt(d)
            verts.append((x,y,.23-depth))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
    m.add(verts,faces)
    if level!='district':
        n=64 if fine else 16
        for side in [-1,1]:
            pts=[]
            for i in range(n+1):
                a=math.pi/2+i*math.tau*1.45/n;r=.14*(1-.88*i/n)
                pts.append((side*.28+side*r*math.cos(a),4.015+r*math.sin(a),.435+.012*i/n))
            m.tube(pts,.023,0,10 if fine else 5)
        if fine:
            # Small egg-and-dart row beneath the scrolls; restrained interpretation.
            for x in [-.16,-.08,0,.08,.16]:
                pts=[(x+.027*math.sin(t),3.94+.052*math.cos(t),.405) for t in [j*math.tau/24 for j in range(25)]]
                m.tube(pts,.009,0,6)
            for y,d in [(.235,.34),(.30,.30),(3.84,.32)]:
                m.tube([(-.28,y,d),(.28,y,d)],.012,0,8)
    # Shallow applied relief: base meets the existing grey skirt at +.06 m.
    # Calibrated relationship from screenshot-20261022-103827, not a survey.
    depth_scale=.06/.38
    m.vertices=[(x,y,z*depth_scale) for x,y,z in m.vertices]
    return m


def build_lod(name,settings,asset_dir):
    if settings['kind']=='window':return window(settings['width'],settings['height'],settings['level'],name).finish([])
    from surface_cleanup import clean
    ob=pilaster(settings['level'],name).finish([]);clean(ob.data);return ob
