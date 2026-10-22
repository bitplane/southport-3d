"""Winged Victory trophy traced from IWM mont_13b in source pixel coordinates.

Includes the medallion figure, separate helmet profiles, inverted torches,
floral swags and ribbons. Depth and hidden surfaces are estimated, not scanned.
"""
from pathlib import Path
import json,math
import numpy as np
from sculpt_surface import Surface

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'
s=Surface((104,75,1220,341),2.0,.52,columns=1100,origin_y=-.26)
def region(name,p,z=.035,edge=3,**kw):s.region(name,p,z,edge=edge,**kw)
def mirrored(p):return [(1310-x,y) for x,y in p]

# Upper swags, with separate folded cloth and densely flowered sections.
garland=[(174,118),(207,120),(239,129),(279,137),(312,143),(347,143),
    (384,130),(426,128),(457,116),(480,108),(516,92),(525,110),
    (505,133),(478,149),(462,167),(438,180),(411,185),(385,181),
    (352,184),(316,182),(281,171),(244,159),(210,154),(170,151)]
for sign in [-1,1]:
    tr=lambda p: p if sign<0 else mirrored(p)
    region('Heavy floral and cloth swag',tr(garland),.033,6)
    for line in [[(232,135),(239,149),(244,157)],[(244,136),(249,149),(252,159)],
        [(278,144),(294,158),(316,173)],[(286,146),(306,151),(331,154)],
        [(290,157),(314,165),(334,161)],[(472,119),(481,130),(490,133)],
        [(466,130),(476,141),(487,142)],[(462,141),(470,150),(478,151)]]:
        s.stroke(tr(line),1.1,-.003)
    for cx,cy,rx,ry in [(344,161,5,24),(450,148,6,23)]:
        for dy in range(-16,20,8):
            x=cx if sign<0 else 1310-cx
            s.ellipse(x,cy+dy,3.5,3.5,.043,base=.028)
    for x,y,r in [(374,142,6),(390,141,10),(409,150,10),(426,143,7),
                  (371,156,7),(389,163,9),(411,172,9),(429,161,7),
                  (381,179,6),(437,174,6),(365,170,5)]:
        s.flower(x if sign<0 else 1310-x,y,r,.043)
    # Folds and curls above the swag near the medallion's top edge.
    line=[(398,103),(408,108),(420,112),(438,107),(451,97),(466,91),
          (477,94),(478,102),(469,108),(462,104)]
    s.stroke(tr(line),3.5,.034,'max')
    for x,y in [(405,97),(415,104),(426,104),(438,98)]:
        s.stroke(tr([(x,y-4),(x+2,y+7),(x+8,y+5)]),2,.038,'max')

# Short horizontal batons behind the two helmets, with turned ends.
for points in [[(296,194),(414,196),(414,232),(299,228)],
               [(914,199),(1016,199),(1016,234),(916,231)]]:
    region('Horizontal staff behind helmet',points,.024,3)
for cx,cy in [(283,211),(1030,217)]:
    s.ellipse(cx,cy,14,16,.031)
    for dx in [-17,17]:s.stroke([(cx+dx,cy-15),(cx+dx,cy+15)],2.4,.033,'max',smooth=False)

def torch(cx,flip=False):
    region('Inverted torch fluted shaft',[(cx-22,155),(cx+22,155),(cx+26,241),
        (cx+37,269),(cx+45,276),(cx+42,284),(cx-46,284),(cx-43,274),
        (cx-33,267),(cx-25,241)],.040,4)
    for dx in [-17,-11,-5,1,7,13,19]:
        s.stroke([(cx+dx,164),(cx+dx*1.04,223),(cx+dx*1.35,268)],1.2,-.004)
    for y,w in [(157,23),(272,39),(282,45),(291,40)]:
        s.stroke([(cx-w,y),(cx+w,y)],2.7,.047,'max',smooth=False)
    region('Inverted torch flame cluster',[(cx-38,294),(cx+36,294),(cx+39,307),
        (cx+32,322),(cx+20,330),(cx+12,333),(cx+2,329),(cx-7,335),
        (cx-17,328),(cx-30,332),(cx-33,318),(cx-39,310)],.042,3)
    for dx in [-25,-14,-3,8,19,29]:
        s.stroke([(cx+dx,296),(cx+dx+4,307),(cx+dx-2,319),(cx+dx+1,329)],1.2,-.004)
    s.stroke([(cx-16,103),(cx-18,93),(cx-10,87),(cx+13,88),
              (cx+17,96),(cx+12,105),(cx-16,103)],3.3,.035,'max')
    for side in [-1,1]:
        region('Folded upper torch ribbon',[(cx+side*18,114),(cx+side*43,109),
             (cx+side*62,91),(cx+side*76,85),(cx+side*88,89),(cx+side*94,103),
             (cx+side*88,113),(cx+side*92,124),(cx+side*83,132),
             (cx+side*88,142),(cx+side*72,150),(cx+side*50,140),
             (cx+side*28,132)],.033,3)
        for yy in [102,114,127,138]:
            s.stroke([(cx+side*69,yy-4),(cx+side*86,yy)],1.3,-.004,smooth=False)
    region('Torch wrapped fabric knot',[(cx-44,123),(cx-14,118),(cx+12,120),
        (cx+43,133),(cx+46,149),(cx+32,160),(cx+4,154),(cx-19,158),
        (cx-47,148)],.047,4)
    for dx in [-15,2,18]:s.stroke([(cx+dx-7,126),(cx+dx+4,148)],1.2,-.004,smooth=False)
    # The hanging bundle sits on the outer side of each torch.
    ox=cx+(-66 if not flip else 66)
    region('Pendant floral bundle',[(ox-18,163),(ox+20,165),(ox+27,202),
        (ox+18,235),(ox+7,245),(ox-8,245),(ox-23,231),(ox-29,207)],.030,4)
    for j in range(3):
        for k in range(4):s.flower(ox-17+k*11+(j%2)*2,192+j*15,5.8,.041)
