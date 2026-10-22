"""Editable shallow reliefs constructed from catalogued photographs.

Shapes are traced/constructed from the catalogued photographs. No photograph is
used as a model colour texture. The two figures use traced depth layers and a
bounded shading-gradient residual; see sculpt_figures.py. Depth and hidden
surfaces remain estimates, not photogrammetry. Coordinates are metres in panel space.
"""
import math
from pathlib import Path
from geometry import Mesh, smooth_path, TAU

RELIEF_DATA=Path(__file__).resolve().parents[1]/'research/relief-data'

def mourning():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'mourning.npz','Mourning figure — traced continuous surface')

def victory():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'victory.npz','Victory Britannia — traced continuous surface')

def salute_wreath():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'salute-wreath.npz','Salute laurel wreath — traced continuous surface')

def path(m, xy, z=.035, r=.008, mat=0):
    m.tube(smooth_path([(x,y,z) for x,y in xy],5),r,mat,8,.7)

def leaf(m, a, b, width, depth=.026, mat=0):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;l=max(math.hypot(dx,dy),1e-5);nx,ny=-dy/l,dx/l
    # Smooth lancet-shaped carved leaf, curved both along its length and across it.
    # This replaces the angular pyramid proxy used in the first research render.
    verts=[];faces=[];rows=10;cols=6
    for j in range(rows+1):
        t=j/rows;w=width*math.sin(math.pi*t)**.85
        for k in range(cols+1):
            q=2*k/cols-1
            ridge=math.sin(math.pi*t)**.65*(1-q*q)
            verts.append((ax+dx*t+nx*w*q,ay+dy*t+ny*w*q,.018+depth*ridge))
    for j in range(rows):
        for k in range(cols):
            i=j*(cols+1)+k;faces.append((i,i+cols+1,i+cols+2,i+1))
    m.add(verts,faces,mat)

def rosette(m, centre, radius, depth=.035, petals=12):
    x,y=centre
    m.ring((x,y,depth*.3),radius*.92,radius*.055)
    for i in range(petals):
        a=TAU*i/petals
        leaf(m,(x+radius*.28*math.cos(a),y+radius*.28*math.sin(a)),
             (x+radius*.93*math.cos(a),y+radius*.93*math.sin(a)),radius*.15,depth)
    m.ring((x,y,depth*.9),radius*.26,radius*.07)
    m.ellipsoid((x,y,depth*.7),(radius*.20,radius*.20,depth*.4),segments=16,rings=6)

def wreath(m, centre, radius, band=.07, flowers=False, depth=.04):
    x,y=centre;m.ring((x,y,depth*.45),radius,band*.64,segments=80,depth_scale=.45)
    for i in range(36):
        a=TAU*i/36;side=1 if i<18 else -1
        for q in (-.5,.45):
            r=radius+q*band
            a2=a+side*.14
            leaf(m,(x+r*math.cos(a),y+r*math.sin(a)),
                 (x+(r+band*.3)*math.cos(a2),y+(r+band*.3)*math.sin(a2)),band*.24,depth)
    if flowers:
        for a in (-1.9,-1.55,-1.2,.3,2.85):
            rosette(m,(x+radius*math.cos(a),y+radius*math.sin(a)),band*.50,depth*.8,8)
    for a in (-math.pi/2,math.pi/2):
        cx=x+radius*math.cos(a);cy=y+radius*math.sin(a)
        m.outline([(cx-band*.25,cy-band*.65),(cx+band*.25,cy-band*.65),
                   (cx+band*.3,cy+band*.65),(cx-band*.3,cy+band*.65)],.015,.065)

def crossed_torches():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'crossed-torches.npz','Crossed inverted torches — traced continuous surface')

