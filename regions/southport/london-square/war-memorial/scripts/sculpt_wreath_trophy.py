"""Exterior flowered trophy, traced from David Long's IWM mont_13a photo.

The original photograph remains untouched. This creates an editable numeric
relief surface from authored outlines and estimated overlapping depth layers.
"""
from pathlib import Path
import json,math
import numpy as np
from sculpt_surface import Surface

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'
s=Surface((55,68,1205,391),2.0,.55,columns=900,origin_y=-.275)

def band(name,points,depth=.04,edge=4):
    s.region(name,points,depth,edge=edge)

# Long crossing weapons are behind the wreath. The scabbard mouths and curved
# ends are visible; blade/hilt directions follow the photograph individually.
band('Upper left scabbard behind wreath',[(313,91),(336,88),(355,96),(357,110),
    (348,119),(331,117),(318,115),(308,129),(900,316),(890,344),(299,146),
    (285,132),(288,115),(297,99)],.034)
band('Upper right scabbard behind wreath',[(400,302),(961,116),(973,105),
    (985,104),(997,111),(1006,124),(1007,134),(998,145),(985,143),
    (975,134),(430,336)],.038)
for a in [[(321,125),(884,325)],[(432,321),(986,125)]]:
    s.stroke(a,1.4,-.003,smooth=False)
for cx in (476,788):
    band('Horizontal weapon fitting',[(cx-36,91),(cx+28,94),(cx+30,116),
        (cx+12,120),(cx+14,131),(cx-8,133),(cx-8,115),(cx-38,114)],.029,2)
    s.stroke([(cx-31,100),(cx+22,102)],2,.004,smooth=False)
s.stroke([(463,115),(791,121)],5,.027,'max',smooth=False)

# Sword grips and the two quillons, seen below the wreath.
band('Left lower grip',[(294,331),(401,305),(423,331),(309,368),
    (285,371),(267,369),(275,349)],.045)
band('Right lower grip',[(889,315),(1006,347),(1026,362),(1027,381),
    (1010,387),(990,374),(883,345)],.043)
band('Left cross guard',[(389,279),(411,272),(417,291),(437,340),
    (447,352),(459,352),(465,364),(458,374),(444,374),(432,354),
    (407,364),(400,349),(405,337)],.055,3)
band('Right cross guard',[(886,279),(900,281),(916,291),(915,310),
    (905,320),(906,356),(898,374),(884,373),(877,364),(881,349),
    (878,323),(858,316),(864,301)],.055,3)
for a,b in [((292,348),(397,318)),((292,356),(402,326)),
            ((898,330),(1009,366)),((894,337),(1006,374))]:
    s.stroke([a,b],1.3,-.003,smooth=False)
for cx,cy in [(414,340),(891,329)]:
    s.stroke([(cx-13,cy-24),(cx+1,cy+21)],2,-.004,smooth=False)

# Braziers: raised bowls, fine shaft fluting, stepped bases, feet and flames.
def brazier(cx,top,base):
    band('Brazier fluted pedestal',[(cx-25,top+75),(cx+22,top+75),
        (cx+29,base-52),(cx+37,base-31),(cx-42,base-31),(cx-28,base-52)],.042,4)
    for dx in [-19,-12,-5,2,9,16]:
        s.stroke([(cx+dx,top+87),(cx+dx*1.22,base-52)],1.3,-.003,smooth=False)
    band('Brazier spreading bowl',[(cx-63,top+26),(cx+67,top+27),
        (cx+56,top+42),(cx+37,top+56),(cx+19,top+65),(cx-22,top+65),
        (cx-40,top+55),(cx-59,top+43)],.052,4)
    for y,w in [(top+27,64),(top+57,28),(top+73,25),(base-45,30),(base-28,46),(base-12,55)]:
        s.stroke([(cx-w,y),(cx+w,y)],3.1,.056,'max',smooth=False)
    band('Brazier base plinth',[(cx-40,base-32),(cx+39,base-32),
        (cx+54,base-14),(cx+59,base),(cx+29,base),(cx+26,base-13),
        (cx-22,base-13),(cx-27,base),(cx-59,base),(cx-53,base-16)],.047,3)
    for dx,dy in [(-38,4),(-21,-2),(-3,-6),(16,-3),(34,6)]:
        x=cx+dx;y=top+dy
        band('Small brazier flame',[(x-13,y+26),(x-12,y+15),(x-4,y+7),
             (x-3,y),(x+6,y+8),(x+13,y+16),(x+10,y+27)],.050,3)
        s.stroke([(x-4,y+22),(x+3,y+13),(x-1,y+5)],1.0,-.003)
brazier(173,78,373)
brazier(1101,102,387)

# Garland hanging from each brazier to the central wreath. The long folded
# ribbons and the flower-rich bulges are distinct pieces of the carving.
left=[(201,149),(225,154),(249,180),(289,204),(333,219),(374,216),
      (420,201),(470,170),(518,140),(531,153),(511,186),(482,218),
      (442,253),(404,273),(362,279),(321,272),(282,256),(246,235),
      (224,207),(208,198),(194,207),(190,191)]
right=[(774,164),(816,181),(858,212),(904,233),(953,234),(999,216),
       (1036,184),(1067,163),(1092,162),(1092,201),(1066,209),(1046,235),
       (1018,260),(979,279),(936,287),(890,282),(848,265),(816,238),(788,208)]