torch(201)
torch(1105,True)

# Helmet crests are combed fans following two different photographed profiles.
for cx,cy,a0,a1 in [(441,262,-2.02,.28),(873,264,-1.16,-3.45)]:
    outer=[(cx+93*math.cos(a),cy+92*math.sin(a)) for a in np.linspace(a0,a1,40)]
    inner=[(cx+71*math.cos(a),cy+72*math.sin(a)) for a in np.linspace(a1,a0,40)]
    region('Radiating helmet crest',outer+inner,.040,2,smooth=False)
    for a in np.linspace(a0+.04,a1-.04,29):
        s.stroke([(cx+74*math.cos(a),cy+75*math.sin(a)),
                  (cx+91*math.cos(a),cy+90*math.sin(a))],1.1,-.004,smooth=False)
for cx,cy,flip in [(534,316,False),(775,316,True)]:
    a=np.linspace(math.pi*.45,math.pi*3.0,85)
    rr=np.linspace(19,3,85)
    pts=[(cx+(-1 if flip else 1)*r*math.cos(aa),cy+r*math.sin(aa)) for r,aa in zip(rr,a)]
    s.stroke(pts,3.1,.045,'max',smooth=False)
for p in [[(529,285),(525,297),(520,309),(524,324),(538,330)],
          [(788,288),(786,300),(789,313),(783,327),(770,331)]]:
    s.stroke(p,4.0,.044,'max')

left=[(300,329),(333,330),(372,321),(410,306),(424,330),(444,335),
      (462,329),(453,312),(459,293),(486,292),(500,269),(493,239),
      (476,216),(451,205),(423,205),(398,215),(381,234),(359,258),
      (339,284),(320,311)]
region('Left helmet shell and cheek guard',left,.046,4,bulge=(443,259,45,54,.007))
s.cut_region('Left helmet open eye notch',[(347,267),(358,257),(365,258),(376,280),(366,284),(354,278)],.001,1.5)
s.stroke([(399,216),(405,249),(423,287),(450,308)],2.2,.055,'max')
s.stroke([(304,326),(335,326),(372,317),(408,302)],1.3,-.003)
right=[(1006,332),(974,331),(945,321),(923,302),(907,295),(896,299),
       (894,310),(903,328),(920,337),(898,337),(883,329),(876,314),
       (856,309),(836,294),(819,272),(814,248),(823,223),(841,208),
       (868,199),(893,201),(915,213),(931,232),(947,251),(969,278),(993,307)]
region('Right helmet shell and cheek guard',right,.046,4,bulge=(864,258,45,52,.007))
s.cut_region('Right helmet open eye notch',[(915,268),(923,261),(935,263),(946,270),(966,273),(957,282),(943,279),(930,276),(923,279)],.001,1.5)
s.stroke([(906,216),(900,238),(887,258),(879,275),(865,286),(854,279),
          (856,268),(865,264),(873,268),(870,275)],1.4,-.003)
s.stroke([(1001,329),(973,327),(947,316),(925,299)],1.3,-.003)

# A flat medallion field and raised rim sit in front of the helmets and swags.
cx,cy=656,209
disc=[(cx+141*math.cos(a),cy+129*math.sin(a)) for a in np.linspace(0,math.tau,100,endpoint=False)]
region('Victory medallion field',disc,.020,3,smooth=False)
s.annulus(cx,cy,134,122,6,.035)
s.ring(cx,cy,125,113,1.1,.021)

# Wing feathers, rear leg and streaming cloth precede the torso and forearm.
wing=[(671,148),(658,131),(640,123),(622,126),(602,137),(579,148),
      (558,154),(549,164),(547,176),(553,185),(568,190),(587,186),
      (608,176),(629,165),(651,159)]
region('Victory leftward swept wing',wing,.036,3)
for line in [[(554,158),(565,163),(587,157),(609,145),(638,131)],
             [(552,167),(565,172),(590,163),(616,150),(647,135)],
             [(551,175),(568,181),(590,172),(616,158),(652,141)],
             [(559,184),(576,186),(601,175),(626,162),(657,149)]]:
    s.stroke(line,1.0,-.0025)