def crossed_torches_legacy_proxy():
    m=Mesh('Crossed inverted torches and wreath')
    wreath(m,(0,0),.32,.10,False,.045)
    for sign in (-1,1):
        a=(-sign*.42,.43);b=(sign*.46,-.49)
        path(m,[a,b],.066,.037)
        # Narrow longitudinal flutes in the torch handles.
        for q in (-.015,0,.015):
            path(m,[(a[0]+q,a[1]-.055),(b[0]+q,b[1]+.13)],.085,.0045)
        m.ring((a[0],a[1],.06),.087,.018,segments=40,depth_scale=.7)
        path(m,[(a[0]-.025,a[1]-.07),(a[0]-.018,a[1]-.36),(a[0]-.03,a[1]-.49)],.046,.013)
        path(m,[(a[0]+.022,a[1]-.07),(a[0]+.03,a[1]-.40),(a[0]+.02,a[1]-.48)],.047,.009)
        # Inverted flames point down; three individually curved lobes.
        for q in (-1,0,1):
            x=b[0]+q*.037;y=b[1]
            pts=[(x-sign*.075,y+.11),(x+sign*.052,y+.05),(x+sign*.10,y-.05),
                 (x+sign*.13,y-.13),(x+sign*.018,y-.085),(x-sign*.042,y-.02)]
            m.outline(smooth_path(pts+[pts[0]],4)[:-1],.025,.07+q*.004)
            path(m,[(x,y+.07),(x+sign*.045,y-.01),(x+sign*.10,y-.10)],.078,.005)
    m.ellipsoid((0,0,.087),(.095,.025,.012),segments=24,rings=6)
    m.ring((0,.50,.046),.065,.010,segments=40)
    path(m,[(-.16,.30),(0,.48),(.16,.30)],.023,.008)
    return m

def brazier(m,x,y,scale=1,inverted=False):
    q=Mesh('brazier');s=scale
    q.outline([(x-.075*s,y-.16*s),(x+.075*s,y-.16*s),(x+.055*s,y-.13*s),
               (x+.038*s,y+.10*s),(x+.083*s,y+.14*s),(x+.088*s,y+.18*s),
               (x-.088*s,y+.18*s),(x-.083*s,y+.14*s),(x-.038*s,y+.10*s),
               (x-.055*s,y-.13*s)],.018,.048)
    for a in (-.045,-.026,0,.026,.045):
        path(q,[(x+a*s,y-.12*s),(x+a*.7*s,y+.09*s)],.057,.0035*s)
    for yy,ww in [(-.15,.075),(-.115,.053),(.10,.05),(.135,.082),(.18,.09)]:
        path(q,[(x-ww*s,y+yy*s),(x+ww*s,y+yy*s)],.059,.006*s)
    for i in range(5):
        xx=x+(i-2)*.027*s
        q.outline([(xx-.022*s,y+.18*s),(xx+.025*s,y+.18*s),(xx+.015*s,y+.22*s),
                   (xx+.005*s,y+.25*s),(xx-.011*s,y+.215*s)],.024,.050)
    if inverted:
        q.vertices=[(vx,2*y-vy,vz) for vx,vy,vz in q.vertices]
    m.add(q.vertices,q.faces)

def sword(m,a,b,width=.03,z=.035):
    dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);nx,ny=-dy/l,dx/l
    m.outline([(a[0]-nx*width,a[1]-ny*width),(a[0]+nx*width,a[1]+ny*width),
               (b[0]+nx*width*.65,b[1]+ny*width*.65),(b[0]+dx*.03,b[1]+dy*.03),
               (b[0]-nx*width*.65,b[1]-ny*width*.65)],.018,z)
    hx=a[0]-dx*.16;hy=a[1]-dy*.16
    path(m,[(hx,hy),a],z+.006,width*.6)
    path(m,[(a[0]-nx*width*2.4,a[1]-ny*width*2.4),(a[0]+nx*width*2.4,a[1]+ny*width*2.4)],z+.01,width*.5)
    m.ellipsoid((hx,hy,z),(.027,.026,.017),segments=14,rings=6)
    for i in range(5):
        t=(i+1)/7
        cx=hx+(a[0]-hx)*t;cy=hy+(a[1]-hy)*t
        path(m,[(cx-nx*width*.6,cy-ny*width*.6),(cx+nx*width*.6,cy+ny*width*.6)],z+.021,.003)

