"""North-west obelisk laurel branches traced from IWM mont_1a.

Leaf endpoints and widths below are source pixels, rather than a repeated
radial rosette. Depth is authored. A documented piecewise vertical mapping
registers the two visible mortar beds to the existing pedestal geometry.
"""
from pathlib import Path
import math,json
import numpy as np
from sculpt_surface import Surface
from pedestal_joints import COURSES,CENTRE_Z,cut_numeric_surface

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'
s=Surface((-670,-670,670,670),1.34,1.34,columns=840,origin_y=-.67)
SCALE_X=1.294/273
SOURCE_Y=[293,374,495,556]
PANEL_Y=[.647,COURSES[1]-CENTRE_Z,COURSES[0]-CENTRE_Z,-.647]
def p(x,y):
    return ((x-459.5)*SCALE_X*1000,-float(np.interp(y,SOURCE_Y,PANEL_Y))*1000)
def points(seq):return [p(*q) for q in seq]

left_stem=[(465,544),(457,533),(438,531),(418,525),(398,514),(382,499),
 (368,481),(358,460),(352,439),(351,418),(354,397),(360,378),(371,359),
 (386,344),(404,331),(424,323),(443,320),(458,319)]
right_stem=[(451,544),(461,533),(480,531),(501,524),(521,512),(538,495),
 (551,474),(559,453),(563,432),(562,410),(557,389),(547,370),(533,353),
 (516,338),(495,327),(477,321),(461,319)]
for line in (left_stem,right_stem):s.stroke(points(line),3.2,.011,'max')

left_outer=[((458,532),(434,543)),((438,532),(408,537)),((418,526),(388,525)),
 ((397,516),(370,509)),((382,502),(356,489)),((369,485),(345,471)),
 ((359,465),(337,444)),((353,445),(334,420)),((351,424),(338,399)),
 ((353,404),(346,377)),((359,384),(358,355)),((369,365),(375,339)),
 ((382,350),(393,323)),((399,336),(415,311)),((419,325),(438,307)),
 ((439,321),(457,309))]
left_inner=[((449,533),(428,515)),((429,530),(407,509)),((409,522),(392,497)),
 ((390,507),(382,481)),((375,491),(373,466)),((363,472),(366,446)),
 ((355,451),(361,427)),((352,430),(361,406)),((353,409),(366,389)),
 ((357,391),(378,373)),((364,372),(391,358)),((376,356),(403,346)),
 ((390,342),(421,337)),((408,331),(440,332)),((428,324),(454,329))]
right_outer=[((461,532),(485,542)),((481,530),(510,534)),((501,524),(532,524)),
 ((520,512),(548,510)),((537,495),(562,489)),((549,476),(573,470)),
 ((558,456),(582,444)),((563,434),(585,420)),((563,413),(581,398)),
 ((559,391),(573,376)),((551,373),(561,355)),((539,356),(543,337)),
 ((523,341),(522,323)),((505,330),(499,312)),((484,323),(476,307))]
right_inner=[((471,532),(492,515)),((491,528),(514,508)),((512,519),(528,494)),
 ((529,506),(538,478)),((543,488),(548,462)),((553,469),(553,443)),
 ((560,448),(555,424)),((563,427),(553,403)),((561,407),(547,385)),
 ((554,387),(535,369)),((544,369),(522,354)),((532,353),(509,344)),
 ((516,339),(491,335)),((497,330),(473,331)),((479,324),(461,328))]

leaves=[]
for group,entries,depth in [('left outer',left_outer,.020),('right outer',right_outer,.020),
                            ('left inner',left_inner,.023),('right inner',right_inner,.023)]:
    for i,(a,b) in enumerate(entries):
        a=np.asarray(a,float);b=np.asarray(b,float);v=b-a
        n=np.array([-v[1],v[0]])/np.linalg.norm(v)
        width=(4.15 if 'outer' in group else 4.75)+(.15 if i%3 else .45)
        bend=(.7 if 'left' in group else -.7)
        c=a+v*.53+n*bend
        outline=[a,a+v*.22+n*(width*.72+bend*.35),c+n*width,
                 a+v*.80+n*(width*.61+bend*.4),b,
                 a+v*.72-n*(width*.67-bend*.5),c-n*width,
                 a+v*.22-n*(width*.66-bend*.35)]
        s.region('Laurel leaf '+group+' '+str(i+1),points(outline),depth,edge=width*SCALE_X*1000,base=.001)
        # Restrained central veins; their depth is not inferred from darkness.
        vein=[a+v*.12,c,b-v*.10]
        s.stroke(points(vein),1.5,-.002,smooth=True)
        leaves.append({'group':group,'base_px':a.tolist(),'tip_px':b.tolist(),
                       'half_width_px':width,'bend_px':bend,'maximum_depth_m':depth})

# Narrow moulding around the inscription field, visible inside the leaves.
fillet=[(459.5+94*math.cos(a),425.5+87.5*math.sin(a))
         for a in np.linspace(0,math.tau,181)]
s.stroke(points(fillet),4.8,.0105,'max',smooth=False)
# Small terminal leaves at the meeting of the branch tips.
for a,b in [((456,320),(460,326)),((464,320),(460,327))]:
    aa=np.asarray(a,float);bb=np.asarray(b,float);v=bb-aa;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
    outline=[aa,aa+v*.45+n*2.1,bb,aa+v*.45-n*2.1]
    s.region('Small terminal leaf',points(outline),.017,edge=4,base=.001)

joint_data=cut_numeric_surface(s,'NW')
s.save(OUT/'salute-wreath.npz')
meta={'source_image':'references/images/iwm-mont_1a.jpg',
 'source_page':'https://memorials.iwm.org.uk/memorial/1228','credit':'David Long',
 'name':'Two laurel branches around the NW salute inscription','leaf_count':len(leaves)+2,
 'leaves_source_pixels':leaves,'stems_source_pixels':[left_stem,right_stem],
 'inner_moulding_source_ellipse':[459.5,425.5,94,87.5],
 'source_to_panel':{'x_centre_px':459.5,'x_scale_m_per_px':SCALE_X,
                   'source_y_px':SOURCE_Y,'panel_up_m':PANEL_Y,
                   'method':'Piecewise linear vertical registration to two visible masonry beds and the outer-ring extrema; not camera calibration'},
 'numeric_frame':'Millimetre drafting coordinates; X right, Y down; numeric surface Z metres',
 'surface_width_height_m':[s.width,s.height],'maximum_depth_m':float(s.z.max()),
 'masonry_joints':joint_data,'layers':s.layers,
 'confidence':'Individual leaf endpoints and branch paths traced; worn tips, veins, undercuts and all depths interpreted. No blocks or tied ribbons are visible at the joins.',
 'limits':['IWM photograph resolves broad leaf shapes, not a measured carving depth',
           'Source perspective and current roundel scale limit absolute placement',
           'Approximate inner moulding ellipse; local erosion not reconstructed',
           'New whole-obelisk Commons images corroborate the composition but are less detailed here']}
(OUT/'salute-wreath-traces.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SALUTE_WREATH_SURFACE_WRITTEN',meta['leaf_count'],float(s.z.max()),flush=True)
