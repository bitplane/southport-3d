"""Observed characteristic details, with restrained relief where photographs are soft."""
# Shop lettering is independent geometry with a narrow light edge behind dark letters.
label('Cafe letter edging','CAFFÈ NERO',W/2,3.47,.095,.37,4.55,gold)
label('Cafe letters','CAFFÈ NERO',W/2,3.47,.108,.35,4.47,black)
label('Cafe subtitle','THE ITALIAN COFFEE CO.',W/2,3.08,.155,.10,2.95,white)
label('Verandah name','CAFFÈ NERO',W/2,3.71,2.48,.12,1.32,black)
label('Door fanlight','ESPRESSO BAR',W/2,2.64,-.62,.10,.88,gold)
box('Door handle',(3.37,1.28,-.59),(.025,.43,.035),material=gold)
# Mortar is restricted to exposed brick; no repeated planes behind windows.
m=Mesh('Fine brick joints');mortar=mat('Dark recessed mortar',(.27,.20,.16))
voids=[rect(.28,-.5,W-.28,3.91),rect(.36,4.37,W-.36,7.75)]+[rect(x-.75,8.04,x+.75,11.26) for x in (1.26,2.925,4.59)]
for row in range(92):
 z=.10+row*.124
 for p in cuts(rect(.26,z,W-.26,z+.008),voids):m.add([(x,h,.007) for x,h in p],[tuple(range(len(p)))])
 for j in range(23):
  x=.26+j*.255+(row%2)*.127
  if x+.009>W-.26:continue
  for p in cuts(rect(x,z+.013,x+.008,z+.12),voids):m.add([(u,h,.008) for u,h in p],[tuple(range(len(p)))])
finish(m,'frontage',mortar,F)
# Enriched colonettes around three upper lights. Capitals read as carved masses,
# with small leaf reliefs; the source is not sharp enough for exact iconography.
for x in (1.26,2.925,4.59):
 for u in (x-.62,x+.62):
  m=Mesh('Stone colonettes');m.lathe((u,-.30),[(8.40,.095),(8.52,.11),(8.62,.065),(10.30,.065),(10.38,.105),(10.49,.11)],16);finish(m,'frontage',stone)
  for z in (8.65,9.06,9.47,9.88,10.29):
   m=Mesh('Fine colonette collars');m.lathe((u,-.30),[(z-.024,.068),(z,.087),(z+.025,.068)],12);finish(m,'frontage',stone)
  m=Mesh('Fine capital leaves')
  for dx in (-.07,.07):m.ellipsoid((u+dx,10.54,.40),(.045,.08,.04),segments=10,rings=6)
  finish(m,'frontage',stone,F)
 # Shallow pointed inner engraving and a central raised roundel.
 m=Mesh('Fine head carving');arc(m,x,10.79,.32,.23,.035,out=.267,depth=.025,steps=20);finish(m,'frontage',stone,F)
 m=Mesh('Fine stone roundel');m.ellipsoid((x,11.05,.275),(.065,.065,.025),segments=12,rings=6);finish(m,'frontage',stone,F)
# Deep, shaped brackets carry the balcony; matching silhouette appears in Street View.
for u in (.28,1.28,2.925,4.57,W-.28):
 profile=[(u-.14,11.64),(u+.14,11.64),(u+.14,10.92),(u+.07,10.74),(u-.06,10.82),(u-.14,11.05)]
 m=Mesh('Gallery carved bracket');m.outline(profile,.05,.71);finish(m,'gallery',timber,F)
 m=Mesh('Fine bracket scroll');arc(m,u,11.10,.07,.16,.028,out=.745,depth=.025,steps=22,start=-math.pi*.5,end=math.pi*.8);finish(m,'gallery',timber,F)
# Herringbone branches across the whole triangular infill, as seen in the gallery photograph.
for side in (-1,1):
 for z in (13.75,14.35,14.95,15.55):
  endx=W/2+side*(17.25-z)*W/7.9*.70
  line('Fine gable branching',(W/2+side*.10,z-.14,.86),(endx,z+.50,.86),.08,.06,'gallery',timber)
# Gallery handrail caps and modest carved fascia panels.
for z in (11.71,11.92,12.68):box('Fine gallery rail moulding',(W/2,z,.83),(W-.04,.045,.06),'gallery',timber)
for i in range(9):
 x=.34+i*(W-.68)/8;m=Mesh('Fine gallery pierced roundel');arc(m,x,11.82,.065,.045,.020,out=.858,depth=.018,steps=16,start=0,end=math.tau);finish(m,'gallery',timber,F)
# Raised X panels under the projecting white bay window.
for a,b in ((1.30,2.36),(2.41,3.47),(3.52,4.55)):
 for c,d in (((a,4.66,.63),(b,4.95,.63)),((a,4.95,.64),(b,4.66,.64))):line('Fine oriel apron cross',c,d,.045,.045)
# Tiled pentice laid horizontally, not vertical zebra stripes.
for z,out in ((7.52,.67),(7.57,.48),(7.62,.28)):
 line('Fine pentice tile edge',(.55,z,out),(W-.55,z,out),.018,.025,material=stone)
# Canopy rafters, perimeter bars and cast-iron cresting.
for i in range(13):
 x=i*W/12
 m=Mesh('Verandah roof rib');m.box((x,-1.235,4.10),(.032,2.47,.032));
 for k,v in enumerate(m.vertices):m.vertices[k]=(v[0],v[1],v[2]+(v[1]+1.235)*.47/2.47)
 finish(m,'verandah',white)
for i in range(27):
 x=.10+i*(W-.20)/26
 m=Mesh('Fine verandah crest');arc(m,x,3.93,.065,.085,.012,out=2.43,depth=.025,steps=12,start=0,end=math.pi);finish(m,'verandah',white,F)
for x in (.10,W-.10):
 for sign in (-1,1):
  if (x<1 and sign<0) or (x>W-1 and sign>0):continue
  m=Mesh('Verandah curved brace');arc(m,x+sign*.33,3.36,.33,.30,.026,out=2.4,depth=.045,steps=20,start=0 if sign<0 else math.pi/2,end=math.pi/2 if sign<0 else math.pi);finish(m,'verandah',white,F)
# Roof material joints follow each slope; retained ridge and right party stack.
for a,b,za,zb in ((-.09,W/2,13.3,17.25),(W/2,W+.09,17.25,13.3)):
 m=Mesh('Fine slate courses')
 for i in range(1,23):
  t=i/23;x=a+(b-a)*t;z=za+(zb-za)*t+.007
  m.add([(x,-.73,z),(x+.012,-.73,z),(x+.012,8.87,z),(x,8.87,z)],[(0,1,2,3)])
 finish(m,'shell',lead)
box('Roof ridge',(W/2,4.1,17.27),(.14,9.75,.10),'shell',lead,T)
# Stack is visible on the right roof edge in rotated 3D; pots are unresolved and omitted.
box('Right party chimney',(W-.34,4.7,14.95),(.56,.85,3.90),'shell',brick,T)
box('Chimney cap',(W-.34,4.7,16.92),(.65,.94,.15),'shell',stone,T)