band('Left flower festoon',left,.054,7)
band('Right flower festoon',right,.054,7)
for side in [-1,1]:
    cx=173 if side<0 else 1101
    band('Garland knot around brazier',[(cx-43,168 if side<0 else 190),
        (cx-14,156 if side<0 else 180),(cx+23,160 if side<0 else 183),
        (cx+45,176 if side<0 else 198),(cx+36,196 if side<0 else 217),
        (cx+11,190 if side<0 else 211),(cx-17,194 if side<0 else 216),
        (cx-40,186 if side<0 else 209)],.065,5)
    x=99 if side<0 else 1181;y=211 if side<0 else 237
    band('Hanging flower bundle',[(x-8,y-52),(x+8,y-53),(x+17,y-14),
        (x+22,y+37),(x+8,y+57),(x-11,y+58),(x-24,y+40),(x-17,y-4)],.050,5)
    s.stroke([(x+2,y-39),(x-5,y-4)],1.3,-.003)

def rose(x,y,r=10,depth=.066):
    s.ellipse(x,y,r,r,depth-.009)
    for j,(radius,start) in enumerate([(r*.75,.1),(r*.48,1.0),(r*.24,.2)]):
        pts=[(x+radius*math.cos(a),y+radius*math.sin(a))
             for a in np.linspace(start,start+math.tau*.82,24)]
        s.stroke(pts,max(1.1,r*.14),depth+j*.001,'max',smooth=False)
    s.ellipse(x+1,y+1,r*.17,r*.17,depth+.004,base=depth-.01)

for x,y,r in [(313,231,11),(328,246,10),(345,252,10),(355,235,11),(376,246,9),
              (393,251,10),(410,236,10),(426,224,9),(293,221,7),
              (865,239,10),(881,254,10),(899,253,9),(918,263,10),(940,264,11),
              (962,260,10),(981,247,10),(997,236,9),
              (87,249,9),(101,259,9),(111,245,8),(92,234,7),
              (1173,274,9),(1189,282,9),(1195,268,8),(1176,259,8)]:
    rose(x,y,r)
for line in [[(234,181),(249,209),(272,231)],[(247,181),(258,208),(282,236)],
             [(443,206),(458,219),(467,225)],[(453,198),(470,211),(477,217)],
             [(808,198),(796,213)],[(819,204),(806,222)],
             [(1049,194),(1034,218),(1016,240)],[(1060,191),(1048,221),(1029,246)]]:
    s.stroke(line,1.5,-.004)

# Large circular wreath, with four long leafy bundles and three wrapped bands.
cx,cy=646,233
s.annulus(cx,cy,120,118,25,.057)
for a0,a1 in [(-2.95,-1.80),(-1.36,-.36),(.36,1.03),(2.10,2.78)]:
    for radius in [101,111,122,133,142]:
        pts=[(cx+radius*math.cos(a),cy+radius*math.sin(a)) for a in np.linspace(a0,a1,40)]
        s.stroke(pts,2.1,-.005,smooth=False)
    for a in [a0+.04,a1-.04]:
        pts=[(cx+r*math.cos(a+(r-120)*.001),cy+r*math.sin(a+(r-120)*.001)) for r in np.linspace(101,143,10)]
        s.stroke(pts,2,.063,'max',smooth=False)
for a in [-math.pi/2,.78,2.37]:
    pts=[(cx+r*math.cos(aa),cy+r*math.sin(aa)) for r,aa in
         [(97,a-.10),(143,a-.09),(146,a+.10),(98,a+.10)]]
    band('Wreath broad tying band',pts,.069,3)
    for da in [-.065,.065]:
        s.stroke([(cx+102*math.cos(a+da),cy+102*math.sin(a+da)),
                  (cx+141*math.cos(a+da),cy+141*math.sin(a+da))],1.3,-.003,smooth=False)

for x,y,r in [(536,191,10),(529,211,10),(521,230,9),(542,219,10),(548,199,8),
              (746,185,10),(760,201,10),(768,221,10),(746,215,8),(734,199,8),
              (586,339,11),(605,346,11),(625,354,10),(643,357,10),(660,357,10),
              (679,350,11),(697,342,11),(713,331,10),(616,332,10),(641,334,9),(668,333,10)]:
    rose(x,y,r,.073)

detail=s.detail_from_shading(ROOT/'references/images/iwm-mont_13a.jpg',
                            light=(-.45,-.85),amount=.55,limit=.003)
s.z=.001+(s.z-.001)*.75
s.save(OUT/'trophy-wreath.npz')
meta={'name':'Flowered wreath, crossed swords, festoons and braziers',
      'source_image':'references/images/iwm-mont_13a.jpg','source_page':'https://memorials.iwm.org.uk/memorial/1228',
      'credit':'David Long','source_pixel_bounds':s.bounds.tolist(),'width_m':s.width,'height_m':s.height,
      'origin_y_m':s.origin_y,'layers':s.layers,'fine_detail':detail,'depth_multiplier_after_sculpt':.75,
      'uncertainty':'Photographic outline interpretation and estimated depth. One common motif shared across SW panels; local damage and individual differences not reconstructed.'}
(OUT/'trophy-wreath-traces.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SCULPTED_WREATH_TROPHY',s.z.shape,'depth range',float(s.z.min()),float(s.z.max()))
