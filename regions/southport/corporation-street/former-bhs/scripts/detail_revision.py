"""Revision 01 reference-led architectural prototypes and low range."""
# Prototype principal arch: layered archivolts, substantial jambs, capitals,
# a central keystone mass and transom divisions. Subsequent bay follows review.
def arch_ribbon(u,spring,inner,outer,yfront,yback,material,name):
 m=Mesh('Architecture '+name);n=32
 for i in range(n):
  a=math.pi*i/n;b=math.pi*(i+1)/n
  p=[(u+inner*math.cos(a),spring+inner*math.sin(a)),(u+inner*math.cos(b),spring+inner*math.sin(b)),(u+outer*math.cos(b),spring+outer*math.sin(b)),(u+outer*math.cos(a),spring+outer*math.sin(a))]
  m.add([(x,yfront,z) for x,z in p],[(0,1,2,3)])
  m.add([(p[0][0],yfront,p[0][1]),(p[1][0],yfront,p[1][1]),(p[1][0],yback,p[1][1]),(p[0][0],yback,p[0][1])],[(0,1,2,3)])
 finish(m,'frontage',material)
def column_profile(x,y,z0,z1,part='frontage'):
 m=Mesh('Architecture profiled stone shaft');m.lathe((x,y),[(z0,.18),(z0+.09,.21),(z0+.17,.17),(z1-.20,.13),(z1-.12,.19),(z1,.21)],segments=16);finish(m,part,cream)
 box('Architecture shaft plinth',x-.23,y-.23,z0-.08,x+.23,y+.23,z0,'frontage',cream)
 box('Architecture shaft capital',x-.25,y-.25,z1,x+.25,y+.25,z1+.13,'frontage',cream)
for u in [19.1,22.8]:
 arch_ribbon(u,7.0,1.20,1.32,-.19,.02,cream,'inner archivolt prototype')
 arch_ribbon(u,7.0,1.36,1.53,-.14,.02,cream,'outer archivolt prototype')
 for side in [-1,1]:column_profile(u+side*1.47,-.16,4.23,7.00)
 box('Architecture arch keystone',u-.17,-.29,8.28,u+.17,-.08,8.62,'frontage',cream)
 # Projected upper arch divisions retain the visible fanlight and scroll rhythm.
 for x in [u-.60,u,u+.60]:box('Architecture fanlight upright',x-.028,-.045,7.02,x+.028,.03,7.82,'frontage',cream)
 box('Architecture arch transom',u-1.13,-.06,6.98,u+1.13,.03,7.06,'frontage',cream)
# Gallery capitals and bases: stepped circular mouldings and paired volutes
# capture the silhouette of the photographed stone without inventing figures.
def gallery_fitting(x,y,return_side=False):
 m=Mesh('Architecture moulded gallery capital and base')
 m.lathe((x,y),[(8.55,.21),(8.59,.24),(8.65,.19),(8.71,.17),(8.76,.16)],segments=16)
 m.lathe((x,y),[(11.92,.13),(11.97,.18),(12.01,.20),(12.04,.19),(12.09,.25),(12.13,.26),(12.16,.24)],segments=16)
 for side in [-1,1]:
  pts=[]
  for j in range(28):
   t=j/27;ang=math.pi*(.1+1.55*t);r=.085*(1-.65*t);offset=side*(.18+r*math.cos(ang));z=12.07+r*math.sin(ang)
   pts.append((x+.18,y+offset,z) if return_side else (x+offset,y-.18,z))
  m.tube(pts,.017,sides=6)
 finish(m,'frontage',cream)
for u in [17.3,19.0,20.7,22.4,24.1,25.8]:gallery_fitting(u,.02)
for v in [1.7,4.9,8.1,11.3,14.5,17.7,20.4]:gallery_fitting(W-.02,v,True)
box('Architecture gallery sill',17.1,-.11,8.52,26.8,.12,8.62,'frontage',cream)
# One bay prototype: curved glazing gains a horizontal transom and radial panes.
# The matching upper/lower curved masonry and outer glazing were built in massing.
def curved_transom(cx,cy,r,t0,t1,z):
 m=Mesh('Architecture curved bay transom');m.tube([(cx+r*math.cos(t0+(t1-t0)*i/24),cy+r*math.sin(t0+(t1-t0)*i/24),z)for i in range(25)],.045,sides=8);finish(m,'frontage',cream)
