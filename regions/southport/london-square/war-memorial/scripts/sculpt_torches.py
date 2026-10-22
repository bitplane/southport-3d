"""Trace the exterior inverted torches from IWM mont_8a into shallow geometry.

Pixel coordinates refer to the untouched 855 x 1280 photograph. Large shapes
and depth ordering are authored; no photographic colour is put in the model.
The SW carving supplies the common design. Damage on the NE version remains
unreconstructed, rather than interpreting erosion stains as new geometry.
"""
from pathlib import Path
import json
import math
import numpy as np
from sculpt_surface import Surface,curve

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'
OUT.mkdir(exist_ok=True)
s=Surface((246,172,676,556),.94,.84,columns=460,origin_y=-.42)

# Thin suspension cords disappear behind the wreath. The circular suspension
# button is a separate carved ring, with a recessed centre.
for sign in (-1,1):
    s.stroke([(459+sign*6,228),(459+sign*34,270),(459+sign*45,291)],2.4,.018,'max')
    s.stroke([(459+sign*2,230),(459+sign*9,263)],2.0,.021,'max')
s.ellipse(459,211,22,22,.035)
s.ring(459,211,20,20,3.4,.046)
s.ring(459,211,15,15,1.8,.041)

# Broad, fluted timber/metal torch bodies behind the front leaf wreath.
def shaft(a,b,half_width,depth,name):
    a=np.asarray(a,float);b=np.asarray(b,float)
    v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
    s.region(name,[tuple(a-n*half_width),tuple(a+n*half_width),
                   tuple(b+n*half_width*1.1),tuple(b-n*half_width*1.1)],depth,edge=3,smooth=False)
    return a,b,n

shaft((341,252),(594,497),12,.040,'Rear descending torch shaft')
shaft((576,252),(330,498),12,.042,'Rear ascending torch shaft')

# The wreath is a thick ring with overlapping long laurel leaves at the sides,
# braided leaf clusters at the foot, and wrapped bands across the crown.
s.annulus(459,372,94,95,18,.039)
left_body=[(393,288),(371,306),(352,332),(343,359),(347,389),
           (358,418),(375,439),(401,454),(412,434),(391,412),
           (383,384),(382,354),(391,327),(410,306)]
for sign in (-1,1):
    outline=left_body if sign<0 else [(918-x,y) for x,y in left_body]
    s.region('Continuous laurel bundle beneath leaves',outline,.043,edge=8)
for sign in (-1,1):
    # Three overlapping ranks, tracing the visible hanging pointed leaves.
    banks=[[(365,313),(368,348),(372,380)],[(355,337),(357,371),(364,407)],
           [(372,334),(374,370),(381,405)]]
    for bank in banks:
        for x,y in bank:
            xx=x if sign<0 else 918-x
            tx=xx+sign*4;ty=y+47
            s.leaf((xx,y),(tx,ty),10.5,.061,.035)
    for j in range(5):
        x=405+j*9 if sign<0 else 513-j*9
        y=445+8*math.sin(j*.4)
        s.leaf((x+sign*16,y-4),(x-sign*18,y+15),7.5,.054,.025)
        s.leaf((x+sign*13,y+11),(x-sign*18,y+23),7,.053,.026)

# Top wrapping is a bundle with folded, curved edges, not a smooth torus.
s.region('Wreath upper binding',[(392,273),(405,260),(428,253),(458,257),
    (481,252),(513,264),(526,278),(510,302),(493,299),(471,285),
    (446,288),(421,303),(407,300)],.061,edge=5)
for line in [[(401,272),(413,289),(422,298)],[(409,265),(421,280),(430,292)],
             [(418,261),(429,274),(439,287)],[(431,260),(441,270),(447,282)],
             [(480,259),(472,270),(467,283)],[(491,258),(483,273),(477,287)],
             [(501,262),(492,278),(487,291)],[(512,267),(501,285),(495,294)]]:
    s.stroke(line,1.3,-.005)
s.region('Wreath lower vertical binding',[(451,445),(464,446),(468,484),(454,484)],.063,edge=2)
s.stroke([(455,449),(458,480)],1,-.003,smooth=False)

# Long hanging ribbons inside each handle loop, ending in curled points.
for sign in (-1,1):
    xx=304 if sign<0 else 615
    s.region('Hanging flat cord',[(xx-3,241),(xx+4,243),(xx+3,393),
        (xx+sign*6,404),(xx+sign*1,410),(xx-3,402)],.023,edge=1.7)
    s.stroke([(xx+8,245),(xx+8,386),(xx+7,407),(xx+12,415),(xx+7,424)],1.6,.027,'max')
    s.stroke([(xx-1,398),(xx+sign*5,408),(xx-1,416)],1.1,.027,'max')

