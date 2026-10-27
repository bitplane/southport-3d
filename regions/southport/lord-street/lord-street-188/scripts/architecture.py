"""Front elevation elements measured from the 188 Lord Street reference.

The working local x axis runs along Court Road and +y faces the road.
These helpers author cut wall panels and avoid a backing wall behind glazing.
"""
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from southport3d.geometry import Mesh
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def build_front(col, bounds, mats, entrance=True):
 x0,x1,y=bounds;w=x1-x0
 def obj(n,vertices,faces,mat):
  m=Mesh(n);m.add(vertices,faces);ob=m.finish([mats[mat]],col);uv=ob.data.uv_layers.new(name='Metric')
  for p in ob.data.polygons:
   for li in p.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/1.0,v.z/1.2)
  return ob
 def quad(n,p,mat):obj(n,p,[tuple(range(len(p)))],mat)
 def box(n,c,size,mat,omit_back=False):
  m=Mesh(n);m.box(c,size)
  # Back at y min is buried against the wall, omit it from attached pieces.
  if omit_back:m.faces.pop(1);m.indices.pop(1)
  return m.finish([mats[mat]],col)
 def panel(n,a,b,z0,z1,holes,mat):
  polygons=[rect(a,z0,b,z1)]
  for h in holes:polygons=[q for p in polygons for q in subtract(p,h)]
  for p in polygons:
   vv=[Vector((u,z))for u,z in p]
   for tri in tessellate_polygon([vv]):
    q=[vv[i] if isinstance(i,int) else i for i in tri]
    quad('Shell '+n,[(x0+v.x,y,v.y)for v in q],mat)
 def window(n,a,b,z0,z1,divisions=2):
  quad('Glazing '+n,[(x0+a,y-.16,z0),(x0+b,y-.16,z0),(x0+b,y-.16,z1),(x0+a,y-.16,z1)],'glass')
  obj('Reveal '+n,[(x0+a,y,z0),(x0+b,y,z0),(x0+b,y,z1),(x0+a,y,z1),(x0+a,y-.16,z0),(x0+b,y-.16,z0),(x0+b,y-.16,z1),(x0+a,y-.16,z1)],[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'stone')
  t=.065
  for u in (a+t/2,b-t/2):box('Joinery '+n,(x0+u,y-.08,(z0+z1)/2),(t,.12,z1-z0),'white')
  for i in range(1,divisions):box('Joinery '+n,(x0+a+(b-a)*i/divisions,y-.08,(z0+z1)/2),(t,.12,z1-z0-2*t),'white')
  for z in (z0+t/2,z1-t/2):box('Joinery '+n,(x0+(a+b)/2,y-.08,z),(b-a-2*t,.12,t),'white')
 def balcony(n,a,b,z):
  # Faceted convex frontage and slab follow the observed bowed balcony bands.
  import math
  N=8;us=[a+(b-a)*i/N for i in range(N+1)];ys=[y+1.0+.48*math.sin(math.pi*i/N) for i in range(N+1)]
  for i in range(N):
   u,v=us[i],us[i+1];p,q=ys[i],ys[i+1]
   obj('Balcony slab '+n,[(x0+u,y,z-.10),(x0+v,y,z-.10),(x0+v,q,z-.10),(x0+u,p,z-.10),(x0+u,y,z+.10),(x0+v,y,z+.10),(x0+v,q,z+.10),(x0+u,p,z+.10)],[(0,3,2,1),(4,5,6,7),(2,3,7,6)],'slab')
   quad('Balcony glass '+n,[(x0+u,p,z+.12),(x0+v,q,z+.12),(x0+v,q,z+1.15),(x0+u,p,z+1.15)],'balcony')
  m=Mesh('Balcony handrail '+n);m.tube([(x0+u,yy,z+1.19)for u,yy in zip(us,ys)],.035,sides=6);m.finish([mats['rail']],col)
  for u,yy in zip(us,ys):
   box('Balcony post '+n,(x0+u,yy,z+.64),(.055,.055,1.08),'rail')
   for zz in (z+.34,z+.96):box('Fine balcony clamp '+n,(x0+u,yy+.045,zz),(.105,.035,.055),'rail')
  for u,yy in ((a,ys[0]),(b,ys[-1])):
   quad('Balcony return '+n,[(x0+u,y+.04,z+.12),(x0+u,yy,z+.12),(x0+u,yy,z+1.15),(x0+u,y+.04,z+1.15)],'balcony')
   box('Balcony return rail '+n,(x0+u,(y+yy)/2,z+1.19),(.045,yy-y,.045),'rail')
 # The left (low x) outer stack, two stone-window and narrow brick axes,
 # central long balcony, and opposite outer stack follow the photograph.
 # Every opening stays inside a material panel to preserve exact skin ownership.
 bands=[(0,4.8,'stone'),(4.8,7.6,'stone'),(7.6,9.3,'brick'),(9.3,20.0,'brick'),(20,23.1,'stone'),(23.1,w,'brick')]
 for floor in range(6):
  base=.4+floor*2.9; top=base+2.9
  windows=[(1.0,3.8,base+.4,base+2.55),(5.0,7.2,base+1.0,base+2.25),(7.9,9.0,base+1.0,base+2.25),(10.0,11.1,base+.4,base+2.55),(13.5,15.0,base+1.0,base+2.25),(18.0,18.75,base+.4,base+2.55),(20.5,22.5,base+1.0,base+2.25),(24.0,min(w-.5,26.5),base+.4,base+2.55)]
  if floor==0 and entrance:windows=windows[:3]+[(11.0,14.9,base,base+2.8),(17.2,18.5,base+1.0,base+2.25)]+windows[-2:]
  active_bands=([(a,b,'brick') for a,b,_ in bands] if floor==5 else bands) if floor or not entrance else [(0,4.8,'brick'),(4.8,7.6,'brick'),(7.6,9.3,'brick'),(9.3,9.5,'brick'),(9.5,16.4,'stone'),(16.4,20,'brick'),(20,23.1,'brick'),(23.1,w,'brick')]
  for a,b,mat in active_bands:
   hs=[rect(c,d,e,f)for c,e,d,f in windows if c>=a and e<=b]
   # Ground uses a red outer bay while upper stone runs form the distinctive pale shafts.
   panel('front '+str(floor),a,b,base,top,hs,('brick' if floor==0 and a==0 else mat))
  for i,(a,b,z0,z1) in enumerate(windows):
   if floor==0 and entrance and i==3:continue
   window(str(floor)+' '+str(i),a,b,z0,z1,3 if floor>0 and i==4 else (2 if b-a>1 else 1))
  if floor==0 and entrance:
   # Glass blocks surround a pale stone door frame, with a blue glazed door.
   for a,b in ((11.0,11.65),(14.25,14.9)):
    quad('Entrance glass blocks',[(x0+a,y-.12,base),(x0+b,y-.12,base),(x0+b,y-.12,base+2.8),(x0+a,y-.12,base+2.8)],'glassblock')
    for z in [base+i*.2 for i in range(1,14)]:box('Fine glass block course',(x0+(a+b)/2,y-.09,z),(b-a-.08,.015,.012),'white')
    for u in (a+(b-a)/3,a+2*(b-a)/3):box('Fine glass block joint',(x0+u,y-.06,base+1.4),(.012,.012,2.8),'white')
   quad('Entrance glass blocks lintel',[(x0+11.65,y-.12,base+2.35),(x0+14.25,y-.12,base+2.35),(x0+14.25,y-.12,base+2.8),(x0+11.65,y-.12,base+2.8)],'glassblock')
   for z in (base+2.50,base+2.65):box('Fine glass block lintel course',(x0+12.95,y-.09,z),(2.52,.015,.012),'white')
   for u in [11.85+i*.20 for i in range(12)]:box('Fine glass block lintel joint',(x0+u,y-.06,base+2.575),(.012,.012,.45),'white')
   # The jamb surround owns the region around the door; no buried wall is kept.
   for a,b,z0,z1 in ((11.65,12.15,base,base+2.35),(13.75,14.25,base,base+2.35),(12.15,13.75,base+2.0,base+2.35)):
    quad('Entrance pale surround',[(x0+a,y-.08,z0),(x0+b,y-.08,z0),(x0+b,y-.08,z1),(x0+a,y-.08,z1)],'white')
   quad('Entrance door glass',[(x0+12.15,y-.14,base),(x0+13.75,y-.14,base),(x0+13.75,y-.14,base+2.0),(x0+12.15,y-.14,base+2.0)],'glass')
   for u in (12.19,12.45,13.45,13.71):box('Entrance blue door frame',(x0+u,y-.09,base+1),(.06,.08,2.0),'blue')
   for z in (base+.05,base+.70,base+1.95):
    for a,b in ((12.22,12.42),(12.48,13.42),(13.48,13.68)):box('Entrance blue door rail',(x0+(a+b)/2,y-.09,z),(b-a,.08,.06),'blue')
   # Circular entrance lamp sits proud of the upper pale panel.
   import math
   for rad,mat in ((.16,'rail'),(.11,'white')):
    points=[(x0+12.95,y-.035+(0.004 if rad<.12 else 0),base+2.18)] + [(x0+12.95+rad*math.cos(i*math.tau/20),y-.035+(0.004 if rad<.12 else 0),base+2.18+rad*math.sin(i*math.tau/20))for i in range(20)]
    obj('Entrance lamp',points,[(0,i+1,(i+1)%20+1)for i in range(20)],mat)
   box('Entrance canopy',(x0+12.95,y+.5,base+2.38),(4.0,1,.075),'balcony',True)
   for u in (11.2,14.7):
    m=Mesh('Entrance canopy support');m.tube([(x0+u,y+.9,base+2.42),(x0+u,y+.05,base+3.2)],.025,sides=6);m.finish([mats['rail']],col)
   box('Entrance threshold',(x0+12.95,y+.2,base+.025),(1.6,.4,.05),'stone',True)
   for u in (4.6,21.9):
    box('Entrance plinth vent',(x0+u,y+.014,.20),(.65,.028,.20),'rail',True)
    for j in range(4):box('Fine vent slat',(x0+u-.22+j*.14,y+.032,.20),(.03,.012,.16),'stone')
  balcony('outer '+str(floor),.3,4.5,base+.25)
  if floor:balcony('long '+str(floor),9.4,19.0,base+.25)
  if floor:balcony('opposite '+str(floor),23.4,w-.2,base+.25)
  if floor:
   # Stone string courses only across red material, leaving pale strips intact.
   for a,b in ((7.6,9.3),(9.3,20),(23.1,w)):
    box('Fine string course',(x0+(a+b)/2,y+.035,base),(b-a,.07,.10),'stone',True)

 panel('foundation',0,w,0,.4,[],'stone')
 panel('top closure',0,w,17.8,18,[],'brick')

def build_side(col,x,y0,y1,mats,outward=1):
 """Tall tower end: pale borders, red centre and two small window axes."""
 def finish(n,verts,faces,mat):
  m=Mesh(n);m.add(verts,faces);ob=m.finish([mats[mat]],col);uv=ob.data.uv_layers.new(name='Metric')
  for p in ob.data.polygons:
   for li in p.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.y/1.0,v.z/1.2)
 def box(n,c,sz,mat):
  m=Mesh(n);m.box(c,sz);m.finish([mats[mat]],col)
 length=y1-y0
 for f in range(6):
  z=.4+f*2.9
  for a,b,mat in ((0,.45,'stone'),(.45,length-.45,'brick'),(length-.45,length,'stone')):
   holes=[] if mat=='stone' else [rect(t,z+1,t+.85,z+2.0)for t in (5.1,length-5.95)]
   polys=[rect(a,z,b,z+2.9)]
   for h in holes:polys=[q for p in polys for q in subtract(p,h)]
   for p in polys:
    vv=[Vector((u,v))for u,v in p]
    for tri in tessellate_polygon([vv]):
     q=[vv[i] if isinstance(i,int) else i for i in tri];finish('Shell side',[(x,y0+t.x,t.y)for t in q],[(0,1,2)],mat)
   for h in holes:
    (a0,z0),(a1,_),(_,z1),_=h
    finish('Glazing side',[(x-outward*.12,y0+a0,z0),(x-outward*.12,y0+a1,z0),(x-outward*.12,y0+a1,z1),(x-outward*.12,y0+a0,z1)],[(0,1,2,3)],'glass')
    finish('Reveal side',[(x,y0+a0,z0),(x,y0+a1,z0),(x,y0+a1,z1),(x,y0+a0,z1),(x-outward*.025,y0+a0,z0),(x-outward*.025,y0+a1,z0),(x-outward*.025,y0+a1,z1),(x-outward*.025,y0+a0,z1)],[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'stone')
    for u in (a0+.035,a1-.035):box('Joinery side',(x-outward*.06,y0+u,(z0+z1)/2),(.07,.07,z1-z0),'white')
    for zz in (z0+.035,z1-.035):box('Joinery side',(x-outward*.06,y0+(a0+a1)/2,zz),(.07,a1-a0-.14,.07),'white')
 # Thin pale horizontal floor bands are visible across the red end face.
 for f in range(1,6):
  z=.4+f*2.9;me=Mesh('Fine side string');me.box((x+outward*.035,y0+length/2,z),(.07,length-.9,.10));me.faces.pop(4 if outward>0 else 2);me.indices.pop(4 if outward>0 else 2);me.finish([mats['stone']],col)
 # Unbroken plinth and closure.
 for lo,hi in ((0,.4),(17.8,18)):
  finish('Shell side closure',[(x,y0,lo),(x,y1,lo),(x,y1,hi),(x,y0,hi)],[(0,1,2,3)],'stone')

def build_garden(col,x,y0,y1,mats):
 """Garden elevation of the separate low block, measured against auction photograph."""
 def face(n,p,mat,xx=x):
  m=Mesh(n);v=[Vector((u,z))for u,z in p]
  for tri in tessellate_polygon([v]):
   q=[v[i]if isinstance(i,int) else i for i in tri];m.add([(xx,y0+t.x,t.y)for t in q],[(0,1,2)])
  ob=m.finish([mats[mat]],col);uv=ob.data.uv_layers.new(name='Metric')
  for f in ob.data.polygons:
   for li in f.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.y/1,v.z/1.2)
 def box(n,c,size,mat):
  m=Mesh(n);m.box(c,size)
  if n.startswith('Balcony slab'):m.faces.pop(4);m.indices.pop(4)
  m.finish([mats[mat]],col)
 def window(n,a,b,z0,z1,recess=0):
  face('Glazing garden '+n,rect(a,z0,b,z1),'glass',x-.13-recess)
  for u in (a+.035,(a+b)/2,b-.035):box('Joinery garden '+n,(x-.06-recess,y0+u,(z0+z1)/2),(.1,.07,z1-z0-.14),'white')
  for z in (z0+.035,z1-.035):box('Joinery garden '+n,(x-.06-recess,y0+(a+b)/2,z),(.1,b-a-.14,.07),'white')
 def balcony(a,b,z,recess=False):
  dep=1.0;xx=x-1.0 if recess else x;box('Balcony slab garden',(xx+dep/2,y0+(a+b)/2,z),(dep,b-a,.14),'stone')
  face('Balcony glass garden',rect(a,z+.1,b,z+1.12),'balcony',xx+dep)
  for u in (a,(a+b)/2,b):box('Balcony post garden',(xx+dep,y0+u,z+.6),(.04,.04,1.05),'rail')
  box('Balcony rail garden',(xx+dep,y0+(a+b)/2,z+1.16),(.05,b-a,.05),'rail')
 for floor in range(3):
  z=.3+floor*2.67;end=z+2.67
  # Side bays, central paired doors, small upper-right window and entrance.
  wins=[(1.0,3.4,z+.35,z+2.3),(8.0,10.0,z+.35,z+2.3),(14.0,16.0,z+.35,z+2.3),(21.0,22.5,z+.85,z+2.1),(25.0,28.0,z+.35,z+2.3)]
  if floor==1:wins.append((6.0,6.55,z+1.0,z+2.1))
  if floor==0:wins[3]=(21.0,22.0,z,z+2.3)
  for a,b in ((0,5.0),(5.0,19.5),(19.5,23.5),(23.5,y1-y0)):
   mat='stone' if floor==2 and a in (5.0,19.5) else ('stone' if floor==0 and a in (0,19.5,23.5) else 'brick')
   polys=[rect(a,z,b,end)];holes=[rect(c,d,e,f)for c,e,d,f in wins if a<=c and e<=b]
   for h in holes:polys=[q for p in polys for q in subtract(p,h)]
   inset=1.0 if (floor==2 and a==5.0) or (floor==0 and a in (0,23.5)) else (.6 if floor==0 and a==19.5 else 0)
   for p in polys:face('Shell garden',p,mat,x-inset)
  for i,(a,b,z0,z1) in enumerate(wins):window(str(floor)+' '+str(i),a,b,z0,z1,1.0 if (floor==2 and i in (1,2)) or (floor==0 and i in (0,4)) else (.6 if floor==0 and i==3 else 0))
  if floor==0:
   for a,b,depth in ((0,5.0,1.0),(19.5,23.5,.6),(23.5,y1-y0,1.0)):
    me=Mesh('Shell recessed garden floor');me.add([(x-depth,y0+a,z),(x,y0+a,z),(x,y0+b,z),(x-depth,y0+b,z)],[(0,1,2,3)]);me.finish([mats['stone']],col)
  if floor==0:
   for u,far in ((5.0,1.0),(19.5,.6),(23.5,.4)):
    near=.6 if u==23.5 else 0;far=1.0 if u==23.5 else far
    m=Mesh('Shell ground garden return');m.add([(x-near,y0+u,z),(x-far,y0+u,z),(x-far,y0+u,end),(x-near,y0+u,end)],[(0,1,2,3)]);m.finish([mats['stone']],col)
  if floor==1:
   for a,b in ((8.0,10.0),(14.0,16.0)):
    box('Balcony Juliet rail',(x+.12,y0+(a+b)/2,z+1.25),(.065,b-a,.065),'rail')
    for u in (a+.08,b-.08):box('Balcony Juliet post',(x+.12,y0+u,z+.84),(.065,.065,.75),'rail')
  if floor:balcony(.4,4.6,z+.2);balcony(24,30.7,z+.2)
  if floor==2:
   me=Mesh('Shell upper garden terrace floor');me.add([(x-1,y0+5,z),(x,y0+5,z),(x,y0+19.5,z),(x-1,y0+19.5,z)],[(0,1,2,3)]);me.finish([mats['stone']],col)
   balcony(5.5,19,z+.08,True)
   for u in (5.0,19.5):
    m=Mesh('Shell recessed garden return');m.add([(x,y0+u,z),(x-1,y0+u,z),(x-1,y0+u,end),(x,y0+u,end)],[(0,1,2,3)]);m.finish([mats['stone']],col)
 for a,b in ((0,.3),(8.31,8.4)):face('Shell garden closure',rect(0,a,y1-y0,b),'stone')

