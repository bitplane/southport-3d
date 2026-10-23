"""11–13: low glazed upper frontage, pitched front and stepped rear roofs."""
from facades import rect
from southport3d.geometry import Mesh


def build(f):
    w=f.w
    cream=f.mat('William Hill off white render',(.66,.65,.59))
    blue=f.mat('William Hill navy fascia',(.025,.055,.15))
    white=f.mat('Shop white lettering',(.87,.88,.84))
    grey=f.mat('William Hill aluminium frames',(.33,.35,.34))
    felt=f.mat('Shop weathered felt',(.13,.14,.14))
    f.enclosed('William Hill front',0,w,0,7.0,5.6,cream)
    holes=[rect(.35,.15,w-.35,2.85),rect(.35,3.95,w-.35,5.25)]
    f.wall('Envelope William Hill frontage',rect(0,0,w,5.6),holes,cream)
    f.window('William Hill ribbon',w/2,4.6,w-.7,1.3,grey,mullions=5,transom=-.58)
    # Three fixed display bays and recessed door at the south end.
    for j in range(3):
        x=.35+(w-1.85)*((j+.5)/3)
        f.window('William Hill display',x,1.5,(w-1.85)/3-.03,2.7,grey,transom=.96)
    f.window('William Hill recessed entrance',w-1.05,1.5,1.25,2.7,grey,transom=.95)
    f.box('Trim William Hill canopy',(w/2,3.77,.18),(w+.15,.14,.55),grey)
    gold=f.mat('William Hill gold lettering',(.86,.57,.09))
    f.sign('William Hill first','William',w*.325,3.29,w*.65,.85,blue,gold)
    f.sign('William Hill last','HILL',w*.825,3.29,w*.35,.85,blue,white)
    # Close 3D orbit reveals a pitched front roof behind the low glazed fascia.
    # The pale weathered slope must not be mistaken for a flat roof in plan.
    roofmat=f.mat('KBA dark slate',(.17,.18,.175))
    m=Mesh('Roof William Hill front pitch')
    top=[(0,5.6,0),(w,5.6,0),(w,6.9,-7),(0,6.9,-7)]
    m.add(top+[(x,y-.12,z) for x,y,z in top],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    f.finish(m,[roofmat])
    for u in [0,w]:
        m=Mesh('Envelope William Hill sloping side')
        m.add([(u,5.6,0),(u,5.6,-7),(u,6.9,-7)],[(0,1,2)])
        f.finish(m,[cream])
    # The aerial shows a lower irregular service extension, not a full-height
    # box throughout the vendor's 20.4 m built depth.
    f.box('Envelope William Hill rear extension',(w/2,2.65,-13.7),(w,5.3,13.4),cream)
    f.box('Roof William Hill rear connector',(w/2,5.38,-8.5),(w,.16,3),felt)
    f.roof('William Hill rear gable',1.4,w,10,20.4,5.3,7.55,roofmat)
    for d in [10,20.4]:
        m=Mesh('Envelope William Hill rear gable')
        m.add([(1.4,5.3,-d),(w,5.3,-d),((w+1.4)/2,7.55,-d)],[(0,1,2)])
        f.finish(m,[cream])
    f.box('Roof William Hill side service strip',(.7,5.37,-15.2),(1.4,.14,10.4),felt)