# Torch handles are open oval loops, with a knot fastening each one to the
# diagonal shaft. Their openings stay at the backing plane.
left=[(301,245),(289,233),(290,217),(301,203),(317,195),(333,196),
      (343,205),(343,218),(331,235),(317,248),(301,245)]
right=[(592,247),(579,236),(573,220),(576,204),(588,197),(601,199),
       (617,209),(633,225),(631,239),(619,248),(607,251),(592,247)]
for outline in [left,right]:
    s.stroke(outline,5.1,.057,'max')
    for a,b in zip(outline[2:6:2],outline[3:7:2]):
        s.stroke([a,b],1.4,.004)
for poly in [[(311,207),(319,202),(335,218),(326,226)],
             [(594,201),(605,207),(596,223),(586,217)]]:
    s.region('Loop fastening knot',poly,.069,edge=3)
for a,b in [((330,237),(350,260)),((586,239),(568,260))]:
    shaft(a,b,8,.065,'Handle neck joining the fluted stem')

# Visible shaft segments pass in front of the wreath. The small collar at the
# crossing is carved with folds, followed by the wider flared cups below.
for a,b in [((340,255),(384,297)),((382,296),(595,502)),
            ((575,253),(537,291)),((537,291),(329,500))]:
    aa,bb,n=shaft(a,b,11.5,.071,'Exposed fluted shaft segment')
    for offset in [-7,-2,3,8]:
        s.stroke([tuple(aa+n*offset),tuple(bb+n*offset)],1.05,-.005,smooth=False)
    for offset in [-9,10]:
        s.stroke([tuple(aa+n*offset),tuple(bb+n*offset)],.9,.002,smooth=False)

s.region('Crossed torch centre binding',[(431,352),(448,349),(474,350),
    (490,355),(488,369),(464,372),(442,368)],.085,edge=3)
s.stroke([(435,356),(457,359),(485,358)],1,-.004)
s.stroke([(438,365),(458,362),(485,365)],1,-.003)

for sign in (-1,1):
    # Left cup is mirrored to the right, with independently traced flames below.
    poly=[(338,462),(353,477),(326,513),(303,493)]
    if sign>0:poly=[(918-x,y) for x,y in poly]
    s.region('Fluted torch flared cup',poly,.075,edge=3)
    for j in range(4):
        a=(337+j*4,469+j*3);b=(311+j*5,493+j*4)
        if sign>0:a=(918-a[0],a[1]);b=(918-b[0],b[1])
        s.stroke([a,b],1.2,-.005,smooth=False)
    for a,b in [((333,459),(356,480)),((301,491),(327,516))]:
        if sign>0:a=(918-a[0],a[1]);b=(918-b[0],b[1])
        s.stroke([a,b],3.2,.080,'max',smooth=False)

s.region('Left inverted flame',[(305,496),(323,513),(318,527),(303,535),
    (288,538),(277,544),(265,539),(259,528),(261,519),(267,520),
    (268,532),(276,532),(281,521),(287,515),(298,514)],.067,edge=4)
s.region('Right inverted flame',[(594,516),(614,496),(625,511),(632,515),
    (640,522),(648,532),(656,530),(661,518),(668,524),(663,537),
    (652,545),(635,546),(620,539),(605,534)],.069,edge=4)
for line in [[(308,509),(303,520),(291,526),(276,535)],
             [(314,516),(307,529),(294,533),(282,538)],
             [(299,508),(293,518),(284,522)],
             [(610,510),(619,521),(633,527),(650,536)],
             [(603,519),(612,530),(631,538),(650,541)],
             [(618,509),(629,520),(640,525)]]:
    s.stroke(line,1.35,-.005)

residual=s.detail_from_shading(ROOT/'references/images/iwm-mont_8a.jpg',
                              light=(-.4,-.9),amount=.6,limit=.003)
# The first raking-light study exaggerated the relief projection. Preserve the
# traced overlaps while bringing the unsupported depth estimate below 61 mm.
s.z=.001+(s.z-.001)*.70
s.save(OUT/'crossed-torches.npz')
metadata={'name':'Crossed inverted exterior torches','source_image':'references/images/iwm-mont_8a.jpg',
          'source_page':'https://memorials.iwm.org.uk/memorial/1228','source_credit':'David Long',
          'cross_checked_with':['iwm-mont_8.jpg','wmo-Southport_6.jpg'],
          'source_pixel_bounds':s.bounds.tolist(),'width_m':s.width,'height_m':s.height,
          'origin_y_m':s.origin_y,'layers':s.layers,'fine_detail':residual,'depth_multiplier_after_sculpt':.70,
          'uncertainty':'All depths estimated. SW reference represents common design; NE erosion differs. Physical size is a photographic estimate.'}
(OUT/'crossed-torches-traces.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('SCULPTED_CROSSED_TORCHES',s.z.shape,'depth range',float(s.z.min()),float(s.z.max()))
