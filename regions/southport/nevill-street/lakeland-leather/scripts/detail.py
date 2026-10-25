"""Photo-derived facade ornament. Fine sculptural anatomy is a documented approximation."""
# This file executes inside build.py's dimensional/material scope.
def lathe_front(name,x,out,profile,mat=stone,part='facades',segments=32):
 m=Mesh(name);m.lathe((x,-out),profile,segments);m.vertices=[(a,c,-b) for a,b,c in m.vertices];o=finish(m,part,mat,F)
 for p in o.data.polygons:p.use_smooth=True
 return o

def swept(name,z,profile,mat=edge):
 m=Mesh(name);verts=[]
 for x,out in path:
  for dz,extra in profile:verts.append((x,z+dz,out+extra))
 n=len(profile);faces=[]
 for i in range(len(path)-1):
  for j in range(n-1):faces.append((i*n+j,(i+1)*n+j,(i+1)*n+j+1,i*n+j+1))
 m.add(verts,faces);return finish(m,mat=mat,frame=F)

def relief_leaf(m,x,z,out,length=.2,width=.08,angle=0):
 # Curved acanthus blade with a raised midrib, no planar triangle noise.
 co=math.cos(angle);si=math.sin(angle);v=[]
 for j in range(9):
  t=j/8;w=width*(.04+.70*math.sin(math.pi*t)**.7)
  for a in (-w,0,w):
   b=length*t;depth=.045*math.sin(math.pi*t)*(1-abs(a)/(w*1.4))
   v.append((x+a*co-b*si,z+a*si+b*co,out+depth))
 m.add(v,[(3*j+k,3*j+k+1,3*(j+1)+k+1,3*(j+1)+k) for j in range(8) for k in (0,1)])

