"""Pelta trophy: authored relief traced in the unchanged IWM mont_13 photo.

The two lion-ended horns, palmette, straps, palm branches, weapons, braziers
and hanging fabric are traced separately. Depth remains an interpretation.
"""
from pathlib import Path
import json,math
import numpy as np
from sculpt_surface import Surface,curve

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'
s=Surface((151,113,1148,371),2.0,.52,columns=1000,origin_y=-.26)

def region(name,points,z=.040,edge=4,**kw):s.region(name,points,z,edge=edge,**kw)
def mirror(points):return [(1286-x,y) for x,y in points]

# The horizontal sword has a decorated left termination and a bound right
# grip. A second long rod runs beneath it, behind the shield and its straps.
region('Long sword or scabbard',[(370,159),(849,153),(851,199),(373,202)],.025,2)
for y in [164,191]:s.stroke([(381,y),(844,y-3)],1.5,-.0025,smooth=False)
region('Decorated left weapon terminal',[(355,160),(369,158),(382,163),
    (385,177),(381,193),(369,202),(355,205),(343,196),(338,184),(344,168)],.038,3)
for line in [[(354,166),(367,166),(373,171),(363,177),(353,178)],
             [(350,181),(359,184),(352,190),(357,197),(366,194)],
             [(364,179),(374,182),(369,188),(377,190)]]:
    s.stroke(line,1.5,-.004)
region('Right sword grip',[(873,161),(916,160),(948,156),(966,161),
    (974,174),(970,188),(950,194),(875,191)],.040,4)
region('Right sword guard',[(849,148),(872,146),(878,153),(876,201),
    (855,203),(850,195)],.048,2)
for x in [855,862,870]:s.stroke([(x,154),(x,196)],1.2,-.003,smooth=False)
for x in range(881,960,9):
    s.stroke([(x,167),(x+14,159)],1.2,-.003,smooth=False)
    s.stroke([(x,189),(x+24,168)],1.2,-.003,smooth=False)
s.stroke([(184,225),(344,222),(977,216),(1097,214)],7.5,.028,'max')
for cx,y in [(292,222),(997,218)]:
    for dx in [-9,-3,3,9]:s.stroke([(cx+dx,y-9),(cx+dx,y+9)],2,.037,'max',smooth=False)
    for dx in [-4,2,7]:
        s.stroke([(cx+dx,y+5),(cx+dx-2,y+22),(cx+dx-7,y+40)],2,.033,'max')

# Paired palm fronds. Their stems and long leaves remain behind the shield.
upper=[(325,330),(345,298),(380,276),(418,266),(456,269),(492,283)]
lower=[(356,359),(397,349),(437,339),(480,330),(525,332),(558,344)]
for sign in [-1,1]:
    transform=lambda p: p if sign<0 else (1286-p[0],p[1])
    s.stroke([transform(p) for p in upper],2.3,.030,'max')
    s.stroke([transform(p) for p in lower],2.1,.027,'max')
    # Each pair follows the photographed change in direction along the branch.
    for x,y,tx,ty in [(329,321,321,340),(335,308,320,325),(344,297,325,310),
        (355,286,333,295),(367,278,345,284),(381,273,360,270),
        (396,269,376,258),(412,268,393,254),(429,268,412,253),
        (445,269,434,255),(460,273,453,259),(475,277,470,263),
        (337,313,353,291),(346,300,368,283),(360,288,383,276),
        (376,278,400,274),(391,271,415,274),(410,268,433,278),
        (430,269,449,286),(448,272,466,292),(465,277,482,298)]:
        s.leaf(transform((x,y)),transform((tx,ty)),4.5,.036,.013)
    for x,y,tx,ty in [(371,354,392,357),(386,351,410,359),(402,347,427,356),
        (418,343,445,352),(435,339,463,349),(452,335,479,347),
        (471,332,494,344),(488,331,512,343),(386,350,404,337),
        (402,346,419,331),(420,341,436,325),(438,336,456,320),
        (456,332,479,316),(477,330,497,317),(496,332,518,321)]:
        s.leaf(transform((x,y)),transform((tx,ty)),4,.032,.012)

