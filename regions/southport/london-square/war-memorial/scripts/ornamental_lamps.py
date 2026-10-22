"""Bromsgrove lamp geometry, authored from the registered exterior photographs.

All coordinates are metres. The original photographs remain separate references;
dimensions and small casting details are estimates, not a measured replica.
Material slots: black paint, ivory paint, opaque globe.
"""
import math
from mathutils import Matrix, Vector
from geometry import Mesh, smooth_path, TAU


class LampMesh(Mesh):
    """Keep cast flat plates flat while smoothly shading turned parts."""
    def __init__(self,name):
        super().__init__(name);self.flat_faces=set()

    def box(self,*args,**kwargs):
        start=len(self.faces);super().box(*args,**kwargs)
        self.flat_faces.update(range(start,len(self.faces)))

    def rect_profile(self,*args,**kwargs):
        start=len(self.faces);super().rect_profile(*args,**kwargs)
        self.flat_faces.update(range(start,len(self.faces)))

    def lathe(self,*args,**kwargs):
        start=len(self.faces);super().lathe(*args,**kwargs)
        self.flat_faces.update([start,len(self.faces)-1])

    def finish(self,*args,**kwargs):
        ob=super().finish(*args,**kwargs)
        for i in self.flat_faces:ob.data.polygons[i].use_smooth=False
        return ob


def bead_ring(m, z, radius, bead=.008, count=32, material=1):
    for i in range(count):
        a=TAU*i/count
        m.ellipsoid((radius*math.cos(a),radius*math.sin(a),z),
                    (bead,bead,bead),material,10,5)


