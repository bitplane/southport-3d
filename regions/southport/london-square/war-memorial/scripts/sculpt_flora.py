"""Exterior frieze foliage and twelve-petal architectural rosettes.

The source photographs remain unchanged. These are numeric carved surfaces,
with estimated depths and a recorded source-to-drafting-frame transform.
"""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image
from sculpt_surface import Surface

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'

def angular_evidence(image,centre,radius,fractions,modes):
    im=np.asarray(Image.open(ROOT/'references/images'/image).convert('L'),float)
    a=np.linspace(0,math.tau,1024,endpoint=False);out=[]
    for fraction in fractions:
        x=centre[0]+radius*fraction*np.cos(a);y=centre[1]+radius*fraction*np.sin(a)
        i=x.astype(int);j=y.astype(int);u=x-i;v=y-j
        z=(im[j,i]*(1-u)*(1-v)+im[j,i+1]*u*(1-v)+
           im[j+1,i]*(1-u)*v+im[j+1,i+1]*u*v)
        amp=abs(np.fft.rfft(z))/len(z)
        out.append({'radius_fraction':fraction,'strongest_angular_modes':
                    sorted([(n,round(float(amp[n]),3)) for n in modes],key=lambda p:-p[1])[:5]})
    return {'image':image,'centre_px':centre,'radius_px':radius,'samples':out,
            'interpretation':'Corroborates repeated divisions seen visually; not a measurement of carving depth'}

# A local drafting frame removes the slight slope of the photographed frieze.
# One drafting unit is one source pixel; model scale is 4.2 mm per unit.
s=Surface((-100,-40,100,40),.84,.336,columns=680,origin_y=-.168)
def p(x,y):return (x-1019,y-498-.055*(x-1019))
def region(name,points,depth=.020,edge=1.4):
    s.region(name,[p(*q) for q in points],depth,edge=edge)

# The central eight-lobed flower has broad cupped petals and a circular boss.
for i in range(8):
    a=-math.pi/2+i*math.tau/8
    pts=[]
    for r,t in [(8,-.29),(21,-.35),(28,-.28),(29.5,0),(28,.28),(21,.35),(8,.29)]:
        pts.append((r*math.cos(a+t),r*math.sin(a+t)))
    s.region('Broad central flower petal',pts,.023,edge=1.5,base=.003)
    inside=[(r*math.cos(a+t),r*math.sin(a+t)) for r,t in
            [(10,-.12),(21,-.22),(25,-.14),(26,0),(25,.14),(21,.22),(10,.12)]]
    s.cut_region('Shallow cupped petal',inside,.012,edge=1.3)
s.annulus(0,0,29.8,29.8,.9,.018)
s.ellipse(0,0,7.0,7.0,.026,base=.013)
s.annulus(0,0,8.5,8.5,.8,.021)

# Independent left and right contours follow the visible curls and lobes.
for name,pts in [
 ('Left outer lobed fan',[(978,492),(967,478),(956,475),(957,485),(941,476),
   (934,478),(940,490),(930,491),(932,500),(942,502),(936,509),
   (943,518),(953,513),(958,520),(968,516),(970,504),(978,500)]),
 ('Left upper scroll',[(980,496),(977,484),(981,480),(983,474),(979,469),
   (973,470),(971,475),(975,478),(975,483),(969,480),(965,474),
   (968,468),(978,467),(986,473),(987,482),(983,490)]),
 ('Left lower return',[(981,498),(987,501),(988,510),(999,519),(997,525),
   (984,519),(973,518),(970,512),(976,507),(981,509),(983,513),
   (987,514),(982,508),(976,506)]),
 ('Right outer lobed fan',[(1060,500),(1070,488),(1076,486),(1075,495),
   (1084,482),(1091,481),(1093,487),(1087,499),(1102,490),(1110,493),
   (1103,504),(1112,509),(1110,517),(1102,516),(1103,524),
   (1096,527),(1087,520),(1083,525),(1075,526),(1070,518),
   (1073,510),(1065,508)]),
 ('Right upper scroll',[(1054,496),(1056,486),(1053,481),(1058,476),
   (1066,476),(1071,481),(1068,488),(1063,489),(1061,485),
   (1065,482),(1061,481),(1059,486),(1061,490),(1060,498)]),
 ('Right lower return',[(1055,501),(1060,506),(1068,507),(1071,514),
   (1067,521),(1057,521),(1044,526),(1043,522),(1054,516),
   (1063,516),(1065,512),(1059,510),(1056,507)])
]:region(name,pts)
for pts in [[(977,497),(966,494),(948,483)],[(974,499),(955,497),(936,493)],
            [(973,502),(955,504),(944,513)],[(1061,501),(1080,503),(1105,495)],
            [(1063,504),(1082,509),(1099,521)],[(1073,503),(1080,491)]]:
    s.stroke([p(*q) for q in pts],.65,-.003)
