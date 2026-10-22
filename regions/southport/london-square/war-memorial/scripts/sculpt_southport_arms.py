"""Obelisk arms traced from the unchanged IWM mont_3a photograph.

Pixel coordinates preserve the evidence. Heraldic identification is supported
by Southport RFC's history of its borough-derived crest, but the geometry
follows the monument photograph. Relief depth and worn fine forms are estimates.
The motto is recessed into the numeric ribbon surface, not floating lettering.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import ImageFont
from sculpt_surface import Surface
from pedestal_joints import cut_numeric_surface,save_layout

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/relief-data'
s=Surface((177,275,692,759),1.30,1.30,columns=820,origin_y=-.65)
def region(name,p,z=.030,edge=2,**kw):s.region(name,p,z,edge=edge,**kw)

# The circular mouldings belong to the obelisk body and are deliberately not
# duplicated in this relief. The ribbon returns are visible inside that border.
left=[(244,411),(276,415),(264,447),(255,479),(251,515),(254,551),
      (265,586),(281,617),(292,633),(263,648),(248,628),(231,590),
      (222,554),(219,518),(223,479),(230,445)]
right=[(586,413),(618,410),(633,449),(643,488),(647,527),(641,565),
       (630,599),(612,633),(581,624),(598,593),(608,556),(612,520),
       (607,481),(598,446)]
region('Left motto ribbon',left,.031,2.3)
region('Right motto ribbon',right,.031,2.3)

# Folded returns follow the photograph, with separate broad top/bottom folds.
for p in [
 [(254,405),(271,380),(284,389),(274,415)],
 [(268,381),(286,360),(304,378),(285,397)],
 [(290,361),(309,349),(323,370),(307,381)],
 [(313,350),(333,338),(344,363),(325,371)],
 [(337,337),(358,328),(368,350),(348,362)],
 [(362,331),(378,329),(376,349),(365,352)],
 [(491,327),(515,334),(506,357),(487,350)],
 [(519,337),(538,346),(524,369),(510,357)],
 [(540,350),(556,359),(541,381),(525,372)],
 [(558,363),(576,379),(561,399),(544,385)],
 [(579,382),(593,406),(574,419),(562,403)],
 [(269,646),(283,631),(310,650),(295,669)],
 [(293,670),(310,650),(330,662),(314,684)],
 [(315,684),(332,664),(348,673),(339,694)],
 [(517,679),(532,660),(546,672),(535,693)],
 [(536,658),(551,645),(568,658),(550,678)],
 [(554,640),(573,629),(590,644),(575,660)]
]:region('Folded ribbon return',p,.027,1.8,smooth=False)
for line in [[(271,387),(278,401)],[(299,365),(311,378)],[(323,344),(334,366)],
 [(349,334),(357,355)],[(504,334),(498,351)],[(532,349),(520,365)],
 [(566,374),(552,390)],[(286,645),(304,659)],[(319,669),(335,679)],
 [(540,665),(551,674)],[(561,641),(570,645),(580,641)]]:
 s.stroke(line,1.0,-.0025,smooth=False)

# Shield and its narrow raised edge. The fess has three deep peaks; it is a
# dancettée horizontal band, not the chevron used in the earlier draft.
shield=[(315,469),(351,466),(397,466),(440,466),(483,466),(526,468),
        (555,474),(554,519),(549,558),(538,599),(519,638),(492,674),
        (464,705),(435,728),(402,708),(372,680),(347,646),(329,606),
        (318,560),(315,514)]
region('Southport shield',shield,.028,3.2)
s.stroke(shield+[shield[0]],1.6,.034,'max')
fess=[(325,575),(365,542),(399,570),(435,543),(469,570),(505,543),
      (546,576),(540,605),(506,578),(470,607),(435,580),(399,609),
      (364,579),(332,605)]
region('Fess dancettee',fess,.034,1.1,base=.028,smooth=False)
s.stroke([(327,575),(365,543),(399,571),(435,544),(469,572),(505,545),(543,576)],.8,-.0018,smooth=False)
s.stroke([(333,604),(364,580),(399,608),(435,581),(470,606),(506,579),(540,604)],.8,-.0018,smooth=False)

def cross_crosslet(cx,top,w=41,h=72,depth=.039):
    # Three short crossed arms and a pointed lower stem (fitchee).
    y=top+25;stem=3.7;arm=w/2;end=5.5
    p=[(cx-stem,top),(cx+stem,top),(cx+stem,top+8),(cx+11,top+8),
       (cx+11,top+15),(cx+stem,top+15),(cx+stem,y-stem),
       (cx+arm-end,y-stem),(cx+arm-end,y-11),(cx+arm+1,y-11),
       (cx+arm+1,y-stem),(cx+arm+8,y-stem),(cx+arm+8,y+stem),
       (cx+arm+1,y+stem),(cx+arm+1,y+11),(cx+arm-end,y+11),
       (cx+arm-end,y+stem),(cx+stem,y+stem),(cx+stem,top+h-16),
       (cx,top+h),(cx-stem,top+h-16),(cx-stem,y+stem),
       (cx-arm+end,y+stem),(cx-arm+end,y+11),(cx-arm-1,y+11),
       (cx-arm-1,y+stem),(cx-arm-8,y+stem),(cx-arm-8,y-stem),
       (cx-arm-1,y-stem),(cx-arm-1,y-11),(cx-arm+end,y-11),
       (cx-arm+end,y-stem),(cx-stem,y-stem),(cx-stem,top+15),
       (cx-11,top+15),(cx-11,top+8),(cx-stem,top+8)]
    region('Cross crosslet fitchee',p,depth,1,base=.028,smooth=False)
for cx,top in [(366,478),(435,476),(503,481)]:cross_crosslet(cx,top,w=37,h=68)

# One-masted galley/lymphad, with a furled sail, stays and projecting oars.
# The worn hull is asymmetrical in this photograph; keep its observed outline.
region('Galley hull',[(350,616),(368,615),(381,620),(417,622),(459,619),
       (482,609),(493,608),(490,623),(477,632),(453,637),(410,637),
       (381,633),(364,626),(350,626)],.039,1.7,base=.028)
s.stroke([(354,619),(380,624),(416,628),(454,626),(485,616)],1.1,-.002)
s.stroke([(365,624),(389,632),(417,634),(455,632),(477,626)],.8,-.002)
s.stroke([(435,586),(436,628)],1.6,.040,'max',smooth=False)
s.stroke([(412,603),(460,607)],1.7,.039,'max',smooth=False)
region('Galley furled sail',[(412,606),(425,603),(443,607),(461,607),
       (458,614),(441,612),(426,610),(414,612)],.040,1,base=.029)
region('Masthead pennant',[(435,585),(444,589),(441,594),(435,593)],.040,1,smooth=False)
for p in [[(433,590),(392,620)],[(438,593),(479,615)],[(461,609),(474,633)],
          [(465,610),(483,631)],[(426,628),(411,653)],[(438,629),(427,657)],
          [(450,627),(443,653)],[(461,625),(458,649)]]:
 s.stroke(p,.9,.040,'max',smooth=False)
for p in [[(354,645),(371,641),(387,646),(405,642),(422,646),(442,643),(460,646),(479,641)],
          [(367,661),(383,658),(401,663),(418,660),(435,665),(453,661),(467,663)]]:
 s.stroke(p,.75,.034,'max')

# Naval crown: the central band, outer ship sterns and two small sailing ships.
region('Naval crown band',[(340,443),(374,440),(411,440),(449,440),(491,442),
       (529,446),(530,463),(490,459),(445,457),(400,458),(363,461),(339,462)],.035,2)
for yy in [446,455]:s.stroke([(341,yy),(392,yy-3),(446,yy-3),(489,yy-1),(528,yy+2)],1.4,.041,'max')
for side in [-1,1]:
 tr=lambda p:p if side<0 else [(871-x,y) for x,y in p]
 region('Naval crown outer stern',tr([(317,415),(339,416),(355,412),
      (358,425),(349,431),(344,445),(342,452),(333,448),(331,435),
      (320,430)]),.038,1.8)
 for line in [[(322,420),(345,421)],[(325,425),(345,426)],[(334,420),(334,428)]]:
  s.stroke(tr(line),.8,-.003,smooth=False)
for cx,top in [(388,383),(484,384)]:
 region('Crown small ship sail',[(cx-14,top+18),(cx-2,top+16),(cx+13,top+21),
      (cx+12,top+49),(cx-10,top+49),(cx-16,top+34)],.040,1.5)
 s.stroke([(cx-17,top+19),(cx+16,top+20)],1.2,.045,'max',smooth=False)
 s.stroke([(cx,top),(cx+1,top+48)],1.1,.046,'max',smooth=False)
 region('Crown small ship hull',[(cx-19,top+45),(cx-9,top+49),(cx+11,top+49),
      (cx+22,top+42),(cx+17,top+54),(cx+6,top+57),(cx-12,top+55)],.043,1.5)
 for yy in [top+23,top+29,top+35]:
  s.stroke([(cx-11,yy),(cx+10,yy+2)],.75,-.002,smooth=False)
 for dx in [-10,-3,5,12]:s.stroke([(cx+dx,top+51),(cx+dx-3,top+61)],.85,.043,'max',smooth=False)
 s.stroke([(cx-15,top+14),(cx,top+4),(cx+13,top+17)],.8,.042,'max')
 region('Crown ship pennant',[(cx,top+2),(cx+9,top+4),(cx+3,top+8),(cx+1,top+7)],.043,1,smooth=False)

# Cross-crosslet crest and the serpent winding around its stem. The rounded
# lower coils were mistaken for a bell in the first coarse model.
crest=[(430,303),(436,300),(443,302),(447,306),(454,309),(457,315),(453,320),(444,318),
       (444,329),(452,329),(452,322),(459,322),(459,329),(467,329),
       (467,338),(459,338),(459,345),(452,345),(452,338),(444,338),
       (444,396),(437,414),(430,396),(430,338),(421,338),(421,344),
       (413,344),(413,338),(405,338),(405,330),(413,330),(413,323),
       (421,323),(421,330),(430,330),(430,318),(421,318),(421,310),(430,310)]
region('Crest cross crosslet',crest,.044,1.5,smooth=True)
serpent=[(428,343),(447,347),(454,352),(451,359),(425,359),
         (416,363),(416,368),(424,373),(448,373),(454,378),
         (453,383),(445,388),(427,389),(419,396),(418,409),
         (423,421),(435,427),(446,423),(451,414),(447,406),
         (437,402),(428,407),(428,416),(437,419),(442,414)]
s.stroke(serpent,3.0,.052,'max')
region('Serpent head against crest',[(423,340),(430,342),(434,348),
       (429,352),(420,350),(417,345)],.053,1.5)
s.stroke([(424,344),(424.1,344)],.8,-.004,smooth=False)
# Worn basal coils are a continuous broad form with shallow spiral incisions.
region('Lower serpent coil mass',[(418,396),(432,391),(449,396),(455,410),
       (452,426),(443,435),(428,435),(417,426),(414,410)],.044,2)
for line in [[(420,402),(434,398),(448,404)],[(418,411),(432,406),(451,412)],
             [(420,420),(435,416),(450,420)],[(425,429),(438,424),(446,428)]]:
 s.stroke(line,.9,-.003)

detail=s.detail_from_shading(ROOT/'references/images/iwm-mont_3a.jpg',light=(-.6,-.7),amount=.55,limit=.002)
s.z=.001+(s.z-.001)*.65

# Roman serif glyphs sampled directly as numeric cutting masks. The chosen
# font approximates the hand-cut letters; their observed positions are retained.
font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',128)
glyphs=[]
def incise(letter,cx,cy,angle,height=26,depth=.0035):
 mask=font.getmask(letter,mode='L');w,h=mask.size
 coverage=np.asarray(mask,dtype=float).reshape(h,w)/255
 scale=height/h;a=math.radians(angle)
 dx=s.x-cx;dy=s.y-cy
 u=(dx*math.cos(a)+dy*math.sin(a))/scale+(w-1)/2
 v=(-dx*math.sin(a)+dy*math.cos(a))/scale+(h-1)/2
 inside=(u>=0)&(u<w-1)&(v>=0)&(v<h-1)
 i=np.clip(u.astype(int),0,w-2);j=np.clip(v.astype(int),0,h-2)
 fu=np.clip(u-i,0,1);fv=np.clip(v-j,0,1)
 cut=((1-fu)*(1-fv)*coverage[j,i]+fu*(1-fv)*coverage[j,i+1]+
       (1-fu)*fv*coverage[j+1,i]+fu*fv*coverage[j+1,i+1])*inside
 covered=cut>.5
 seated=float(np.mean(s.z[covered]>.018))
 if seated<=.99:
  bad=covered&(s.z<=.018)
  print('GLYPH_REQUIRES_PLACEMENT',letter,cx,cy,seated,
        'bad_xy_mean',float(s.x[bad].mean()),float(s.y[bad].mean()),flush=True)
 s.z-=depth*cut
 glyphs.append({'letter':letter,'centre_px':[cx,cy],'baseline_clockwise_deg':angle,
                'height_source_px':height,'engraving_depth_m':depth,'seated_on_ribbon_fraction':seated})
for word,angles,rx,ry in [('SALVS',[159,169.5,180,190.5,201],199.5,185),
                         ('POPVLI',[-23,-12,0,11,21.5,31],193,185)]:
 for index,(letter,a) in enumerate(zip(word,angles)):
  rad=math.radians(a)
  # Slightly asymmetric photographed ribbon; the circle is only a layout aid.
  dx={0:3.0,4:5.0,5:5.0}.get(index,0) if word=='POPVLI' else 0
  incise(letter,434+rx*math.cos(rad)+dx,517+ry*math.sin(rad),a+90)
assert min(g['seated_on_ribbon_fraction'] for g in glyphs)>.99,'Motto glyph extends beyond ribbon face'
joint_metadata=cut_numeric_surface(s,'SE')
save_layout()
s.save(OUT/'southport-arms.npz')
meta={'name':'Southport borough arms on SE obelisk face','source_image':'references/images/iwm-mont_3a.jpg',
 'source_page':'https://memorials.iwm.org.uk/memorial/1228','credit':'David Long',
 'identification_reference':'https://www.southportrfc.com/news/our-new-club-heritage-crest-2672058.html',
 'source_pixel_bounds':s.bounds.tolist(),'width_m':s.width,'height_m':s.height,'origin_y_m':s.origin_y,
 'layers':s.layers,'fine_detail':detail,'depth_multiplier_before_lettering':.65,'inscription':'SALVS POPVLI','glyphs':glyphs,
 'masonry_joints':joint_metadata,
 'heraldic_components':['cross-crosslet entwined by serpent','naval crown','three cross-crosslets fitchee',
                         'fess dancettee','single-masted galley/lymphad'],
 'uncertainty':'Single photographic trace; worn ship/serpent forms and all depths are estimates. Font is an approximation. Outer obelisk rings are modelled separately.'}
(OUT/'southport-arms-traces.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SCULPTED_SOUTHPORT_ARMS',s.z.shape,'maximum depth',float(s.z.max()))