def festoon(m, points, radius=.034):
    smooth=smooth_path(points,5)
    path(m,points,.034,radius)
    for i in range(0,len(smooth),3):
        x,y=smooth[i]
        rosette(m,(x,y),radius*.72,.048,7)

def helmet(m,x,y,s=.3,flip=False):
    pts=[(-.48,-.42),(.18,-.42),(.05,-.28),(.19,-.15),(.38,-.10),(.29,.18),
         (.10,.36),(-.20,.36),(-.37,.19),(-.42,-.02),(-.15,.09),(-.20,-.13)]
    k=-1 if flip else 1
    m.outline([(x+k*px*s,y+py*s) for px,py in pts],.028,.069)
    path(m,[(x+k*px*s,y+py*s) for px,py in [(-.18,-.12),(-.21,.13),(-.08,.25),(.12,.25),(.27,.10)]],.076,.008)
    for i in range(19):
        a=.10+i*math.pi*.88/18
        xx=x-math.cos(a)*.34*s;yy=y+.14*s+math.sin(a)*.31*s
        leaf(m,(xx,yy),(xx-math.cos(a)*.15*s,yy+math.sin(a)*.16*s),.018*s,.052)

def wing(m,root,tip,s=.2,flip=False):
    x,y=root;tx,ty=tip
    for i in range(8):
        t=i/8
        a=(x+t*(tx-x)*.30,y+t*(ty-y)*.30)
        b=(tx+(i-3)*s*.10,ty-i*s*.12)
        leaf(m,a,b,s*.065,.045-i*.001)

def trophy(kind):
    from sculpt_surface import mesh_from_surface
    if kind not in ('wreath','pelta','victory'):raise ValueError(kind)
    return mesh_from_surface(RELIEF_DATA/('trophy-'+kind+'.npz'),
                             'Classical trophy '+kind+' — traced continuous surface')

