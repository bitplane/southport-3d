"""11–13: low glazed upper frontage, flat stepped rear service roof."""
from facades import rect


def build(f):
    w=f.w
    cream=f.mat('William Hill off white render',(.66,.65,.59))
    blue=f.mat('William Hill navy fascia',(.025,.055,.15))
    white=f.mat('Shop white lettering',(.87,.88,.84))
    grey=f.mat('William Hill aluminium frames',(.33,.35,.34))
    felt=f.mat('Shop weathered felt',(.13,.14,.14))
    f.enclosed('William Hill front',0,w,0,7.0,6.15,cream)
    holes=[rect(.35,.15,w-.35,2.85),rect(.35,4.02,w-.35,5.75)]
    f.wall('Envelope William Hill frontage',rect(0,0,w,6.15),holes,cream)
    f.window('William Hill ribbon',w/2,4.885,w-.7,1.73,grey,mullions=5,transom=-.58)
    # Three fixed display bays and recessed door at the south end.
    for j in range(3):
        x=.35+(w-1.85)*((j+.5)/3)
        f.window('William Hill display',x,1.5,(w-1.85)/3-.03,2.7,grey,transom=.96)
    f.window('William Hill recessed entrance',w-1.05,1.5,1.25,2.7,grey,transom=.95)
    f.box('Trim William Hill canopy',(w/2,3.77,.18),(w+.15,.14,.55),grey)
    f.sign('William Hill','William HILL',w/2,3.29,w,.85,blue,white)
    f.box('Roof William Hill front flat',(w/2,6.12,-3.5),(w,.16,7),felt)
    # The aerial shows a lower irregular service extension, not a full-height
    # box throughout the vendor's 20.4 m built depth.
    f.box('Envelope William Hill rear extension',(w/2,2.35,-13.7),(w,4.7,13.4),cream)
    f.box('Roof William Hill rear felt',(w/2,4.78,-13.7),(w,.16,13.4),felt)
    for d in [9,14,18]:
        f.box('Envelope William Hill rooflight kerb',(w/2,4.95,-d),(1.5,.25,1.25),grey)
        f.box('Window William Hill rooflight',(w/2,5.095,-d),(1.38,.04,1.13),f.mat('Shop dark glazing',(.07,.105,.12)))
