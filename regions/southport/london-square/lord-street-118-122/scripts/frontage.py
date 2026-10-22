"""Shop-specific exterior joinery from the linked photographs; dimensions estimated."""
from mathutils import Matrix
from southport3d.geometry import Mesh

def build_frontages(D,box,finish,sign,frame,mats,material):
 dark=mats['dark'];glass=mats['glass'];metal=mats['metal'];pier=mats['pier']
 blue=mats['blue'];cream=mats['cream'];red=mats['red']
 burgundy=material('Mamma Mia lower painted door',(.12,.026,.022),rough=.55)
 bulb=material('Festoon pale glass',(.68,.60,.40),rough=.32)
 # Draw rectangular frames with rails between stiles, never overlapping fronts.
 def rectangle(mesh,u,z,w,h,t,out,depth,mat=0):
  for x in [u-w/2+t/2,u+w/2-t/2]:mesh.box((x,z,out),(t,h,depth),mat)
  for y in [z-h/2+t/2,z+h/2-t/2]:mesh.box((u,y,out),(w-2*t,t,depth),mat)
 for shop in D['shops']:
  a,b=shop['u0'],shop['u1'];w=b-a;u=(a+b)/2;name=shop['id']
  sam=name=='sam-thai';mamma=name=='mamma-mia';bugle=name=='bugle-tap'
  # Shared stone divisions are owned once, with narrow returns beside the glazing.
  if sam:box('Shop polished pier '+name,a-.075,2.6,.15,5.2,.32,-.12,pier,'shopfront')
  right_width=.20 if not bugle else .36
  box('Shop polished pier '+name,b+(.10 if not bugle else .025),2.6,right_width,5.2,.32,-.12,pier,'shopfront')
  for x in [a,b]:box('Shop stone return '+name,x,2.6,.045,5.2,.22,-.24,pier,'shopfront')
  box('Shop transom '+name,u,4.22,w,1.76,.035,-.18,glass,'shopfront')
  doorw=1.06;doorx=b-doorw/2-.08 if not bugle else a+w*.67
  leftedge=doorx-doorw/2;rightedge=doorx+doorw/2
  bottom=.10 if bugle else .72
  top=3.28
  panes=[(a,leftedge)]
  if bugle:panes.append((rightedge,b))
  for j,(l,r) in enumerate(panes):
   box('Shop display '+name+str(j),(l+r)/2,(bottom+top)/2,r-l,top-bottom,.035,-.17,glass,'shopfront')
   if not bugle:box('Shop stallriser '+name,(l+r)/2,.36,r-l,.70,.10,-.12,blue if sam else dark,'shopfront')
  # Rear-set door is modelled closed, preserving the photographed recessed threshold.
  doorout=-.45 if mamma else -.40
  box('Shop recessed door '+name,doorx,1.56,doorw,3.08,.07,doorout,glass,'shopfront')
  for x in [leftedge,rightedge]:box('Shop door reveal '+name,x,1.56,.065,3.08,.42,-.22,dark,'shopfront')
  box('Shop threshold '+name,doorx,.035,doorw,.07,.50,-.22,metal if sam else dark,'shopfront')
  m=Mesh('Shop door joinery '+name)
  rectangle(m,doorx,1.56,doorw,3.08,.06,doorout+.055,.055)
  m.box((doorx,2.62,doorout+.055),(doorw-.12,.06,.055))
  finish(m,'shopfront',[metal if sam else dark],frame)
  if mamma:
   box('Shop door lower panel',doorx,.56,doorw-.13,1.0,.04,doorout+.07,burgundy,'shopfront')
   m=Mesh('Fine Mamma door panel moulding');rectangle(m,doorx,.56,doorw-.27,.77,.035,doorout+.10,.025)
   finish(m,'shopfront',[dark],frame)
  # Photo-specific glazing, including Mamma Mia's single broad lower pane.
  lower=[a+.035,leftedge-.025,b-.035]
  if sam:lower.insert(1,a+(leftedge-a)/2)
  if bugle:lower=[a+.035,a+(leftedge-a)*.50,leftedge-.025,rightedge+.025,b-.035]
  m=Mesh('Shop glazing joinery '+name)
  for x in lower:m.box((x,(bottom+top)/2,-.07),(.055,top-bottom,.10))
  for pane_left,pane_right in panes:
   stiles=[x for x in lower if pane_left-.04<=x<=pane_right+.04]
   for l,r in zip(stiles,stiles[1:]):
    for z in [bottom,top]:m.box(((l+r)/2,z,-.07),(r-l-.055,.065,.10))
  # High lights have their own grid; they do not extend through the large pane.
  upper=[a+.035,a+w*.38,a+w*.73,b-.035]
  if sam:upper=[a+.035,a+(leftedge-a)/2,leftedge-.025,b-.035]
  for x in upper:m.box((x,4.21,-.07),(.055,1.76,.10))
  for l,r in zip(upper,upper[1:]):
   for z in [3.33,5.09]:m.box(((l+r)/2,z,-.07),(r-l-.055,.065,.10))
  finish(m,'shopfront',[metal if sam else dark],frame)
  # Tiny gasket beads sit behind the main frame, with no coincident front faces.
  m=Mesh('Fine glazing beads '+name)
  for l,r in panes:
   rectangle(m,(l+r)/2,(bottom+top)/2,r-l-.11,top-bottom-.10,.014,-.115,.018)
  finish(m,'shopfront',[dark],frame)
  if sam:
   box('Shop fascia stone',u,4.85,w,.66,.20,0,pier,'shopfront')
   sign(name+' fascia','Sam Thai',u,4.85,w*.70,.53,pier,blue)
   leftwidth=leftedge-a
   for k in range(2):
    px=a+(k+.5)*leftwidth/2
    sign(name+' window '+str(k),'Sam Thai',px,3.10,leftwidth/2-.05,.33,blue,cream,out=.025)
    sign(name+' lower '+str(k),'Sam Thai',px,.39,leftwidth/2-.08,.26,blue,cream,out=-.045)
   sign(name+' door band','01704250163',doorx,2.92,doorw-.07,.24,dark,cream,out=.04)
   # The reference shows one continuous fascia strip light, not two flood boxes.
   m=Mesh('Fine Sam strip light');m.box((u,5.08,.22),(w*.80,.05,.065));finish(m,'shopfront',[cream],frame)
  elif mamma:
   sign(name+' high','Mamma Mia',u,4.24,w*.87,.72,dark,cream,out=.035,script=True)
   sign(name+' small','PIZZERIA',u,4.73,w*.40,.20,dark,cream,out=.04)
   m=Mesh('Trim neon border');m.tube([(-w*.43,-.53,0),(w*.43,-.53,0),(w*.43,.53,0),(-w*.43,.53,0),(-w*.43,-.53,0)],.012,0,8)
   finish(m,'shopfront',[red],frame@Matrix.Translation((u,4.32,.065)))
   # Readable pale script on the outside of the large lower pane. The receiver
   # uses the same opaque glass material, so reduced levels can bake the lettering.
   display_centre=(a+leftedge)/2;display_width=leftedge-a
   sign(name+' lower glass','Mamma Mia',display_centre,2.29,display_width*.92,.53,glass,metal,out=-.145,script=True)
   sign(name+' lower pizzeria','PIZZERIA',display_centre,2.67,display_width*.39,.14,glass,metal,out=-.145)
   # Distinct row of short lights above the large ground-floor pane.
   m=Mesh('Shop Mamma lower transom');pw=leftedge-a
   for k in range(1,12):m.box((a+pw*k/12,3.04,-.065),(.035,.40,.08))
   m.box(((a+leftedge)/2,2.83,-.065),(pw,.055,.08));finish(m,'shopfront',[dark],frame)
  else:
   sign(name+' fascia','THE BUGLE TAP',u,3.43,w,.61,dark,cream,out=.35)
   sign(name+' subtitle','CASK AND CRAFT ALES',u,3.12,w*.53,.13,dark,cream,out=.35)
   # The fixed sign sits below high transoms, without a fictitious fabric awning.
   box('Shop Bugle fascia end cap',u,3.77,w,.06,.42,.15,dark,'shopfront')
   # Folding leaf hinges distinguish the black pub frontage at close range.
   m=Mesh('Fine Bugle hinges')
   for x in lower[1:-1]:
    for z in [.44,1.55,2.64]:m.box((x,z,.005),(.035,.12,.04))
   finish(m,'shopfront',[metal],frame)
   # Visible festoon cable and sparse unlit bulbs; no simulated interior.
   m=Mesh('Fine Bugle festoon');pts=[]
   for i in range(31):
    t=i/30;pts.append((a+w*t,3.83-.18*4*t*(1-t),.43))
   m.tube(pts,.008,0,6)
   for i in range(1,11):
    t=i/11;z=3.83-.18*4*t*(1-t)
    m.tube([(a+w*t,z,.43),(a+w*t,z-.11,.43)],.009,0,6)
    m.ellipsoid((a+w*t,z-.145,.43),(.026,.043,.026),1,8,4)
   finish(m,'shopfront',[dark,bulb],frame)
  if mamma:
   m=Mesh('Awning mamma-mia');depth=.85
   # Thin closed fabric shell: opposing duplicate planes can flicker under
   # double-sided rendering. Local Y is height; preserve the photographed pitch.
   top=[(a,3.62,0),(b,3.62,0),(b,3.28,depth),(a,3.28,depth)]
   m.add(top+[(x,y-.018,z) for x,y,z in top],
         [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
   m.box((u,3.20,depth),(w,.16,.035));finish(m,'shopfront',[dark],frame)
   sign(name+' awning','Mamma Mia',a+w*.24,3.20,w*.36,.14,dark,cream,out=depth+.025,script=True)
   sign(name+' awning phone','01704 540259',a+w*.70,3.20,w*.49,.14,dark,cream,out=depth+.025)
   m=Mesh('Fine awning arms')
   for x in [a+.18,b-.18]:
    m.tube([(x,3.54,-.01),(x,3.20,.40),(x,3.25,.79)],.019,0,8)
   finish(m,'shopfront',[metal],frame)
  m=Mesh('Fine door hardware '+name)
  m.tube([(doorx+.32,1.15,doorout+.13),(doorx+.32,1.65,doorout+.13)],.016,0,10)
  for z in [1.15,1.65]:m.tube([(doorx+.32,z,doorout+.04),(doorx+.32,z,doorout+.13)],.013,0,8)
  for z in [.40,1.55,2.70]:m.box((doorx-doorw/2+.07,z,doorout+.10),(.03,.08,.03))
  finish(m,'shopfront',[metal],frame)