for z in [5.88,10.95]:curved_transom(15.5,0,1.46,math.pi,math.tau,z)
# Five timber gables: diagonal members, curved eaves cove and physical louvre
# heads. The cove is an actual concave surface, not a decal on the timber band.
for i in range(5):
 y0=F+(L-F)*i/5;y1=F+(L-F)*(i+1)/5;ym=(y0+y1)/2;span=y1-y0
 def beam(name,p,q,r=.045):
  m=Mesh('Architecture '+name);m.tube([p,q],r,sides=4);finish(m,'frontage',timber)
 # Intermediate posts and short alternating braces follow the dense
 # half-timber rhythm visible on the 2011 Corporation panorama.
 for t in [.1,.3,.5,.7,.9]:
  v=y0+span*t;top=Q+(S-Q)*(1-abs(2*t-1))
  if top>Q+.30:beam('gable additional upright',(W+.09,v,Q+.17),(W+.09,v,top-.10),.045)
 for j in range(8):
  a=y0+span*(j+.08)/8;b=y0+span*(j+.92)/8
  if j%2:a,b=b,a
  t=(b-y0)/span;top=Q+(S-Q)*(1-abs(2*t-1))
  zb=min(Q+.87,top-.10)
  if zb>Q+.2:beam('gable diagonal',(W+.09,a,Q+.16),(W+.09,b,zb),.045)
 # Cream curved eaves band, inset from the dark beam. Surface is broken into
 # strips along the cove arc; ribs project forward and remain visible in Walk.
 m=Mesh('Architecture curved cove');steps=12
 def cove(t):return (W+.035+.58*(1-math.cos(t*math.pi/2)),4.62+.78*math.sin(t*math.pi/2))
 for j in range(steps):
  x0,z0=cove(j/steps);x1,z1=cove((j+1)/steps)
  m.add([(x0,y0+.05,z0),(x0,y1-.05,z0),(x1,y1-.05,z1),(x1,y0+.05,z1)],[(0,1,2,3)])
 finish(m,'frontage',cream)
 for j in range(1,13):
  v=y0+span*j/13;m=Mesh('Architecture curved cove rib');m.tube([(cove(t/12)[0]+.035,v,cove(t/12)[1])for t in range(13)],.035,sides=6);finish(m,'frontage',timber)
 for v in [y0+.10,y1-.10]:box('Architecture cove bracket',W+.03,v-.12,4.45,W+.35,v+.12,4.85,'frontage',timber)
 # Arched louvre openings and their vertical borders sit on a single dark band;
 # shallow raised slats avoid the previous coplanar stripe conflict.
 for j in range(7):
  v=y0+span*(j+.5)/7;rx=span/17
  for side in [-1,1]:box('Architecture louvre jamb',W+.035,v+side*rx-.028,3.56,W+.10,v+side*rx+.028,4.45,'frontage',timber)
  m=Mesh('Architecture louvre arch');m.tube([(W+.08,v+rx*math.cos(math.pi*k/16),4.42+.25*math.sin(math.pi*k/16))for k in range(17)],.03,sides=6);finish(m,'frontage',timber)
  for k in range(5):
   z=4.05+k*.075;box('Fine louvre blade',W+.11,v-rx+.04,z,W+.15,v+rx-.04,z+.025,'frontage',dark)
 # Discrete crest above each ridge; true silhouette at both near levels.
 m=Mesh('Architecture gable finial');m.lathe((W,ym),[(S-.08,.08),(S+.08,.11),(S+.34,.06),(S+.47,.02)],segments=8);finish(m,'roof',timber)
# Recesses in brick base get window frames and a real service door panel.
for i in range(5):
 y0=F+(L-F)*i/5;y1=F+(L-F)*(i+1)/5
 if i==0:
  a,b=y0+.45,y0+1.7
  box('Architecture service door',W-.16,a,.05,W-.10,b,3.0,'frontage',timber)
  for v in [a+.1,b-.1]:box('Architecture door stile',W-.09,v-.045,.1,W-.02,v+.045,2.9,'frontage',dark)
  for z in [.28,1.2,2.5,2.85]:box('Architecture door rail',W-.09,a+.1,z,W-.02,b-.1,z+.06,'frontage',dark)
 else:
  a,b=(y0+y1)/2-1.0,(y0+y1)/2+1.0
  for v in [a,b,(a+b)/2]:box('Architecture brick window frame',W-.12,v-.045,.65,W-.025,v+.045,2.9,'frontage',timber)
  box('Architecture brick sill',W-.12,a-.08,.53,W+.10,b+.08,.65,'frontage',brick)
  box('Architecture brick lintel',W-.12,a-.08,2.9,W+.10,b+.08,3.06,'frontage',brick)
