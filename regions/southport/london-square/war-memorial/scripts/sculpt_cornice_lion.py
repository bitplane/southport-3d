"""Small cornice mask: broad forms visible in the Commons and Flickr elevations.

These views resolve the circular mane and projecting muzzle, not individual
locks or teeth. The symmetric sculpt is explicitly an interpretation.
"""
from pathlib import Path
import json,math
import numpy as np
from sculpt_surface import Surface

ROOT=Path(__file__).resolve().parents[1]
s=Surface((-110,-115,110,115),.220,.230,columns=260,origin_y=-.115)
# Numeric coordinates are a drafting frame in millimetres, not image pixels.
outline=[]
for a in np.linspace(0,math.tau,80,endpoint=False):
    r=1+.035*math.sin(13*a)+.025*math.sin(7*a)
    outline.append((94*r*math.cos(a),99*r*math.sin(a)))
s.region('Rounded scalloped mane',outline,.041,edge=26)
s.ellipse(0,-3,70,82,.055)
# Broad flowing grooves are intentionally restrained at this source resolution.
for side in (-1,1):
    for j in range(5):
        yy=-63+j*30
        s.stroke([(side*53,yy),(side*73,yy+8),(side*82,yy+25)],3,-.006)
    s.ellipse(side*58,-57,17,19,.060,base=.023)
    s.ellipse(side*61,-57,8,10,.063,base=.030)
    s.ellipse(side*29,-8,27,34,.069,base=.036)
    s.stroke([(side*9,-28),(side*24,-37),(side*43,-32)],4,.015)
    s.cut_region('Shallow eye socket',[(side*13,-23),(side*30,-27),
                 (side*42,-22),(side*30,-14),(side*16,-17)],.048,edge=4)
    s.ellipse(side*27,-20,5,3.5,.056,base=.048)
    s.ellipse(side*23,32,30,24,.083,base=.044)
s.ellipse(0,-2,18,35,.092,base=.043)
s.region('Blunt nose',[(-20,16),(-15,11),(0,9),(15,11),(20,16),
                      (11,28),(0,32),(-11,28)],.101,edge=8,base=.063)
s.ellipse(0,62,33,22,.067,base=.027)
s.cut_region('Narrow mouth opening',[(-33,45),(-17,47),(0,43),(17,47),
               (33,45),(23,55),(0,59),(-23,55)],.025,edge=3)
s.stroke([(0,31),(0,43)],2.5,-.009,smooth=False)
dest=ROOT/'research/relief-data/cornice-lion.npz';s.save(dest)
report={'source_images':['commons-columns-1','commons-columns-2','flickr-7465690872',
                         'centenary-11'],
 'coordinate_frame':'Authored millimetre drafting frame; not a source-coordinate trace',
 'model_extent_m':[.220,.230], 'depth_max_m':float(s.z.max()),
 'method':'Authored broad relief forms; no image shading or photographic texture',
 'confidence':'Count and rounded projecting silhouette supported by elevations; fine anatomy and depth estimated',
 'not_claimed':['Exact mane locks','Individual weathering','A measured carving depth','Teeth or hidden anatomy'],
 'layers':s.layers}
(ROOT/'research/relief-data/cornice-lion-traces.json').write_text(json.dumps(report,indent=2)+'\n')
print('CORNICE_LION_SURFACE_WRITTEN',s.z.shape,float(s.z.max()))
