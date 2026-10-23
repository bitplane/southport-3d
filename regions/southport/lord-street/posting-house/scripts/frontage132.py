"""132 Lord Street: three canted bays over red sandstone arcade, from Nov 2020 imagery."""
import math
import bpy
import bmesh
from mathutils import Matrix, Vector
from southport3d.geometry import Mesh
from components import rect, wall, opening, ellipse_band, sash


def bay_sash(width):
    mesh=sash('Window 132 bay sash',width,3.0)
    # Keep timber close to the glazing, so canted corners meet their aprons.
    timber={i for face,mat in zip(mesh.faces,mesh.indices) if mat==1 for i in face}
    mesh.vertices=[(x,y,z-.13 if i in timber else z) for i,(x,y,z) in enumerate(mesh.vertices)]
    return mesh


def build_132(g):
    front=g['front'];finish=g['finish'];box=g['box'];instance=g['instance']
    brick=g['brick'];black=g['black'];white=g['white'];glass=g['glass'];slate=g['slate']
    w=g['start'];depth=g['depth'];eave=16.35
    red=g['material']('132 red sandstone',(.37,.18,.11))
    baycentres=[w*(j+.5)/3 for j in range(3)]
    holes=[]
    for c in baycentres:
        for z,h in [(7.05,3.0),(11.05,3.0),(14.75,1.65)]:holes.append(rect(c-1.25,z-h/2,c+1.25,z+h/2))
    # Four ground openings: the outer pair are narrower round-headed portals.
    ground=[(.8,.60),(w/3,1.18),(2*w/3,1.18),(w-.8,.60)]
    for c,r in ground:holes.append(opening(c,.55,3.0,r,.7))
    finish(wall('Envelope 132 front',rect(0,0,w,eave),holes),mats=[brick],frame=front)
    finish(wall('Envelope 132 ground red stone',rect(0,0,w,4.8),holes,back=.015,front=.13),mats=[red],frame=front)
    for c,r in ground:
        m=Mesh('Arch 132 ground surround');ellipse_band(m,c,3.0,r,.7,.17,.32)
        for side in [-1,1]:m.box((c+side*(r+.085),1.8,.24),(.17,2.5,.30))
        finish(m,mats=[red],frame=front)
        m=Mesh('Glazing 132 arched shop');m.outline(opening(c,.55,3.0,r,.7),-.23,-.20,0)
        m.box((c,1.85,-.08),(.065,2.6,.13),1);m.box((c,2.96,-.08),(2*r,.08,.13),1)
        finish(m,'shopfronts',[glass,white],front)
    for z,h,d in [(4.08,.16,.32),(4.62,.17,.46),(4.83,.12,.52)]:box('Trim 132 red cornice',(w/2,z,d/2),(w,h,d),mat=red,frame=front)
    for c,r in (ground[0],ground[-1]):
        m=Mesh('Gable 132 entrance pediment');m.outline([(c-1.02,4.86),(c+1.02,4.86),(c,5.65)],.05,.29)
        m.tube([(c-1.09,4.86,.34),(c,5.68,.34),(c+1.09,4.86,.34)],.065,sides=8)
        finish(m,mats=[red],frame=front)
    for idx,c in enumerate(baycentres):
        # Canted bays have real return glass and projecting opaque aprons.
        outline=[(-1.27,0),(-.97,.74),(.97,.74),(1.27,0)]
        for z in [7.05,11.05]:
            for (x0,d0),(x1,d1) in zip(outline,outline[1:]):
                length=math.hypot(x1-x0,d1-d0);angle=-math.atan2(d1-d0,x1-x0)
                f=front@Matrix.Translation((c+(x0+x1)/2,z,(d0+d1)/2))@Matrix.Rotation(angle,4,'Y')
                instance('132-bay-'+str(round(length,4)),bay_sash(length-.08),f@Matrix.Translation((0,0,.19)),mats=[glass,white])
                m=Mesh('Trim 132 arched upper lights')
                count=3 if length>1.5 else 1
                for j in range(count):
                    cx=(j+.5)*length/count-length/2;rx=length/count/2-.055
                    ellipse_band(m,cx,.72,rx,.30,.038,-.025,mat=0)
                finish(m,mats=[white],frame=f)
                box('Trim 132 window head',(0,1.56,.06),(length+.08,.13,.24),mat=black,frame=f)
                box('Trim 132 window sill',(0,-1.53,.08),(length+.12,.13,.25),mat=black,frame=f)

            # One closed apron across the whole canted plan avoids overlapping
            # white panel ends and closes the former slit below the sill.
            m=Mesh('Envelope 132 white apron')
            v=[(c+x,h,d) for h in [z-2.34,z-1.47] for x,d in outline]
            m.add(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            finish(m,mats=[white],frame=front)
            for x,d in outline:
                box('Trim 132 corner post',(c+x,z,d),(.10,3.15,.12),mat=black,frame=front)
            # Thin roof ledges close canted bay tops and bottoms in plan.
            for h in [z+1.65,z-1.58]:
                m=Mesh('Roof 132 bay ledge');m.add([(c+x,h,d) for x,d in outline]+[(c+x,h+.10,d) for x,d in outline],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                finish(m,mats=[black],frame=front)
        # The top row is four plain vertical casements, not a Georgian sash grid.
        m=Mesh('Window 132 upper casement');m.box((0,0,-.23),(2.5,1.65,.04),0)
        for x in [-1.215,-.625,0,.625,1.215]:m.box((x,0,-.10),(.055,1.54,.13),1)
        for z in [-.7975,.7975]:m.box((0,z,-.10),(2.5,.055,.13),1)
        instance('132-top-casement',m,front@Matrix.Translation((c,14.75,0)),mats=[glass,white])
        for h in [13.72,15.75,16.17]:box('Trim 132 black band',(c,h,.07),(w/3,.14,.23),mat=black,frame=front)
        m=Mesh('Gable 132 white front');m.outline([(c-1.4,16.35),(c+1.4,16.35),(c,18.05)],-.18,.07)
        finish(m,mats=[white],frame=front)
        m=Mesh('Trim 132 gable barge');m.tube([(c-1.47,16.31,.13),(c,18.14,.13),(c+1.47,16.31,.13)],.10,sides=8)
        finish(m,mats=[black],frame=front)
    # Closed pitched roof and brick end returns. Exact rear bay layout unobserved.
    m=Mesh('Roof 132 main gable')
    section=[(16.3,0),(19.1,-depth/2),(16.3,-depth),(16.14,-depth),(18.94,-depth/2),(16.14,0)]
    m.add([(u,h,d) for u in [0,w] for h,d in section],
          [tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)])
    main=finish(m,'roof',[slate],front)
    # Three projecting white gables need their own pitched roofs. They intersect
    # the transverse main slope, rather than standing as unsupported screens.
    for c in [w*(j+.5)/3 for j in range(3)]:
        top=[(c-1.48,16.32,.08),(c+1.48,16.32,.08),(c+1.48,16.32,-6.0),(c-1.48,16.32,-6.0),
             (c,18.12,.08),(c,18.12,-6.0)]
        faces=[(0,4,5,3),(4,1,2,5)]
        edges=[(0,4),(4,1),(1,2),(2,5),(5,3),(3,0)]
        m=Mesh('Temporary 132 front cross gable')
        m.add(top+[(x,y-.16,z) for x,y,z in top],faces+[tuple(i+6 for i in reversed(f)) for f in faces]+[(a,b,b+6,a+6) for a,b in edges])
        cross=finish(m,'roof',[slate],front)
        bm=bmesh.new();bm.from_mesh(cross.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cross.data);bm.free()
        bpy.context.view_layer.objects.active=main
        mod=main.modifiers.new('Join 132 front gable roof','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=cross
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cross,do_unlink=True)
    for u in [0,w]:
        f=front@Matrix.Translation((u,0,0))@Matrix.Rotation(math.pi/2,4,'Y')
        finish(wall('Envelope 132 side',[(0,0),(depth,0),(depth,16.14),(depth/2,18.94),(0,16.14)],[]),mats=[brick],frame=f)
    back=front@Matrix.Translation((w,0,-depth))@Matrix.Rotation(math.pi,4,'Y')
    finish(wall('Envelope 132 rear',rect(0,0,w,16.3),[]),mats=[brick],frame=back)