def brazier(cx,top,bottom):
    # Smooth centre shaft, short fluted collars at its ends.
    region('Brazier shaft',[(cx-20,top+75),(cx+18,top+75),
        (cx+23,bottom-69),(cx+25,bottom-53),(cx-27,bottom-53),
        (cx-23,bottom-70)],.037,4)
    for y0,y1 in [(top+51,top+77),(bottom-88,bottom-53)]:
        region('Short fluted brazier collar',[(cx-23,y0),(cx+23,y0),
            (cx+25,y1),(cx-25,y1)],.044,2)
        for dx in range(-18,23,7):s.stroke([(cx+dx,y0+3),(cx+dx,y1-3)],1.1,-.004,smooth=False)
    region('Brazier cup',[(cx-53,top+22),(cx+54,top+22),(cx+47,top+37),
        (cx+28,top+49),(cx+19,top+54),(cx-20,top+54),(cx-38,top+45),
        (cx-51,top+33)],.049,4)
    s.stroke([(cx-54,top+23),(cx,top+20),(cx+54,top+23)],3.0,.053,'max')
    for y,w in [(top+53,22),(top+77,24),(bottom-53,25),
                (bottom-43,30),(bottom-29,46),(bottom-18,51)]:
        s.stroke([(cx-w,y),(cx+w,y)],2.8,.050,'max',smooth=False)
    region('Brazier spreading foot',[(cx-27,bottom-46),(cx+28,bottom-46),
        (cx+41,bottom-31),(cx+55,bottom-22),(cx+56,bottom-12),
        (cx+68,bottom-7),(cx+61,bottom),(cx+35,bottom),(cx+30,bottom-11),
        (cx-30,bottom-11),(cx-35,bottom),(cx-67,bottom),(cx-70,bottom-7),
        (cx-56,bottom-14),(cx-52,bottom-25),(cx-39,bottom-32)],.047,3)
    for j,dx in enumerate(range(-35,36,10)):
        yy=top+(3 if j%2 else 6)
        region('Curled brazier flame',[(cx+dx-7,top+19),(cx+dx-9,yy+4),
             (cx+dx-3,yy-4),(cx+dx+4,yy-5),(cx+dx+8,yy+1),
             (cx+dx+3,yy+8),(cx+dx+6,top+19)],.048,2)
        s.stroke([(cx+dx,top+17),(cx+dx-2,yy+6),(cx+dx+3,yy)],.8,-.003)
    # Curled fabric lugs and the long hanging tails flanking the standard.
    for sign in [-1,1]:
        region('Brazier upper fabric loop',[(cx+sign*43,top+35),(cx+sign*53,top+28),
             (cx+sign*60,top+40),(cx+sign*58,top+57),(cx+sign*47,top+69),
             (cx+sign*28,top+68),(cx+sign*24,top+55),(cx+sign*39,top+59),
             (cx+sign*45,top+49)],.039,3)
        x=cx+sign*57
        region('Brazier hanging ribbon',[(x-sign*8,top+79),(x+sign*10,top+75),
             (x+sign*10,bottom-70),(x+sign*15,bottom-54),
             (x+sign*7,bottom-40),(x-sign*3,bottom-45),
             (x+sign*1,bottom-59),(x-sign*8,bottom-72)],.032,3)
        for yy in [top+101,bottom-88,bottom-69]:
            s.stroke([(x-sign*7,yy),(x+sign*9,yy+3)],1.4,-.004,smooth=False)
brazier(245,122,365)
brazier(1047,114,359)

# Palmette behind the shield's raised central neck.
for j in range(11):
    a=math.pi+j*math.pi/10
    tip=(643+47*math.cos(a),151+34*math.sin(a))
    s.leaf((643+(j-5)*2,154),tip,5.5,.047,.016)