def trophy_legacy_proxy(kind):
    m=Mesh('Classical trophy '+kind)
    if kind=='pelta':
        for x in (-.87,.87):brazier(m,x,0,1.1)
        sword(m,(.45,.07),(-.65,.07),.025)
        path(m,[(-.70,-.03),(.72,-.03)],.027,.013)
        # Pelta: central crescent shield with outward curving terminal lobes.
        pts=[(-.32,.17),(-.21,.17),(-.14,.12),(-.12,.055),(.12,.055),(.14,.12),(.21,.17),(.32,.17),
             (.29,.07),(.26,-.06),(.19,-.16),(.09,-.21),(0,-.23),(-.09,-.21),(-.19,-.16),(-.26,-.06),(-.29,.07)]
        m.outline(pts,.03,.088)
        path(m,[(-.29,.12),(-.24,-.08),(0,-.205),(.24,-.08),(.29,.12)],.096,.009)
        for sign in (-1,1):
            m.ellipsoid((sign*.285,.175,.088),(.035,.027,.027),segments=16,rings=8)
            for i in range(12):
                a=i/11;x=sign*(.22+.47*a);y=-.19+.16*math.sin(a*math.pi)
                leaf(m,(x,y),(x-sign*.07,y+.075),.014,.038)
                leaf(m,(x,y),(x-sign*.045,y-.045),.011,.036)
            path(m,[(sign*.17,-.23),(sign*.45,-.21),(sign*.72,-.20)],.03,.009)
        for i in range(9):
            a=.2+i*(math.pi-.4)/8
            leaf(m,(0,.13),(.13*math.cos(a),.13+.10*math.sin(a)),.013,.048)
        for x in (-.14,.14):
            m.outline([(x-.025,.14),(x+.025,.14),(x+.025,.015),(x-.025,.015)],.088,.105)
            for y in (.035,.115):m.ellipsoid((x,y,.11),(.009,.009,.006),segments=10,rings=5)
    elif kind=='wreath':
        sword(m,(-.38,-.12),(.57,.19),.033)
        sword(m,(.37,-.14),(-.58,.19),.034,z=.049)
        wreath(m,(0,.015),.215,.067,True,.050)
        for sign in (-1,1):
            brazier(m,sign*.87,0,1.1)
            festoon(m,[(sign*.15,.19),(sign*.39,.005),(sign*.61,-.035),(sign*.80,.13)],.035)
            festoon(m,[(sign*.83,.10),(sign*.97,.04),(sign*1.0,-.08)],.025)
    else:
        for sign in (-1,1):
            brazier(m,sign*.88,0,1.1,True)
            festoon(m,[(sign*.20,.21),(sign*.42,.095),(sign*.63,.11),(sign*.82,.18)],.036)
            helmet(m,sign*.48,-.07,.46,flip=sign<0)
            path(m,[(sign*.30,.0),(sign*.70,.0)],.025,.019)
        m.ellipsoid((0,0,.034),(.245,.245,.025),segments=80,rings=10)
        m.ring((0,0,.062),.235,.013,segments=96)
        # Small winged Victory carrying palm and trumpet; silhouette from mont_13b.
        m.outline([(-.04,.12),(.045,.10),(.06,-.02),(.11,-.08),(.035,-.12),(.0,-.08),(-.07,-.04),(-.09,.02)],.065,.089)
        m.ellipsoid((.038,.145,.086),(.025,.031,.013),segments=16,rings=8)
        wing(m,(-.02,.10),(-.19,.12),.17)
        path(m,[(.025,.07),(.10,.015),(.15,.025)],.10,.009)
        path(m,[(.02,-.09),(.025,-.17),(.07,-.18)],.10,.009)
        path(m,[(-.04,-.07),(-.11,-.11),(-.14,-.085)],.10,.009)
        path(m,[(.15,-.04),(.16,.04),(.145,.10)],.085,.006)
        for i in range(6):leaf(m,(.15,.02+i*.012),(.12,.04+i*.015),.006,.073)
    return m

def lion_head(size=None):
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'cornice-lion.npz','Cornice lion mask — interpreted broad forms')

def frieze_foliage():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'frieze-foliage.npz','Frieze foliage — traced lobed scrolls')

def architectural_rosette():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'architectural-rosette.npz','Architectural rosette — twelve cupped petals')

def lion_head_legacy(size=.085):
    m=Mesh('Lion head cornice spout')
    for i in range(16):
        a=TAU*i/16
        leaf(m,(.5*size*math.cos(a),.5*size*math.sin(a)),
             (size*math.cos(a),size*math.sin(a)),size*.22,.04)
    m.ellipsoid((0,0,.042),(size*.66,size*.75,.039),segments=20,rings=10)
    for sign in (-1,1):
        m.ellipsoid((sign*size*.42,size*.05,.079),(size*.23,size*.19,.019),segments=12,rings=6)
        path(m,[(sign*size*.17,size*.24),(sign*size*.43,size*.31)],.087,.008)
        m.ellipsoid((sign*size*.22,-size*.27,.082),(size*.27,size*.22,.019),segments=16,rings=8)
    m.ellipsoid((0,-size*.03,.10),(size*.20,size*.18,.021),segments=16,rings=8)
    path(m,[(-size*.29,-size*.44),(0,-size*.50),(size*.29,-size*.44)],.096,.006)
    return m