# Plain Chapel range prototype: paired stone surrounds and grouped sash glazing.
for u in [2.1,4.1,7.3,9.2]:
 for side in [-1,1]:
  column_profile(u+side*.56,-.12,4.7,7.42)
  column_profile(u+side*.56,-.12,8.7,10.40)
 arch_ribbon(u,10.4,.50,.61,-.15,.02,cream,'plain paired arch')
 box('Architecture plain sash divider',u-.035,-.05,4.75,u+.035,.04,7.35,'frontage',dark)
 for z in [5.6,6.55,9.65]:box('Architecture plain sash rail',u-.45,-.055,z,u+.45,.04,z+.045,'frontage',cream)
 box('Architecture plain sill',u-.64,-.20,4.58,u+.64,-.02,4.70,'frontage',cream)
# The two dark projecting oriels distinguish this range from the ornate bays.
for u in [10.8,13.0]:
 box('Architecture oriel base',u-.65,-.62,4.48,u+.65,-.02,4.64,'frontage',dark)
 face('Oriel glazing front',[(u-.55,-.60,4.64),(u+.55,-.60,4.64),(u+.55,-.60,7.05),(u-.55,-.60,7.05)],'frontage',glass)
 for x in [u-.55,u,u+.55]:box('Architecture oriel stile',x-.045,-.66,4.64,x+.045,-.51,7.05,'frontage',dark)
 for z in [5.5,6.38]:box('Architecture oriel transom',u-.55,-.66,z,u+.55,-.51,z+.06,'frontage',dark)
 box('Architecture oriel cap',u-.72,-.74,7.05,u+.72,-.01,7.23,'frontage',dark)
# Shopfront divisions and door leaves are explicit; interiors remain unmodelled.
for u,w in chapel_doors:
 # The door plane is behind the display glass, with physical side returns.
 box('Architecture shop door panel',u-w/2,.54,.12,u+w/2,.58,2.95,'frontage',glass)
 for x in [u-w/2,u+w/2]:
  box('Architecture shop entrance return',x-.04,0,.12,x+.04,.58,2.95,'frontage',cream)
 for x in [u-w/2,u+w/2,u]:box('Architecture door stile',x-.045,.45,.12,x+.045,.55,2.95,'frontage',dark)
 for z in [.12,2.3,2.9]:box('Architecture door rail',u-w/2,.45,z,u+w/2,.55,z+.06,'frontage',dark)
 box('Architecture entrance threshold',u-w/2,0,.04,u+w/2,.58,.12,'frontage',cream)
 m=Mesh('Architecture door handle');m.tube([(u+.16,.42,1.0),(u+.16,.42,1.55)],.022,sides=8);finish(m,'frontage',cream)
# Sign treatment records the visible 2025 tenants, rather than inventing stores.
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
serif=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf')
def inscription(body,u,z,width,height,material,out=.25,facefont=None):
 ob=text_object('Architecture sign '+body,body,(X+u,Y-out,Z+z),(0,-1,0),height,width,facefont or font,material,extrude=.003,collection=collections['frontage'],fit_bounds=True)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob.select_set(False)
 ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
 for vert in ob.data.vertices:vert.co=world((vert.co.x-X,vert.co.y-Y,vert.co.z-Z))
 ob.data.update()
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='metric')
box('Architecture Paperbox fascia',4.6,-.24,3.08,8.4,-.08,3.62,'frontage',red)
inscription('PAPERBOX',6.5,3.36,3.2,.34,cream,.27)
inscription('HUGO LOUNGE',24.8,3.35,3.8,.31,cream,.17)
for u in [5.8,12.0]:
 # Pale rim and offset blue italic letter faces approximate the retained BHS
 # signs in the reference photograph; exact proprietary typography remains estimated.
 inscription('BHS',u,11.76,1.28,.58,cream,.13,serif)
 inscription('BHS',u,11.76,1.20,.52,blue,.17,serif)