s.stroke([(594,154),(643,151),(690,155)],3,.049,'max')

shield=[(458,164),(460,216),(477,265),(510,307),(560,338),
    (611,354),(662,356),(716,343),(767,318),(806,279),(829,234),
    (835,168),(813,163),(802,188),(786,207),(764,220),(736,221),
    (715,212),(698,191),(689,164),(595,165),(588,187),(572,208),
    (548,220),(521,220),(501,204),(487,179)]
region('Solid pelta shield',shield,.050,edge=8,bulge=(646,272,170,94,.006))
rim=[(471,193),(475,228),(493,267),(526,303),(569,327),(617,341),
     (664,342),(708,330),(751,309),(786,278),(809,235),(819,195)]
s.stroke(rim,5,.067,'max')
s.stroke([(x+(2 if x<643 else -2),y-8) for x,y in rim],1.3,-.004)
s.stroke([(493,191),(512,215),(539,228),(570,214),(591,186),(599,158),
          (687,157),(696,185),(719,212),(745,225),(774,214),(797,191)],2.4,.057,'max')

# Lion heads terminate both horns, facing into the shield's centre.
head=[(482,146),(498,149),(505,160),(520,167),(514,175),(520,179),
      (511,186),(504,197),(493,202),(480,196),(471,185),(468,172),(472,158)]
for sign in [-1,1]:
    tr=lambda points: points if sign<0 else mirror(points)
    region('Lion terminal head',tr(head),.070,edge=4)
    for line in [[(478,154),(475,167),(480,181),(488,188)],
        [(484,151),(479,165),(484,177),(493,184)],
        [(490,153),(485,163),(488,173),(498,179)],
        [(475,181),(478,190),(489,197)],
        [(491,164),(496,166),(502,165)],[(501,180),(510,182),(515,179)],
        [(501,187),(496,192),(502,194)]]:
        s.stroke(tr(line),1.2,-.004)
    ex=487 if sign<0 else 1286-487
    s.ellipse(ex,157,4,5,.074,base=.060)
    ex=497 if sign<0 else 1286-497
    s.stroke([(ex,167),(ex+.1,167)],1.0,-.006)
    ex=513 if sign<0 else 1286-513
    s.stroke([(ex,171),(ex+.1,171)],1.1,-.004)

# Two angular riveted straps hang across the upper edge of the shield.
for pts,holes in [([(535,154),(554,153),(552,218),(550,237),(533,243),(529,232),(531,214)],[(541,222),(540,232)]),
    ([(737,153),(758,153),(758,210),(764,226),(760,239),(742,238),(738,219)],[(750,221),(752,231)])]:
    region('Riveted shield suspension strap',pts,.075,edge=2)
    for x,y in holes:
        s.ellipse(x,y,2.5,2.5,.079,base=.070)
        s.stroke([(x,y),(x+.1,y)],1.0,-.007)

detail=s.detail_from_shading(ROOT/'references/images/iwm-mont_13.jpg',light=(-.45,-.85),amount=.65,limit=.003)
s.z=.001+(s.z-.001)*.78
s.save(OUT/'trophy-pelta.npz')
meta={'name':'Lion-ended pelta, palm fronds, weapons and braziers','source_image':'references/images/iwm-mont_13.jpg',
 'source_page':'https://memorials.iwm.org.uk/memorial/1228','credit':'David Long',
 'source_pixel_bounds':s.bounds.tolist(),'width_m':s.width,'height_m':s.height,'origin_y_m':s.origin_y,
 'layers':s.layers,'fine_detail':detail,'depth_multiplier_after_sculpt':.78,
 'uncertainty':'Photographic trace with estimated depth; shared motif does not reproduce individual damage or prove face assignments.'}
(OUT/'trophy-pelta-traces.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SCULPTED_PELTA',s.z.shape,'maximum depth',float(s.z.max()))