def scroll(m,x,z,out,r=.15,turns=1.1,rotation=0,width=.028):
 p=[]
 for j in range(49):
  t=j/48;a=rotation+turns*math.tau*t;R=r*(1-.88*t);p.append((x+R*math.cos(a),z+R*math.sin(a)))
 v=[]
 for i,(a,b) in enumerate(p):
  before=p[max(0,i-1)];after=p[min(len(p)-1,i+1)];dx=after[0]-before[0];dz=after[1]-before[1];n=math.hypot(dx,dz)
  for depth in (out-.0225,out+.0225):
   for sign in (-1,1):v.append((a-sign*dz/n*width/2,b+sign*dx/n*width/2,depth))
 f=[]
 for i in range(len(p)-1):
  a=4*i;b=a+4;f.extend([(a+2,b+2,b+3,a+3),(a,a+1,b+1,b),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
 f.extend([(0,2,3,1),(4*(len(p)-1),4*(len(p)-1)+1,4*(len(p)-1)+3,4*(len(p)-1)+2)])
 m.add(v,f)

def ribbon(m,points,out,width,depth,closed=False):
 v=[];count=len(points)
 for i,(x,z) in enumerate(points):
  prev=points[(i-1)%count] if closed else points[max(0,i-1)]
  nex=points[(i+1)%count] if closed else points[min(count-1,i+1)]
  dx=nex[0]-prev[0];dz=nex[1]-prev[1];n=math.hypot(dx,dz)
  for o in (out-depth/2,out+depth/2):
   for sign in (-1,1):v.append((x-sign*dz/n*width/2,z+sign*dx/n*width/2,o))
 f=[]
 for i in range(count if closed else count-1):
  a=4*i;b=4*((i+1)%count);f.extend([(a+2,b+2,b+3,a+3),(a,a+1,b+1,b),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
 if not closed:f.extend([(0,2,3,1),(4*(count-1),4*(count-1)+1,4*(count-1)+3,4*(count-1)+2)])
 m.add(v,f)

# Masonry courses are shallow incised joints outside the actual openings.
# There is no duplicate sandstone skin covering the apertures.
joints=Mesh('Fine ashlar joints')
for z in [4.48,7.55,11.65,12.00,14.40,15.45,15.85]:
 for q in cuts(rect(.01,z-.006,6.99,z+.006),holes):joints.outline(q,.004,.010)
for row,(lo,hi) in enumerate([(3.95,4.46),(7.2,7.53),(11.68,11.98),(14.42,14.78),(15.48,15.83),(15.88,16.25)]):
 for x in [1.4+(row%2)*.6,2.8+(row%2)*.6,4.2+(row%2)*.6,5.6+(row%2)*.6]:
  joints.outline(rect(x-.005,lo,x+.005,hi),.004,.010)
finish(joints,mat=darkstone,frame=F)
# Full-width cornice, dentils and simple panelled parapet.
for name,z,prof in [('upper string',11.55,[(0,.02),(.06,.13),(.13,.19),(.19,.19),(.23,.03)]),('great cornice',14.80,[(0,.02),(.08,.12),(.16,.14),(.25,.25),(.32,.33),(.39,.33),(.46,.12),(.50,.22),(.56,.22),(.60,.02)]),('parapet cap',16.14,[(0,.02),(.05,.16),(.12,.16),(.16,.08)])]:
 m=Mesh('Trim '+name);moulding(m,0,7,z,prof);finish(m,mat=edge,frame=F)
for k in range(23):
 x=.19+k*.30;box('Fine cornice dentil',(x,15.01,.20),(.13,.14,.15),mat=darkstone)
for x in (.25,3.5,6.75):box('Trim parapet pier',(x,15.76,.055),(.40,.64,.11),mat=edge)
# Terminal pilasters have individual top/bottom blocks; shafts remain narrow.
for x in (.25,6.75):
 box('Trim upper pilaster',(x,13.2825,.08),(.40,2.445,.16),mat=edge)
 box('Trim upper capital',(x,14.63,.14),(.61,.25,.28),mat=edge)
 box('Trim upper base',(x,11.96,.12),(.56,.20,.24),mat=edge)
 box('Trim lower side pier',(x,5.91,.085),(.50,2.70,.17),mat=stone)
# Main arch is four nested uninterrupted rings; no internal radial caps.
for k,(r,t,o,d) in enumerate([(2.50,.08,.12,.15),(2.60,.12,.20,.23),(2.74,.10,.14,.17),(2.86,.07,.22,.25)]):
 m=Mesh('Trim great archivolt '+str(k));arc(m,3.5,8.12,r,r,t,out=o,depth=d,steps=64);finish(m,mat=edge if k%2 else darkstone,frame=F)
# Voussoir joints and egg ornament remain bounded by the moulding width.
m=Mesh('Fine great arch enrichment')
for j in range(33):
 a=math.pi*(j+.5)/33
 relief_leaf(m,3.5+2.70*math.cos(a),8.12+2.70*math.sin(a),.205,.11,.05,a-math.pi/2)
finish(m,mat=edge,frame=F)
# Paired top arches: sandstone reveals, double enriched surround, altered white glazing.
for i,u in enumerate((1.9,5.1)):
 for r,t,o in [(1.,.07,.10),(1.10,.12,.17),(1.24,.08,.10)]:
  m=Mesh('Trim upper arch '+str(i));arc(m,u,13,r,r,t,out=o,depth=o+.02,steps=40);finish(m,mat=edge,frame=F)
 for sign in (-1,1):
  box('Trim upper arch jamb',(u+sign*1.14,12.525,.10),(.28,.95,.20),mat=edge)
 box('Trim upper sill',(u,11.98,.15),(2.65,.14,.30),mat=edge)
 m=Mesh('Frames upper '+str(i));arc(m,u,13,.94,.94,.045,out=-.085,depth=.08,steps=32)
 for x in (u-.95,u+.95):m.box((x,12.515,-.095),(.045,.97,.08))
 m.box((u,12.075,-.085),(1.86,.065,.08))
 for x in (u-.32,u+.32):
  top=13+math.sqrt(.94**2-(x-u)**2);m.box((x,(12.10+top)/2,-.075),(.045,top-12.10,.09))
 finish(m,'frontage',white,F)
 m=Mesh('Fine upper arch eggs '+str(i))
 for j in range(21):
  a=math.pi*(j+.5)/21;relief_leaf(m,u+1.17*math.cos(a),13+1.17*math.sin(a),.185,.09,.06,a-math.pi/2)
 finish(m,mat=darkstone,frame=F)
 # Acanthus keystone at the crown.
 m=Mesh('Carving upper keystone '+str(i));m.outline([(u-.13,13.91),(u+.13,13.91),(u+.19,14.34),(u-.19,14.34)],.08,.24)
 for dx in (-.10,0,.10):relief_leaf(m,u+dx,14.0,.25,.26,.08,-dx)
 finish(m,mat=edge,frame=F)
# Large arch glazing: measured five major vertical divisions and small square panes.
m=Mesh('Frames great window');arc(m,3.5,8.12,2.44,2.44,.045,out=-.075,depth=.07,steps=64)
for x in [1.02,2.02,3.02,4.02,5.02,5.98]:
 top=8.12+math.sqrt(max(0,2.44**2-(x-3.5)**2));m.box((x,(7.97+top)/2,-.085),(.045,top-7.97,.08))
for z in [8.16,9.20]:
 half=math.sqrt(max(0,2.44**2-(z-8.12)**2));m.box((3.5,z,-.065),(2*half,.043,.085))
finish(m,'frontage',white,F)
m=Mesh('Fine great leadwork')
for x in [1.16+i*.22 for i in range(22)]:
 if abs(x-3.5)>=2.40:continue
 top=8.12+math.sqrt(2.40**2-(x-3.5)**2);m.box((x,(7.98+top)/2,-.115),(.012,top-7.98,.021))
for z in [8.15+i*.22 for i in range(11)]:
 half=math.sqrt(max(0,2.40**2-(z-8.12)**2));m.box((3.5,z,-.102),(2*half,.012,.022))
finish(m,'frontage',white,F)
# Oriel sill, curved entablature and genuinely pierced roundel parapet.
swept('Trim oriel sill',4.48,[(0,-.04),(.04,.03),(.10,.10),(.16,.10),(.20,.0)],edge)
swept('Trim oriel cornice',7.10,[(0,.0),(.06,.05),(.12,.11),(.18,.15),(.24,.15),(.30,.06),(.34,.08)],edge)
swept('Trim oriel parapet base',7.44,[(0,.04),(.06,.10),(.10,.10)],edge)
swept('Trim oriel parapet cap',7.88,[(0,.06),(.04,.13),(.10,.13),(.14,.06)],edge)
# Five grey granite shafts following the curve, with floral sandstone capitals.
for i,x in enumerate((.86,2.18,3.5,4.82,6.14)):
 out=out_at(x)+.025
 lathe_front('Oriel colonette '+str(i),x,out,[(4.65,.10),(4.71,.11),(4.78,.075),(6.86,.065),(6.92,.09)],granite,segments=32)
 lathe_front('Trim oriel capital '+str(i),x,out,[(6.90,.09),(6.96,.14),(7.04,.16),(7.10,.18)],edge,segments=24)
 m=Mesh('Fine oriel capital leaves')
 for dx,a in [(-.10,-.5),(0,0),(.10,.5)]:relief_leaf(m,x+dx,6.91,out+.10,.16,.09,a)
 finish(m,mat=edge,frame=F)
# Continuous narrow glazing bars follow the curved corner surface.
m=Mesh('Frames oriel')
for x in [1.15,2.18,3.5,4.82,5.85]:m.box((x,5.88,out_at(x)-.005),(.045,2.48,.08))
for z in (4.65,6.24,7.10):
 for (a,o),(b,p) in zip(path,path[1:]):beam(m,(a,z,o-.005),(b,z,p-.005),.035,.07)
finish(m,'frontage',white,F)
m=Mesh('Fine oriel leadwork')
for x in [.77+i*.205 for i in range(27)]:m.box((x,5.88,out_at(x)-.025),(.012,2.36,.025))
for z in [4.74+i*.205 for i in range(12)]:
 for (a,o),(b,p) in zip(path,path[1:]):beam(m,(a,z,o-.015),(b,z,p-.015),.012,.025)
finish(m,'frontage',white,F)
# Ring centres are distributed in frontage distance. Open centres remain actual air.
for i,x in enumerate([.88+i*.31 for i in range(18)]):
 out=out_at(x)+.10;m=Mesh('Trim pierced oriel roundels');arc(m,x,7.70,.115,.115,.038,out=out+.055,depth=.11,steps=20,start=0,end=math.tau);finish(m,mat=edge,frame=F)
# Paired flanking tourelles and sculpted supports.
for i,x in enumerate((.33,6.67)):
 lathe_front('Tourelle '+str(i),x,.13,[(7.05,.21),(7.24,.26),(7.40,.26),(7.48,.21),(10.82,.21),(10.90,.29),(11.03,.29),(11.09,.22),(11.44,.19),(11.55,.07),(11.62,.05)],edge,segments=32)
 m=Mesh('Carving tourelle support')
 m.outline([(x-.24,6.76),(x+.24,6.76),(x+.20,7.28),(x-.20,7.28)],.03,.20)
 for dx in (-.13,0,.13):relief_leaf(m,x+dx,6.79,.22,.36,.13,-dx*2)
 finish(m,mat=edge,frame=F)
# Carved spandrel panels: composition observed, small figure anatomy approximate.
for side in (-1,1):
 x=3.5+side*2.0;m=Mesh('Carving spandrel scroll '+str(side))
 for dx,dz,r in [(0,0,.23),(-side*.42,.22,.16),(side*.38,.12,.18),(side*.65,-.25,.15)]:scroll(m,x+dx,11.07+dz,.12,r,1.2,rotation=side*.7)
 for j in range(7):relief_leaf(m,x+side*(j-3)*.16,10.90+.14*math.sin(j),.15,.25,.10,side*(j-3)*.22)
 # Central cartouche shield and rolled upper shoulders.
 cx=3.5+side*1.50
 m.outline([(cx-.18,10.90),(cx+.18,10.90),(cx+.15,10.52),(cx,10.38),(cx-.15,10.52)],.06,.17)
 scroll(m,cx-.18,10.93,.19,.11,.8);scroll(m,cx+.18,10.93,.19,.11,.8,math.pi)
 finish(m,mat=edge,frame=F)
 # Small reclining relief figure: shoulders, head oval and bent legs.
 m=Mesh('Fine spandrel figure '+str(side));cx=3.5+side*2.35;cz=11.20
 head=[(cx+.075*math.cos(math.tau*j/20),cz+.12*math.sin(math.tau*j/20)) for j in range(20)];m.outline(head,.12,.23)
 m.outline([(cx-side*.10,cz-.10),(cx+side*.12,cz-.12),(cx+side*.30,cz-.32),(cx+side*.18,cz-.39),(cx-side*.04,cz-.24)],.10,.20)
 ribbon(m,[(cx,cz-.18),(cx-side*.24,cz-.28),(cx-side*.34,cz-.12)],.22,.07,.09)
 ribbon(m,[(cx+side*.22,cz-.33),(cx+side*.45,cz-.24),(cx+side*.58,cz-.41)],.19,.07,.09)
 finish(m,mat=edge,frame=F)
# Central arch keystone, acanthus fan and small scroll shoulders.
m=Mesh('Carving central acanthus keystone');m.outline([(3.35,10.53),(3.65,10.53),(3.75,11.17),(3.25,11.17)],.09,.26)
for j in range(7):relief_leaf(m,3.5+(j-3)*.06,10.62,.27,.43,.095,(j-3)*.20)
finish(m,mat=edge,frame=F)
# Shopfront has a central pair of doors, timber stiles and separate rectangular sign.
for x in (.46,2.46,4.54,6.54):box('Frames shop jamb',(x,1.5,-.10),(.08,2.92,.10),'frontage',green)
for x in (2.58,3.5,4.42):box('Frames shop door',(x,1.46,-.65),(.045,2.84,.08),'frontage',green)
for z in (.08,2.90):
 for a,b,o in [(.5,2.4,-.1),(2.55,4.45,-.65),(4.6,6.5,-.1)]:box('Frames shop rail',((a+b)/2,z,o),(b-a,.07,.09),'frontage',green)
for x in (3.38,3.62):box('Shop brass handle',(x,1.26,-.58),(.025,.32,.025),'frontage',edge)
box('Sign main board',(3.5,3.23,.085),(2.65,.49,.065),'frontage',brown)
text('LAKELAND','LAKELAND',3.5,3.23,.125,.28,2.20)
# Three unequal iron bays and authentic open brackets.
for a,b in ((0,1.9),(1.9,5.1),(5.1,7)):
 box('Verandah top rail',((a+b)/2,3.72,2.40),(b-a,.10,.16),'verandah',iron)
 box('Verandah lower rail',((a+b)/2,3.295,2.40),(b-a,.07,.13),'verandah',iron)
for x in (0,1.9,5.1,7):box('Verandah fascia stile',(x,3.50,2.47),(.06,.44,.04),'verandah',iron)
box('Verandah centre sign',(3.5,3.50,2.48),(3.08,.30,.025),'verandah',brown)
text('canopy website','lakelandleather.co.uk',3.5,3.50,2.50,.105,2.45,'verandah')
for a,b in ((.12,1.78),(5.22,6.88)):
 m=Mesh('Verandah fascia pinstripe');p=[(a+.15,3.39),(b-.15,3.39),(b-.04,3.50),(b-.15,3.61),(a+.15,3.61),(a+.04,3.50),(a+.15,3.39)]
 ribbon(m,p[:-1],2.48,.015,.02,closed=True)
 arc(m,(a+b)/2,3.5,.028,.04,.012,out=2.49,depth=.015,steps=16,start=0,end=math.tau);finish(m,'verandah',green,F)
# Roof bars run along the sloping roof, not in a horizontal plane.
for k in range(19):
 x=k*7/18;m=Mesh('Verandah roof bar')
 for lo,hi in ((.025,.805),(.855,1.635),(1.685,2.475)):
  beam(m,(x,4.335-.67*lo/2.5,lo),(x,4.335-.67*hi/2.5,hi),.034,.035)
 finish(m,'verandah',iron,F)
for out in (0,.83,1.66,2.5):
 z=4.32-.67*out/2.5;box('Verandah cross bar',(3.5,z+.016,max(.0175,out)),(7,.035,.035),'verandah',iron)
# Foliated brackets are actual scroll silhouettes, not solid triangular plates.
for x,sgn in ((.12,1),(1.9,-1),(1.9,1),(5.1,-1),(5.1,1),(6.88,-1)):
 m=Mesh('Verandah scroll bracket');scroll(m,x+sgn*.24,3.11,2.42,.20,1.10,rotation=-sgn*.5,width=.025)
 for j in range(3):relief_leaf(m,x+sgn*(.08+j*.13),3.04+j*.075,2.43,.14,.055,-sgn*.8)
 beam(m,(x+sgn*.07,2.84,2.41),(x+sgn*.49,3.28,2.41),.025,.05);finish(m,'verandah',iron,F)
# Regular cresting and the distinctive central scrolled upstand.
m=Mesh('Fine verandah cresting')
for i in range(48):
 x=.10+i*6.8/47;arc(m,x,3.83,.035,.055,.018,out=2.42,depth=.035,steps=12,start=0,end=math.tau)
 beam(m,(x,3.73,2.42),(x,3.87,2.42),.018,.03)
finish(m,'verandah',iron,F)
m=Mesh('Verandah central crest')
for side in (-1,1):
 scroll(m,3.5+side*.20,3.94,2.42,.22,1.2,rotation=side*.7,width=.035)
 scroll(m,3.5+side*.44,3.86,2.42,.11,.8,rotation=math.pi,width=.03)
 relief_leaf(m,3.5+side*.06,3.95,2.44,.30,.11,side*.3)
beam(m,(3.5,3.73,2.42),(3.5,4.25,2.42),.035,.05);finish(m,'verandah',iron,F)
for x in (.03,6.97):
 m=Mesh('Verandah terminal finial');beam(m,(x,3.73,2.42),(x,4.24,2.42),.035,.05)
 for a in (-.6,0,.6):relief_leaf(m,x,4.02,2.42,.20,.08,a)
 finish(m,'verandah',iron,F)
# Discreet roof edge flashing. Chimneys/rooflights not clearly attributable are deferred.
for x in (.06,6.94):
 m=Mesh('Roof side flashing');m.add([(x-.035,0,15.51),(x+.035,0,15.51),(x+.035,9.2,13.31),(x-.035,9.2,13.31)],[(0,1,2,3)]);finish(m,'roof',lead)
# Estimated slate-course spacing; preserves the observed slate surface without
# asserting unseen rooflights or chimney locations.
m=Mesh('Fine slate courses')
for j in range(1,37):
 y=j*.245
 if y>=9.2:break
 z=15.5+(13.3-15.5)*y/9.2+.006;m.box((3.5,y,z),(7,.006,.005))
for j in range(1,28):
 x=j*.25;end=15.5 if x<2.1 else 18.8;z=13.3-x*2.7/7+.006
 m.box((x,(9.2+end)/2,z),(.006,end-9.2,.005))
finish(m,'roof',lead)