def mourning_legacy_proxy():
    """Trace coordinates from IWM mont_9a; front relief, no invented rear anatomy."""
    m=Mesh('Mourning figure — provisional sculptural depths')
    def p(pt):return ((pt[0]-427.5)/249*1.45,(1005-pt[1])/502*2.75)
    def poly(pts,z):m.cushion([p(v) for v in pts],.018,z,softness=.025,spacing=.004)
    def line(pts,z=.082,r=.008):path(m,[p(v) for v in pts],z,r)
    poly([(451,579),(477,577),(497,593),(509,630),(513,691),(519,769),(526,869),(540,972),
          (473,975),(447,968),(450,917),(440,860),(434,790),(421,733),(431,663),(440,617)],.065)
    # Sandalled feet and hem.
    poly([(456,950),(451,969),(439,977),(467,979),(483,972),(479,953)],.084)
    poly([(504,954),(507,972),(520,977),(540,978),(533,969),(520,958)],.078)
    # Neck and bent head.
    poly([(446,566),(446,588),(461,603),(478,587),(462,570)],.076)
    poly([(437,532),(423,540),(417,550),(419,557),(416,564),(423,567),(425,574),(436,581),(447,580),(459,563),(465,544),(452,532)],.096)
    for j in range(9):
        line([(421,537+j*3),(432,530+j*3),(447,532+j*3),(460,541+j*2)],.105,.005)
    hx,hy=p((469,536));m.ellipsoid((hx,hy,.084),(.065,.085,.028),segments=22,rings=12)
    line([(422,554),(431,558)],.113,.004)
    line([(421,568),(430,570)],.112,.003)
    # Bare forearms, hands and separate fingers.
    poly([(461,619),(440,645),(403,663),(353,698),(336,720),(330,740),(337,748),(345,740),
          (352,714),(402,688),(442,671),(480,640)],.091)
    poly([(481,643),(465,669),(435,689),(417,708),(409,726),(414,733),(422,728),(431,714),
          (447,707),(488,683),(498,660)],.110)
    for i in range(4):
        line([(331+i*4,728),(333+i*4,744)],.115,.003)
        line([(413+i*4,715),(410+i*4,730)],.129,.003)
    # Long drapery ridges, varied curves echo the source folds.
    for i in range(12):
        xx=449+i*5
        line([(xx,699+i%3*9),(xx-7,778),(xx+1,864),(xx+5,961)],.074+(i%3)*.005,.006)
    for i in range(6):
        line([(484+i*3,601),(493+i*2,631),(486+i*3,655)],.081,.006)
    line([(428,733),(446,779),(438,805),(458,851),(453,879),(471,926)],.086,.009)
    # Garland held above a helmet; flowers cluster on its low curve.
    pts=[p(v) for v in [(337,742),(330,790),(349,839),(375,854),(405,835),(420,737)]]
    festoon(m,pts,.035)
    for j in range(14):
        x,y=p((323,752+j*15));leaf(m,(x,y),(x-.03,y-.07),.025,.05);leaf(m,(x,y),(x+.03,y-.07),.025,.055)
    hx,hy=p((373,947));helmet(m,hx,hy,.62)
    # PATRIA standard with Ionic curls; lion and lettering added separately.
    line([(364,607),(373,751)],.065,.018)
    for sign in (-1,1):
        x,y=p((363+sign*14,604));m.ring((x,y,.071),.048,.008,segments=32)
        m.ring((x,y,.075),.023,.006,segments=24)
    poly([(322,553),(382,550),(388,579),(326,584)],.070)
    poly([(325,543),(335,532),(357,532),(370,539),(385,538),(382,545),(365,547),(355,543),(342,548),(329,550)],.088)
    line([(330,535),(320,530),(321,522),(332,521)],.091,.009)
    return m