# Cresting: paired inward scrolls, bars and small finials retain the visible
# lattice above the canopy, rather than one row of open C-shaped loops.
m=Mesh('Architecture canopy paired cresting')
for i in range(47):
 x=.28+i*.59
 if x+.54>=W:break
 for side in [-1,1]:
  pts=[]
  for j in range(25):
   t=j/24;ang=(.25+1.65*t)*math.pi;rad=.12*(1-.58*t)
   pts.append((x+.295+side*(.17+rad*math.cos(ang)),-2.99,4.13+rad*math.sin(ang)))
  m.tube(pts,.017,sides=6)
 m.tube([(x+.295,-2.99,3.94),(x+.295,-2.99,4.37)],.018,sides=6)
 m.lathe((x+.295,-2.99),[(4.34,.035),(4.41,.065),(4.5,.015)],segments=6)
finish(m,'frontage',dark)
# Arcade-side framed panels, pilasters and shopfront. The lower band is blind
# moulded panelling in the loaded 2011 panorama; high windows remain above it.
for i in range(6):
 v=F+2.0+i*4.0
 for z in [4.10,6.65]:box('Architecture arcade panel band',-.11,v-1.55,z,.01,v+1.55,z+.08,'rear',cream)
 for y in [v-1.55,v+1.55]:box('Architecture arcade pilaster',-.13,y-.07,3.55,.02,y+.07,7.25,'rear',cream)
 for y in [v-.9,v+.9]:box('Architecture arcade shop divider',-.10,y-.04,.25,.04,y+.04,3.4,'rear',dark)
 box('Architecture arcade shop transom',-.10,v-1.55,2.65,.04,v+1.55,2.72,'rear',dark)
# Prototype archivolt ornament: small repeated egg-like blocks follow the outer
# curve, a simplified relief mass sits at its crown, and the fanlight has
# scrolls and lead divisions observed in qlocal-2.jpg. No inscription is invented.
for u in [19.1,22.8]:
 # Rounded moulding profiles project beyond the flat stone arch rings.
 m=Mesh('Architecture rounded archivolt mouldings')
 for radius,depth,thickness in [(1.22,-.22,.075),(1.35,-.27,.065),(1.51,-.19,.06)]:
  m.tube([(u+radius*math.cos(math.pi*j/24),depth,7+radius*math.sin(math.pi*j/24)) for j in range(25)],thickness,sides=10)
 finish(m,'frontage',cream)
 # Crown is a compact moulded central relief with swept side lobes;
 # no attempt is made to infer the unreadable carved figure.
 m=Mesh('Architecture arch crown relief')
 m.lathe((u,-.30),[(8.17,.08),(8.23,.16),(8.34,.19),(8.45,.15),(8.53,.09)],segments=12)
 for side in [-1,1]:
  for j in range(3):
   z=8.20+j*.065
   m.tube([(u+side*.10,-.31,z),(u+side*.22,-.32,z+.04),(u+side*.32,-.25,z+.12)],.035,sides=8)
 finish(m,'frontage',cream)
 for x in [u-.55,u+.55]:box('Architecture lower glazing mullion',x-.025,-.035,4.25,x+.025,.04,6.96,'frontage',cream)
 box('Architecture lower glazing rail',u-1.14,-.04,5.68,u+1.14,.04,5.73,'frontage',cream)
 m=Mesh('Fine prototype arch scrollwork')
 for side in [-1,1]:
  pts=[]
  for j in range(31):
   t=j/30;ang=math.pi*(.2+1.7*t);r=.17*(1-.65*t)
   pts.append((u+side*(.28+r*math.cos(ang)),-.085,7.02+r*math.sin(ang)))
  m.tube(pts,.018,sides=6)
 finish(m,'frontage',dark)
# Lower curved glazing has a fine rectilinear lead matrix with circular motifs;
# the upper sash glazing is clear in the reference and carries no lead pattern.
def curved_lead(cx,cy,r,t0,t1):
 m=Mesh('Fine lower curved bay lead')
 n=16
 for j in range(n+1):
  t=t0+(t1-t0)*j/n
  m.tube([(cx+r*math.cos(t),cy+r*math.sin(t),4.84),(cx+r*math.cos(t),cy+r*math.sin(t),7.14)],.009,sides=5)
 for z in [4.88,5.16,5.44,5.72,6.00,6.28,6.56,6.84,7.12]:
  m.tube([(cx+r*math.cos(t0+(t1-t0)*j/48),cy+r*math.sin(t0+(t1-t0)*j/48),z) for j in range(49)],.009,sides=5)
 for j in range(4):
  mid=t0+(t1-t0)*(j+.5)/4
  pts=[]
  for k in range(25):
   a=math.tau*k/24;t=mid+.055*math.cos(a)
   pts.append((cx+r*math.cos(t),cy+r*math.sin(t),6.31+.11*math.sin(a)))
  m.tube(pts,.009,sides=5)
 finish(m,'frontage',dark)