def build_service(col,x,y0,y1,mats):
 """Low block service face, from loaded opposing 3D view; openings are estimated."""
 def finish(n,vs,fs,mat):
  me=Mesh(n);me.add(vs,fs);ob=me.finish([mats[mat]],col);uv=ob.data.uv_layers.new(name='Metric')
  for p in ob.data.polygons:
   for li in p.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.y,v.z/1.2)
 def box(n,c,sz,mat):
  me=Mesh(n);me.box(c,sz);me.finish([mats[mat]],col)
 length=y1-y0;centres=(2.0,5.4,8.4,12.3,16.2,21.0,25.0,29.0)
 for f in range(3):
  z=.3+f*2.67
  for a,b in ((0,10.3),(10.3,20),(20,length)):
   mat='brick' if f==2 and a in (0,20) else 'stone'
   hs=[rect(u-.60,z+1.0,u+.60,z+1.8)for u in centres if a+.60<=u<=b-.60]
   polys=[rect(a,z,b,z+2.67)]
   for h in hs:polys=[q for p in polys for q in subtract(p,h)]
   for p in polys:
    vv=[Vector((u,v))for u,v in p]
    for tri in tessellate_polygon([vv]):
     q=[vv[i]if isinstance(i,int)else i for i in tri];finish('Shell service',[(x,y0+t.x,t.y)for t in q],[(0,1,2)],mat)
   for h in hs:
    (u0,z0),(u1,_),(_,z1),_=h
    finish('Glazing service',[(x+.12,y0+u0,z0),(x+.12,y0+u1,z0),(x+.12,y0+u1,z1),(x+.12,y0+u0,z1)],[(0,1,2,3)],'glass')
    for u in (u0+.035,u1-.035):box('Joinery service',(x+.06,y0+u,(z0+z1)/2),(.07,.07,z1-z0),'white')
    for zz in (z0+.035,z1-.035):box('Joinery service',(x+.06,y0+(u0+u1)/2,zz),(.07,u1-u0-.14,.07),'white')
 for a,b in ((0,.3),(8.31,8.4)):
  finish('Shell service closure',[(x,y0,a),(x,y1,a),(x,y1,b),(x,y0,b)],[(0,1,2,3)],'stone')
