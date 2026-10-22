"""Anchor Street redevelopment, calibrated to RGP Architects' exterior photographs."""
import math
from mathutils import Matrix
from southport3d.geometry import Mesh
from components import wall, rect, sash


def build_rear(g):
    front=g['front'];finish=g['finish'];box=g['box'];instance=g['instance']
    brick=g['brick'];cream=g['cream'];glass=g['glass'];white=g['white'];flat=g['flat']
    blue=g['material']('Modern blue metal railings',(.12,.25,.34))
    f=front@Matrix.Translation((29.3,0,-54.3))@Matrix.Rotation(math.pi,4,'Y')
    w=28.3;h=12.6
    # Brick lower floors, a light framed attic, and taller rendered corner tower.
    holes=[]
    for x in [1.8,4.8,16.3,19.3,22.3]:
        for z in [3.0,6.6]:holes.append(rect(x-.57,z-1.0,x+.57,z+1.0))
    holes += [rect(7.0,.1,10.6,8.7),rect(12.0,4.9,14.9,8.0),rect(12.0,.1,14.9,3.0)]
    finish(wall('Envelope modern Anchor brick',rect(0,0,24.3,9.1),holes),'rear-range',[brick],f)
    upper=[rect(x-.83,9.5,x+.83,11.9) for x in [1.7,4.4,12.6,15.3,18,20.7,23.2]]+[rect(6.2,9.5,10.6,11.9)]
    finish(wall('Envelope modern Anchor attic',rect(0,9.1,24.3,h),upper),'rear-range',[cream],f)
    for x in [1.8,4.8,16.3,19.3,22.3]:
        for z in [3.0,6.6]:instance('modern-white',sash('Window modern white sash',1.14,2.0),f@Matrix.Translation((x,z,0)),'rear-range',[glass,white])
    for x in [1.7,4.4,12.6,15.3,18,20.7,23.2]:instance('modern-blue',sash('Window modern blue door',1.66,2.4),f@Matrix.Translation((x,10.7,0)),'rear-range',[glass,blue])
    for x,z,ww,hh in [(8.8,4.4,3.6,8.6),(13.45,6.45,2.9,3.1),(8.4,10.7,4.4,2.4)]:
        m=Mesh('Glazing modern curtain wall');m.box((0,0,-.22),(ww,hh,.05),0)
        for xx in [-ww/2,0,ww/2]:m.box((xx,0,-.10),(.08,hh,.16),1)
        for j in range(int(hh/.85)+1):m.box((0,-hh/2+j*.85,-.10),(ww,.065,.16),1)
        finish(m,'rear-range',[glass,blue],f@Matrix.Translation((x,z,0)))
    towerholes=[rect(25.0,z-1.3,27.4,z+1.3) for z in [2.5,6.1,9.7,13.3]]
    finish(wall('Envelope modern cream corner',rect(24.3,0,w,15.2),towerholes),'rear-range',[cream],f)
    for z in [2.5,6.1,9.7,13.3]:instance('corner-blue',sash('Window modern corner door',2.4,2.6),f@Matrix.Translation((26.2,z,0)),'rear-range',[glass,blue])
    def balcony(x,z,ww):
        box('Balcony modern deck',(x,z,.52),(ww,.16,1.1),'rear-range',blue,f)
        m=Mesh('Balcony modern rails')
        for y in [.35,.68,1.02]:m.tube([(x-ww/2,z+y,1.03),(x+ww/2,z+y,1.03)],.022,sides=6)
        for j in range(max(2,int(ww/.85))+1):
            xx=x-ww/2+j*ww/max(2,int(ww/.85));m.tube([(xx,z,1.03),(xx,z+1.08,1.03)],.028,sides=6)
        for xx in [x-ww/2,x+ww/2]:
            for y in [.35,.68,1.02]:m.tube([(xx,z+y,.05),(xx,z+y,1.03)],.022,sides=6)
        finish(m,'rear-range',[blue],f)
    for x,z,ww in [(3,9.35,5.8),(17,9.35,13.7),(13.45,4.95,3.2)]+[(26.2,z-1.30,2.8) for z in [2.5,6.1,9.7,13.3]]:balcony(x,z,ww)
    # Remaining elevations are deliberately low-detail envelopes with readable
    # openings; exact courtyard fenestration awaits a survey.
    inward=front@Matrix.Translation((1,0,-44.4))
    iholes=[rect(x-.7,z-1.05,x+.7,z+1.05) for x in [10,14,18,22] for z in [3,6.6,10.3]]
    iholes.append(rect(13.4,0,16.3,3.3))
    finish(wall('Envelope modern courtyard',rect(0,0,w,h),iholes),'rear-range',[cream],inward)
    for x in [10,14,18,22]:
        for z in ([6.6,10.3] if x==14 else [3,6.6,10.3]):instance('courtyard-sash',sash('Window modern courtyard',1.4,2.1),inward@Matrix.Translation((x,z,0)),'rear-range',[glass,blue])
    for u in [1,29.3]:box('Envelope modern side',(u,h/2,-49.35),(.30,h,9.9),'rear-range',cream,front)
    for u in [1,5]:box('Envelope modern raised corner side',(u,13.85,-49.35),(.25,2.7,9.9),'rear-range',cream,front)
    box('Envelope modern raised corner courtyard',(3,13.85,-44.4),(4,2.7,.25),'rear-range',cream,front)
    box('Roof modern grey metal',(17.25,12.7,-49.35),(24.8,.20,10.7),'roof',flat,front)
    box('Roof modern corner canopy',(3,15.35,-49.35),(4.8,.20,10.7),'roof',flat,front)