curved_lead(15.5,0,1.465,math.pi,math.tau)
# Dentil sequence across the ornate cornice and discrete panel rosettes.
m=Mesh('Fine ornate fascia dentils')
for j in range(59):
 x=17.05+j*.16
 if x<26.85:m.box((x,-.24,8.39),(.065,.06,.08))
finish(m,'frontage',cream)
for x in [18.7,22.0,25.3]:
 m=Mesh('Architecture fascia rosette mass');m.lathe((x,-.22),[(8.43,.11),(8.52,.16),(8.58,.07)],segments=8);finish(m,'frontage',cream)
# Corporation return uses the same distinct stone vocabulary as the front:
# deep archivolts, profiled shafts and divided arched fanlights.
for u in [3.4,6.8,10.2,13.6,17.0,20.0]:
 for ri,ro in [(1.05,1.16),(1.21,1.34)]:
  m=Mesh('Architecture return archivolt')
  for j in range(24):
   a=math.pi*j/24;b=math.pi*(j+1)/24
   m.add([(W+.14,u+ri*math.cos(a),7+ri*math.sin(a)),(W+.14,u+ri*math.cos(b),7+ri*math.sin(b)),(W+.14,u+ro*math.cos(b),7+ro*math.sin(b)),(W+.14,u+ro*math.cos(a),7+ro*math.sin(a))],[(0,1,2,3)])
  finish(m,'frontage',cream)
 for side in [-1,1]:
  m=Mesh('Architecture return arch shaft');m.lathe((W+.15,u+side*1.29),[(4.2,.19),(4.34,.21),(6.8,.13),(6.98,.20)],segments=12);finish(m,'frontage',cream)
  box('Architecture return arch capital',W-.08,u+side*1.29-.23,6.98,W+.38,u+side*1.29+.23,7.12,'frontage',cream)
 box('Architecture return keystone',W+.08,u-.17,8.14,W+.26,u+.17,8.49,'frontage',cream)
 for v in [u-.5,u,u+.5]:box('Architecture return fanlight stile',W-.04,v-.035,7.03,W+.04,v+.035,7.68,'frontage',cream)
 box('Architecture return arch transom',W-.04,u-1.0,6.95,W+.04,u+1.0,7.02,'frontage',cream)
 for v in [u-.55,u+.55]:box('Architecture return lower mullion',W-.035,v-.025,4.24,W+.035,v+.025,6.93,'frontage',cream)
 box('Architecture return sash rail',W-.035,u-1,5.65,W+.035,u+1,5.70,'frontage',cream)
# Corporation return ground-floor evidence, loaded May 2011 panorama: long
# display frontage, a recessed service pair and an adjacent roller shutter.
# Structural arrangement is retained; historic shop lettering is not inferred.
box('Architecture Corporation fascia',W+.03,.15,2.75,W+.14,F-.15,3.4,'frontage',cream)
for v in [1.4,3.6,5.8,8.0,10.2,12.4,14.6]:box('Architecture Corporation display frame',W-.09,v-.045,.10,W+.04,v+.045,2.75,'frontage',dark)
for z in [.12,2.68]:box('Architecture Corporation display rail',W-.09,.20,z,W+.04,F-6.0,z+.07,'frontage',dark)
# Recess is physically inset behind the facade line; returns frame the paired door.
for v in [F-5.85,F-3.05]:box('Architecture service recess return',W-.75,v-.10,.05,W+.04,v+.10,2.75,'frontage',cream)
box('Architecture return service door',W-.72,F-5.72,.05,W-.66,F-3.18,2.52,'frontage',timber)
for v in [F-5.70,F-4.45,F-3.20]:box('Architecture return door stile',W-.65,v-.04,.07,W-.59,v+.04,2.50,'frontage',dark)
box('Architecture return door lintel',W-.72,F-5.85,2.52,W+.04,F-3.05,2.76,'frontage',cream)
# Roller interface at the adjoining gabled service block.
box('Architecture roller shutter',W-.12,F-2.95,.06,W-.06,F-.25,2.72,'frontage',dark)
for j in range(18):
 z=.15+j*.14;box('Fine roller slat',W-.055,F-2.92,z,W-.025,F-.28,z+.028,'frontage',timber)
