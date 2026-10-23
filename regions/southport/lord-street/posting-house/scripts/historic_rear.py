"""Unequal rear openings from the 2024 photographic schedule and garden photos."""
import math
import bpy
from mathutils import Matrix
from southport3d.geometry import Mesh
from components import rect, wall, sash


def build_historic_rear(g):
    front=g['front'];width=g['width'];depth=g['depth'];start=g['start']
    finish=g['finish'];instance=g['instance'];box=g['box']
    brick=g['brick'];glass=g['glass'];white=g['white'];eave=g['eave']
    rear=front@Matrix.Translation((width,0,-depth))@Matrix.Rotation(math.pi,4,'Y')
    # Rear-local X runs west to east. Widths and heights are estimates fitted
    # to the photographed unequal groups, not repetitions of the front sash.
    openings=[(3.0,7.25,2.15,3.9),(6.15,7.25,1.05,3.9),
              (3.0,13.7,2.15,1.55),(6.15,13.7,1.05,1.55),
              (10.45,6.9,2.2,2.6),(10.45,12.1,2.2,4.35),
              (12.6,6.9,1.15,1.8),(12.6,12.15,1.15,3.05)]
    holes=[rect(x-w/2,z-h/2,x+w/2,z+h/2) for x,z,w,h in openings]
    finish(wall('Envelope historic rear',rect(0,0,width-start,eave),holes),'rear-range',[brick],rear)
    for j,(x,z,w,h) in enumerate(openings):
        instance('rear-observed-'+str(j),sash('Glazing rear estimated sash',w,h),
                 rear@Matrix.Translation((x,z,0)),'rear-range',[glass,white])
        # Rear surrounds are plain brick heads and projecting sills; the
        # elaborate stone window frames from the street do not occur here.
        box('Trim rear plain sill',(x,z-h/2-.06,.07),(w+.18,.12,.24),'rear-range',g['cream'],rear)
        box('Trim rear brick head',(x,z+h/2+.10,.025),(w+.16,.18,.12),'rear-range',brick,rear)
    for c,w,top,centres in [(start+3.1,5.7,g['ridge']-.65,[0]),
                            ((start+width)/2,6.2,g['ridge']-.15,[-1.25,0,1.25]),
                            (width-3,5.7,g['ridge']-.65,[])]:
        frame=front@Matrix.Translation((c,0,-depth-.035))@Matrix.Rotation(math.pi,4,'Y')
        holes=[rect(x-.36,17.0,x+.36,18.4) for x in centres]
        finish(wall('Gable rear brick',[(-w/2,eave),(w/2,eave),(0,top)],holes,-.15,0),'rear-range',[brick],frame)
        for x in centres:
            cutter_mesh=Mesh('Temporary rear attic aperture')
            cutter_mesh.box((x,17.7,-.15),(.74,1.42,1.0))
            cutter=cutter_mesh.finish([]);cutter.matrix_world=frame
            roof=g['roof'];bpy.context.view_layer.objects.active=roof
            mod=roof.modifiers.new('Rear attic clear glazing','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
            instance('rear-attic-small',sash('Glazing rear attic',.72,1.4),frame@Matrix.Translation((x,17.7,.0)),
                     'rear-range',[glass,white])
    # Juliet rail on the tall central opening, visible in both property and
    # heritage photographs. Separate narrow bars retain the negative spaces.
    m=Mesh('Balcony historic rear Juliet')
    for z in [10.05,10.65,11.25]:m.tube([(9.2,z,.26),(11.7,z,.26)],.025,sides=6)
    for j in range(13):m.tube([(9.2+j*2.5/12,9.95,.26),(9.2+j*2.5/12,11.3,.26)],.018,sides=6)
    finish(m,'rear-range',[white],rear)

    # Glazed stair connection at the historic end of the modern access tower.
    # Only its exterior enclosure is represented; the internal stair is deferred.
    for frame,ww in [
        (front@Matrix.Translation((17.5,0,-20.9))@Matrix.Rotation(math.pi,4,'Y'),1.0),
        (front@Matrix.Translation((17.5,0,-20.9))@Matrix.Rotation(math.pi/2,4,'Y'),-3.0),
    ]:
        m=Mesh('Window historic glazed stair enclosure')
        a,b=sorted([0,ww]);mid=(a+b)/2
        m.box((mid,8.8,-.12),(b-a,11.8,.04),0)
        for j in range(5):m.box((a+(b-a)*j/4,8.8,-.055),(.055,11.8,.07),1)
        for j in range(17):m.box((mid,2.9+11.8*j/16,-.055),(b-a,.045,.07),1)
        finish(m,'rear-range',[glass,white],frame)
    box('Roof historic stair cap',(17.0,14.8,-19.4),(1.15,.16,3.15),'roof',g['lead'],front)