s.save(OUT/'frieze-foliage.npz')
frieze={'source_images':['commons-columns-2','flickr-7465690872','commons-columns-1'],
 'source_page':'https://commons.wikimedia.org/wiki/File:Columns,_Southport_Monument_2.JPG',
 'source_to_drafting_frame':'u=x-1019; v=y-498-0.055*(x-1019), pixels in unchanged Commons columns 2',
 'scale_m_per_drafting_unit':.0042,'surface_bounds_drafting':s.bounds.tolist(),
 'recess_field_m':[.82,.275],'recess_depth_m':.018,'maximum_relief_depth_m':float(s.z.max()),
 'central_flower_petals':8,'layers':s.layers,
 'angular_evidence':angular_evidence('commons-columns-2.jpg',[1019,498],29,[.65,.80],range(3,19)),
 'confidence':'Lobed silhouette, eight central petals and shallow recessed setting visible. Small contour, relative depth and repeated-panel differences are interpreted.',
 'metric_limits':'0.82 x 0.275 m recess is a photographic estimate, approximately +/- 0.12 x 0.05 m; whole-building vertical calibration remains unresolved'}
(OUT/'frieze-foliage-traces.json').write_text(json.dumps(frieze,indent=2)+'\n')

# Millimetre drafting coordinates for the smaller round rosettes. The close
# SW exterior photograph resolves twelve broad flared petals, rather than
# the pointed leaves / fourteen divisions used by the previous end proxy.
s=Surface((-90,-90,90,90),.18,.18,columns=340,origin_y=-.09)
s.ellipse(0,0,81,81,.006,base=.001)
for i in range(12):
    a=-math.pi/2+i*math.tau/12
    outline=[(r*math.cos(a+t),r*math.sin(a+t)) for r,t in
             [(29,-.13),(47,-.22),(77,-.25),(84,-.16),(85,0),(84,.16),
              (77,.25),(47,.22),(29,.13)]]
    s.region('Flared rosette petal',outline,.019,edge=3.8,base=.004)
    hollow=[(r*math.cos(a+t),r*math.sin(a+t)) for r,t in
            [(36,-.07),(51,-.14),(74,-.17),(78,-.10),(79,0),(78,.10),
             (74,.17),(51,.14),(36,.07)]]
    s.cut_region('Cupped rosette petal',hollow,.013,edge=4)
s.annulus(0,0,27.5,27.5,3.0,.0205)
s.ellipse(0,0,20.5,20.5,.018,base=.012)
s.annulus(0,0,21.5,21.5,1.2,.019)
s.save(OUT/'architectural-rosette.npz')
rosette={'source_images':['iwm-mont_8a','iwm-mont_9a','commons-columns-2'],
 'source_page':'https://memorials.iwm.org.uk/memorial/1228',
 'coordinate_frame':'Authored millimetre drafting frame; petal profile inferred from IWM mont_8a',
 'petals':12,'model_diameter_m':.170,'maximum_relief_depth_m':float(s.z.max()),
 'post_decimation_radius_limit_m':.087,
 'layers':s.layers,'angular_evidence':[
 angular_evidence('iwm-mont_8a.jpg',[105,48],40,[.70,.85],range(8,23)),
 angular_evidence('iwm-mont_8a.jpg',[813,39],40,[.70,.85],range(8,23))],
 'confidence':'Twelve divisions corroborated on both SW SE rosettes. Repeated design at the windows and other ends is a photographic interpretation; individual weathering and exact depth unresolved.',
 'metric_limits':'Diameter approximately +/- 20 mm; depth approximately +/- 10 mm'}
(OUT/'architectural-rosette-traces.json').write_text(json.dumps(rosette,indent=2)+'\n')
print('FLORA_SURFACES_WRITTEN',frieze['maximum_relief_depth_m'],rosette['maximum_relief_depth_m'])