box('Architecture roller hood',W-.15,F-3.02,2.72,W+.10,F-.18,3.33,'frontage',cream)

# Recessed glazed entrance leaf on the arcade wing, with side frames and handle.
v=F+5.0
box('Architecture arcade entrance leaf',.08,v-.62,.10,.13,v+.62,3.05,'rear',glass)
for yy in [v-.62,v,v+.62]:box('Architecture arcade entrance stile',-.08,yy-.045,.10,.10,yy+.045,3.05,'rear',dark)
for z in [.14,2.4,2.98]:box('Architecture arcade entrance rail',-.08,v-.62,z,.10,v+.62,z+.06,'rear',dark)
m=Mesh('Architecture arcade door handle');m.tube([(-.11,v+.18,1.0),(-.11,v+.18,1.5)],.022,sides=8);finish(m,'rear',cream)
# Matching curved transoms and lead pattern at the physical street-corner bay.
for z in [5.88,10.95]:curved_transom(W-1.4,1.4,1.915,-math.pi/2,0,z)
curved_lead(W-1.4,1.4,1.915,-math.pi/2,0)
# Continuous stepped, curved cornices: moulding rolls and a dentil course wrap
# around both projecting bays and meet the straight fascia at their endpoints.
for cx,cy,r,t0,t1 in [(15.5,0,1.49,math.pi,math.tau),(W-1.4,1.4,1.94,-math.pi/2,0)]:
 m=Mesh('Architecture stepped curved cornices')
 for z,offset,thickness in [(8.08,.05,.065),(8.20,.11,.075),(8.38,.12,.08),(8.51,.05,.06),(11.99,.05,.06),(12.12,.10,.075),(12.25,.12,.075),(12.34,.05,.055)]:
  m.tube([(cx+(r+offset)*math.cos(t0+(t1-t0)*j/48),cy+(r+offset)*math.sin(t0+(t1-t0)*j/48),z) for j in range(49)],thickness,sides=8)
 finish(m,'frontage',cream)
 m=Mesh('Fine curved cornice dentils')
 for i in range(32):
  t=t0+(t1-t0)*(i+.5)/32;x=cx+(r+.14)*math.cos(t);y=cy+(r+.14)*math.sin(t)
  for z in [8.29,12.18]:m.box((x,y,z),(.055,.055,.08))
 finish(m,'frontage',cream)
# Return fascia mouldings carry the same stepped edge between the bays.
for z in [8.08,8.20,8.38,8.51,12.03,12.16,12.28]:
 m=Mesh('Architecture return cornice moulding');m.tube([(W+.29,0,z),(W+.29,F,z)],.055,sides=8);finish(m,'frontage',cream)
# The upper gallery's rear glazing has real sash frames, mullions and transoms.
for a,b in [(18.0,20.8),(22.3,25.1)]:
 for x in [a,(a+b)/2,b]:box('Architecture gallery sash upright',x-.04,1.18,9.2,x+.04,1.29,11.55,'frontage',dark)
 for z in [9.2,10.65,11.48]:box('Architecture gallery sash rail',a,1.18,z,b,1.29,z+.07,'frontage',dark)
for a,b in [(2.1,4.7),(5.5,8.1),(8.9,11.5),(12.3,14.9),(15.7,18.3)]:
 for v in [a,(a+b)/2,b]:box('Architecture return gallery sash upright',W-1.29,v-.04,9.2,W-1.18,v+.04,11.55,'frontage',dark)
 for z in [9.2,10.65,11.48]:box('Architecture return gallery sash rail',W-1.29,a,z,W-1.18,b,z+.07,'frontage',dark)

# Projecting brick piers, simple capitals and drainpipes are visible at bay
# boundaries in the 2011 Corporation view.
for i in range(6):
 v=F+(L-F)*i/5
 box('Architecture brick pier',W-.03,v-.16,0,W+.18,v+.16,3.45,'frontage',brick)
 box('Architecture pier cap',W-.05,v-.22,3.31,W+.24,v+.22,3.50,'frontage',timber)
for v in [F+.22,F+(L-F)*.4,L-.2]:
 m=Mesh('Architecture rainwater pipe');m.tube([(W+.22,v,.08),(W+.22,v,4.5),(W+.45,v,4.8)],.045,sides=8);finish(m,'frontage',timber)