def leaf_crown(m, z0, height, radius, count=12, relief=.018, profile=None):
    """Two-lobed raised acanthus silhouettes wrapped around the turned base."""
    for k in range(count):
        a=TAU*k/count
        verts=[];faces=[];rows=14;cols=8
        for j in range(rows+1):
            t=j/rows
            # Five broad lobes, ending in a folded pointed tip.
            width=.17*math.sin(math.pi*t)**.65*(.82+.18*math.cos(6*math.pi*t))
            z=z0+height*t
            if profile:
                rr=profile[-1][1]
                for (za,ra),(zb,rb) in zip(profile,profile[1:]):
                    if za<=z<=zb:
                        rr=ra+(rb-ra)*(z-za)/(zb-za);break
            else:rr=radius*(1-.34*t)
            for i in range(cols+1):
                q=2*i/cols-1;aa=a+q*width
                r=rr+.001+relief*(1-q*q)*math.sin(math.pi*t)
                verts.append((r*math.cos(aa),r*math.sin(aa),z0+height*t))
        for j in range(rows):
            for i in range(cols):
                v=j*(cols+1)+i;faces.append((v,v+1,v+cols+2,v+cols+1))
        m.add(verts,faces,1)
        # Central vein is a shallow raised casting rib.
        points=[verts[j*(cols+1)+cols//2] for j in range(1,rows)]
        m.tube(points,.0035,1,6)


def short_standard():
    """One globe, open footed stand, fluted stem and acanthus foot; base z=.48."""
    m=LampMesh('Bromsgrove single-globe standard')
    # A thin square frame on four raised, outward-curving feet. The space
    # beneath the circular foot is open in both Commons column photographs.
    m.box((0,0,.565),(.47,.47,.035),0)
    for k in range(4):
        a=math.pi/4+k*math.pi/2
        u=Vector((math.cos(a),math.sin(a),0));v=Vector((-u.y,u.x,0))
        outline=[(.16,.55),(.22,.54),(.32,.49),(.36,.49),(.35,.55),
                 (.33,.59),(.33,.67),(.30,.70),(.28,.62),(.24,.595),(.16,.595)]
        verts=[]
        for side in (-1,1):
            for r,z in outline:verts.append(tuple(u*r+v*(side*.035)+Vector((0,0,z))))
        n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        start=len(m.faces);m.add(verts,faces,0);m.flat_faces.update(range(start,len(m.faces)))
    m.lathe((0,0),[(.565,.19),(.58,.20),(.602,.20),(.618,.17),(.64,.155),
                    (.665,.14),(.705,.126),(.76,.115),(.85,.105),(.91,.086)],64,1)
    leaf_crown(m,.635,.28,.153,12,.014,[(.63,.162),(.665,.14),(.705,.126),(.76,.115),(.85,.105),(.91,.086),(.92,.09)])
    bead_ring(m,.618,.174,.006,40)
    m.lathe((0,0),[(.90,.089),(.92,.090),(.94,.071),(.985,.067),
                    (1.01,.056),(2.40,.044),(2.45,.047)],64,1,16,.005)
    for z,r in [(.94,.073),(1.035,.059),(2.39,.049)]:
        m.lathe((0,0),[(z,r),(z+.012,r+.004),(z+.024,r)],48,1)
    m.lathe((0,0),[(2.425,.045),(2.47,.060),(2.49,.077),(2.51,.115),
                    (2.525,.155),(2.548,.160),(2.563,.151),(2.575,.105),
                    (2.61,.075),(2.65,.054),(2.675,.051)],64,1)
    bead_ring(m,2.553,.147,.0055,48)
    m.lathe((0,0),[(2.67,.053),(2.70,.063),(2.75,.099),(2.775,.112)],48,0)
    m.ellipsoid((0,0,2.942),(.210,.210,.218),2,48,24)
    return m


def cluster_arm(angle):
    """A moulded beam and an open scroll bracket in one radial plane."""
    m=LampMesh('Cluster lamp arm')
    for z,w,d,h in [(4.57,.70,.14,.045),(4.63,.73,.15,.085),
                     (4.69,.78,.19,.035),(4.718,.81,.21,.022)]:
        inner=.11;outer=.34+w/2
        m.box(((inner+outer)/2,0,z),(outer-inner,d,h),1)
    # Cast diagonal ridges along both visible sides of the beam.
    for side in (-1,1):
        for j in range(16):
            x=.02+j*.044
            m.tube([(x,side*.079,4.596),(x+.027,side*.079,4.658)],.0038,1,5)
    # Actual curved support is a volute below the cross-arm. Keep its central
    # aperture open; a solid triangular bracket gives the wrong silhouette.
    line=[(.035,0,4.285),(.13,0,4.335),(.23,0,4.45),(.36,0,4.51),
          (.46,0,4.515),(.49,0,4.48),(.465,0,4.45),(.425,0,4.465)]
    m.tube(smooth_path(line,6),.033,1,12)
    for side in (-1,1):
        # Small raised scroll on the side of the central bracket.
        pts=[]
        for j in range(55):
            t=j/54;a=math.pi*2.2*t;r=.082*(1-.77*t)
            pts.append((.17+r*math.cos(a),side*.037,4.42+r*math.sin(a)))
        m.tube(pts,.009,1,8)
    # Turned finial above each arm end; pendant holder underneath.
    x=.66
    m.lathe((x,0),[(4.73,.040),(4.76,.043),(4.78,.025),(4.80,.021),
                     (4.82,.046),(4.83,.050),(4.842,.031),(4.88,.020)],32,1)
    m.ellipsoid((x,0,4.899),(.023,.023,.029),1,16,8)
    m.lathe((x,0),[(4.47,.046),(4.48,.063),(4.49,.071),(4.505,.063),
                     (4.53,.044),(4.57,.033),(4.59,.043)],40,1)
    m.lathe((x,0),[(4.28,.115),(4.31,.106),(4.39,.061),(4.44,.044),
                     (4.47,.046)],40,0)
    m.ellipsoid((x,0,4.075),(.275,.275,.283),2,48,24)
    return m.transform(Matrix.Rotation(angle,4,'Z'))


def clustered_standard():
    m=LampMesh('Bromsgrove five-globe clustered standard')
    # Square black pedestal with panelled sides and stepped cap.
    m.rect_profile((0,0),[(-.01,.82,.82),(.05,.82,.82),(.10,.76,.76),
                          (.65,.72,.72),(.71,.77,.77),(.75,.78,.78),
                          (.79,.69,.69)],0)
    for k in range(4):
        p=LampMesh('Pedestal panel border')
        for x in (-.282,.282):p.box((x,-.365,.36),(.018,.012,.46),0)
        for z in (.13,.59):p.box((0,-.365,z),(.58,.012,.018),0)
        p.transform(Matrix.Rotation(k*math.pi/2,4,'Z'))
        start=len(m.faces);m.add(p.vertices,p.faces,0)
        m.flat_faces.update(start+i for i in p.flat_faces)
    # Spreading acanthus foot and large bulbous base above it.
    m.lathe((0,0),[(.77,.31),(.80,.32),(.82,.30),(.86,.27),(.92,.23),
                    (1.00,.205),(1.05,.205),(1.07,.225),(1.12,.226),
                    (1.14,.208),(1.18,.215),(1.24,.225),(1.33,.215),
                    (1.47,.180),(1.51,.166),(1.54,.17)],80,1)
    leaf_crown(m,.82,.24,.29,20,.018,[(.82,.30),(.86,.27),(.92,.23),(1.00,.205),(1.05,.205),(1.07,.225)])
    leaf_crown(m,1.17,.36,.211,16,.019,[(1.14,.208),(1.18,.215),(1.24,.225),(1.33,.215),(1.47,.180),(1.51,.166),(1.54,.17)])
    bead_ring(m,1.535,.170,.011,40)
    m.lathe((0,0),[(1.53,.163),(1.565,.163),(1.585,.145),(1.62,.14),
                    (4.07,.113),(4.11,.119)],96,1,20,.009)
    # Decorated capital, shallow flutes below the supported cross arms.
    m.lathe((0,0),[(4.07,.117),(4.10,.139),(4.125,.151),(4.15,.153),
                    (4.18,.139),(4.21,.137),(4.28,.143),(4.39,.157),
                    (4.43,.174),(4.455,.177)],64,1)
    leaf_crown(m,4.20,.24,.151,12,.014,[(4.18,.139),(4.21,.137),(4.28,.143),(4.39,.157),(4.43,.174),(4.455,.177)])
    bead_ring(m,4.17,.145,.008,32)
    for k in range(4):
        arm=cluster_arm(k*math.pi/2)
        m.flat_faces.update(len(m.faces)+i for i in arm.flat_faces)
        start=len(m.vertices);m.vertices.extend(arm.vertices)
        m.faces.extend(tuple(start+i for i in f) for f in arm.faces)
        m.indices.extend(arm.indices)
    # Raised central stem carries the fifth, upright globe.
    m.lathe((0,0),[(4.43,.176),(4.49,.164),(4.56,.126),(4.72,.115),
                    (4.75,.145),(4.785,.15),(4.81,.122),(4.85,.095),
                    (4.99,.082),(5.025,.122),(5.055,.153),(5.085,.159),
                    (5.11,.137),(5.13,.083)],64,1)
    bead_ring(m,4.79,.139,.007,40)
    m.lathe((0,0),[(5.12,.079),(5.17,.084),(5.22,.121),(5.235,.133)],48,0)
    m.ellipsoid((0,0,5.465),(.275,.275,.283),2,48,24)
    return m