for i in range(8):
    x=586+i*8;y=181-i*4
    s.stroke([(x,y-6),(x-3,y+5),(x+1,y+8)],.8,-.002)
region('Trailing bare leg and foot',[(612,246),(611,256),(595,259),(582,269),
    (574,279),(566,282),(562,278),(566,268),(579,253),(595,245)],.037,2)
region('Standing leg and foot',[(657,256),(670,261),(666,284),(662,298),
    (675,305),(686,309),(681,313),(660,310),(648,304),(650,294),(653,276)],.038,2)
for line in [[(660,269),(660,285),(655,299)],[(651,304),(665,307),(680,310)],
             [(570,273),(576,269),(584,261)]]:s.stroke(line,.8,-.002)

robe=[(676,149),(689,154),(697,165),(697,183),(706,196),(696,208),
      (685,211),(675,230),(676,248),(662,263),(645,278),(636,273),
      (626,276),(619,270),(608,270),(603,262),(589,264),(578,259),
      (585,247),(608,236),(631,224),(646,204),(656,180),(667,163)]
region('Victory draped torso and tunic',robe,.038,3,bulge=(681,176,16,21,.005))
for line in [[(674,158),(677,169),(691,177)],[(669,164),(674,177),(692,184)],
    [(665,172),(670,184),(689,191)],[(660,180),(670,193),(686,197)],
    [(654,193),(670,201),(687,203)],[(650,203),(669,208),(682,208)],
    [(645,211),(663,216),(679,214)],[(639,221),(657,222),(674,220)],
    [(628,231),(646,230),(670,226)],[(617,239),(640,238),(665,232)],
    [(605,247),(630,246),(660,237)],[(594,254),(621,255),(650,245)],
    [(623,266),(639,262),(657,250)],[(644,273),(653,262),(665,250)]]:
    s.stroke(line,.85,-.0025)
for poly in [[(680,188),(680,194),(627,211),(587,222),(579,220),(582,215),(624,205),(660,190)],
             [(677,195),(676,201),(631,220),(595,232),(584,228),(587,224),(626,214),(657,200)]]:
    region('Streaming robe tie',poly,.041,1.5)
region('Neck',[(684,145),(699,145),(698,160),(689,165),(679,155)],.044,2)
region('Victory face profile',[(685,117),(699,122),(706,131),(707,137),
    (714,141),(708,145),(710,148),(705,151),(701,157),(693,156),
    (685,149),(680,137),(679,125)],.047,2)
region('Victory swept hair',[(680,114),(688,116),(693,124),(689,137),
    (683,143),(677,138),(675,127)],.049,2)
for tip in [(678,112),(681,114),(685,117),(689,121),(691,125)]:
    s.stroke([(683,139),tip],.6,-.002,smooth=False)
for line in [[(679,120),(683,128),(682,137)],[(683,117),(687,126),(686,136)],
             [(697,135),(704,138)],[(704,149),(709,149)],[(687,139),(689,143)]]:
    s.stroke(line,.7,-.002)
region('Extended bare forearm and hand',[(692,175),(700,185),(710,196),
    (730,202),(739,198),(744,196),(749,201),(747,211),(740,216),
    (728,214),(703,207),(690,195)],.045,2)
for j in range(3):s.stroke([(739+j*2,201),(739+j*2,211)],.55,-.002,smooth=False)

# Palm spray and the downward trumpet are visible beside the hand.
s.stroke([(743,204),(752,184),(749,163),(743,149)],1.4,.040,'max')
for x,y,tx,ty in [(748,170,741,152),(750,177,741,160),(752,183,742,169),
                  (751,175,753,158),(752,182,758,166),(749,192,758,176)]:
    s.leaf((x,y),(tx,ty),2.2,.044,.027)
s.stroke([(738,207),(732,227),(727,246),(722,266)],1.8,.040,'max')
region('Flared downward trumpet bell',[(719,262),(725,264),(728,273),
    (736,277),(732,281),(714,278),(709,275),(717,271)],.043,2)

detail=s.detail_from_shading(ROOT/'references/images/iwm-mont_13b.jpg',light=(-.45,-.85),amount=.60,limit=.0025)
s.z=.001+(s.z-.001)*.85
s.save(OUT/'trophy-victory.npz')
meta={'name':'Winged Victory medallion, helmets, floral swags and inverted torches',
 'source_image':'references/images/iwm-mont_13b.jpg','source_page':'https://memorials.iwm.org.uk/memorial/1228','credit':'David Long',
 'source_pixel_bounds':s.bounds.tolist(),'width_m':s.width,'height_m':s.height,'origin_y_m':s.origin_y,
 'layers':s.layers,'fine_detail':detail,'depth_multiplier_after_sculpt':.85,
 'uncertainty':'Small figure and surface depth interpreted from one photograph. Shared motif; local damage and provisional panel assignments remain documented separately.'}
(OUT/'trophy-victory-traces.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SCULPTED_VICTORY_TROPHY',s.z.shape,'maximum depth',float(s.z.max()))