def victory_legacy_proxy():
    m=Mesh('Victory Britannia — provisional sculptural depths')
    # Panel normalized to 1.45 x 2.75 metres.
    def p(a):return ((a[0]-.5)*1.45,a[1]*2.75)
    def poly(pts,z):m.cushion([p(v) for v in pts],.015,z,softness=.022,spacing=.004)
    def line(pts,z=.08,r=.008):path(m,[p(v) for v in pts],z,r)
    # Large shield and spear behind the standing figure.
    sx,sy=p((.64,.58));m.ellipsoid((sx,sy,.032),(.37,.55,.027),segments=64,rings=12)
    # Elliptical rim (tube rather than a round generic shield).
    m.tube([(sx+.37*math.cos(TAU*i/100),sy+.55*math.sin(TAU*i/100),.066) for i in range(101)],.018)
    line([(.86,.035),(.86,.88)],.04,.015)
    poly([(.845,.88),(.875,.88),(.86,.98)],.064)
    poly([(.28,.79),(.43,.79),(.54,.71),(.52,.52),(.55,.32),(.61,.05),(.58,.025),(.24,.025),(.22,.09),(.26,.34),(.22,.53)],.078)
    poly([(.35,.79),(.35,.86),(.43,.87),(.44,.79),(.40,.76)],.088)
    poly([(.34,.90),(.39,.92),(.46,.90),(.48,.87),(.50,.855),(.477,.848),(.47,.82),(.43,.81),(.38,.83)],.106)
    # Corinthian-style helmet crest and cheek flap, matching the visible outline.
    poly([(.29,.88),(.32,.94),(.43,.96),(.51,.945),(.46,.92),(.37,.915),(.34,.86)],.112)
    for i in range(15):
        t=i/14
        line([(.30+t*.19,.922+math.sin(t*math.pi)*.022),(.31+t*.19,.958+math.sin(t*math.pi)*.025)],.124,.005)
    line([(.373,.904),(.367,.846)],.12,.009)
    line([(.443,.873),(.468,.87)],.122,.004)
    # Long hanging sleeve beneath the extended arm, confirmed by the historic
    # paired detail photograph reproduced in the 2023 centenary article.
    poly([(.44,.72),(.53,.605),(.68,.60),(.665,.39),(.63,.28),(.59,.25),
          (.60,.22),(.555,.20),(.57,.18),(.53,.17),(.51,.22),(.485,.20),(.48,.47)],.087)
    poly([(.45,.75),(.53,.625),(.67,.62),(.75,.64),(.78,.625),(.73,.598),(.61,.588),(.49,.60),(.43,.71)],.113)
    for i in range(4):line([(.727,.624-i*.005),(.777,.63-i*.005)],.13,.003)
    for i in range(7):
        line([(.49+i*.012,.60),(.52+i*.016,.48),(.54+i*.014,.36),(.52+i*.009,.23+i*.004)],.098,.006)
    # Statuette stands on a small stepped pedestal in the upturned palm.
    poly([(.68,.63),(.80,.63),(.80,.66),(.775,.665),(.77,.695),(.715,.695),(.71,.665),(.68,.66)],.125)
    for y in (.645,.665,.69):line([(.70,y),(.785,y)],.133,.005)
    poly([(.27,.735),(.23,.60),(.23,.39),(.255,.36),(.28,.40),(.29,.59),(.32,.72)],.096)
    for i in range(4):line([(.234+i*.011,.408),(.237+i*.011,.367)],.11,.003)
    # Dress and cloak folds run continuously into the hem.
    for i in range(13):
        x=.28+i*.020
        line([(x,.69-(i%3)*.014),(x-.012,.48),(x+.008,.23),(x+.025,.05)],.089+(i%4)*.003,.006)
    line([(.30,.76),(.31,.62),(.29,.47),(.32,.31),(.31,.12)],.107,.012)
    for q in (0,.015,.03):line([(.48+q,.73),(.51+q,.61),(.50+q,.46),(.55+q,.27)],.10,.007)
    poly([(.28,.045),(.28,.018),(.38,.012),(.42,.025),(.36,.046)],.096)
    poly([(.48,.045),(.49,.016),(.61,.01),(.63,.025),(.57,.049)],.102)
    # Small winged Victory; raised arm, flowing skirt, lifted heel.
    poly([(.72,.795),(.76,.79),(.79,.715),(.75,.71),(.71,.75)],.12)
    hx,hy=p((.74,.817));m.ellipsoid((hx,hy,.13),(.023,.031,.016),segments=16,rings=8)
    line([(.735,.80),(.705,.85),(.72,.875)],.13,.009)
    line([(.75,.74),(.77,.705),(.73,.695)],.13,.008)
    wing(m,p((.77,.80)),p((.91,.86)),.18)
    wing(m,p((.75,.80)),p((.82,.88)),.12)
    return m

def southport_arms():
    from sculpt_surface import mesh_from_surface
    return mesh_from_surface(RELIEF_DATA/'southport-arms.npz','Southport arms — traced continuous surface')

def southport_arms_legacy_proxy():
    m=Mesh('Southport arms relief — traced heraldic components')
    m.ring((0,0,.018),.62,.014,segments=128)
    m.ring((0,0,.025),.59,.006,segments=128)
    # Ribbon above, left and right; motto placed along these arcs by main script.
    for sign in (-1,1):
        pts=[]
        for i in range(25):
            a=math.radians(45+i*4.3)
            pts.append((sign*.535*math.sin(a),.535*math.cos(a)))
        for i in reversed(range(25)):
            a=math.radians(45+i*4.3)
            pts.append((sign*.455*math.sin(a),.455*math.cos(a)))
        m.outline(pts,.018,.039)
    shield=[(-.285,.16),(.285,.16),(.282,-.08),(.24,-.30),(.12,-.48),(0,-.55),(-.12,-.48),(-.24,-.30),(-.282,-.08)]
    m.outline(shield,.018,.052)
    path(m,shield+[shield[0]],.061,.008)
    # Chevron, three cross-crosslets, sailing vessel below.
    m.outline([(-.255,-.15),(-.13,-.055),(0,-.15),(.13,-.055),(.255,-.15),(.245,-.205),(.13,-.11),(0,-.20),(-.13,-.11),(-.245,-.205)],.055,.066)
    for x in (-.18,0,.18):
        y=.05
        path(m,[(x,y-.09),(x,y+.08)],.072,.010)
        path(m,[(x-.055,y+.03),(x+.055,y+.03)],.072,.010)
        for xx in (x-.045,x+.045):path(m,[(xx,y+.005),(xx,y+.06)],.073,.007)
        path(m,[(x-.022,y+.065),(x+.022,y+.065)],.073,.007)
    path(m,[(-.17,-.30),(-.09,-.34),(.11,-.34),(.18,-.30),(-.17,-.30)],.074,.009)
    for x in (-.09,.015,.11):
        path(m,[(x,-.33),(x,-.20)],.074,.006)
        m.outline([(x-.05,-.22),(x+.045,-.23),(x+.035,-.285),(x-.05,-.28)],.064,.075)
    for j in range(3):path(m,[(-.18,-.37-j*.025),(-.08,-.36-j*.025),(.04,-.38-j*.025),(.15,-.365-j*.025)],.065,.004)
    # Mural crown, bell crest and two small supporting animals.
    m.outline([(-.27,.19),(.27,.19),(.25,.23),(.29,.29),(.20,.28),(.17,.33),(.11,.29),(0,.34),(-.11,.29),(-.17,.33),(-.20,.28),(-.29,.29),(-.25,.23)],.027,.066)
    path(m,[(-.27,.19),(0,.185),(.27,.19)],.074,.009)
    m.outline([(-.06,.31),(.06,.31),(.07,.34),(.045,.39),(.032,.45),(-.032,.45),(-.045,.39),(-.07,.34)],.05,.082)
    path(m,[(0,.43),(0,.52)],.078,.010)
    for y in (.45,.48):path(m,[(-.043,y),(.043,y)],.083,.008)
    for sign in (-1,1):
        m.ellipsoid((sign*.13,.30,.071),(.039,.063,.020),segments=16,rings=8)
        m.ellipsoid((sign*.14,.355,.078),(.030,.028,.021),segments=16,rings=8)
        path(m,[(sign*.115,.27),(sign*.11,.23)],.078,.008)
    return m
