"""Westminster Chambers: metric architectural reconstruction."""
import math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh,text_object,smooth_path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
c=bpy.data.collections.new('architecture');s.collection.children.link(c)
def mat(name,col,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1)
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Red brick',(.45,.16,.11),'brick'); slate=mat('Slate',(.12,.14,.15),'slate'); cream=mat('Cream dressings',(.69,.63,.49)); glass=mat('Recessed glass',(.07,.12,.14)); iron=mat('Iron',(.045,.05,.052));white=mat('Painted veranda',(.75,.74,.68));wood=mat('Shopfront dark timber',(.16,.085,.045))
def finish(m,material):
 ob=m.finish([material],c);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update(); uv=ob.data.uv_layers.new(name='metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/(1.8 if material==brick else 2.4 if material==slate else 1),v[axes[1]]/(.6 if material==brick else 2.2 if material==slate else 1))
 return ob
def box(name,centre,size,material):
 m=Mesh(name);m.box(centre,size);return finish(m,material)
# Temporary massing, deliberately omits all joinery; used only to compare silhouette.
base=.10; x0,x1=-286.4,-266.24;y0,y1=-46.42,-25.45
# The rear-facing notch preserves the courtyard between the wings. The
# source OSM split is only an estimate, so the 1–3 m boundary uncertainty stays open.
front=box('Envelope front wing',((x0+x1)/2,(-32.7+y1)/2,base+5.75),(x1-x0,y1+32.7,11.5),brick)
wing=box('Envelope Eastbank wing',((-276.1+x1)/2,(y0-32.7)/2,base+5.75),(x1+276.1,-32.7-y0,11.5),brick)
def fuse(a,b):
 bpy.context.view_layer.objects.active=a
 mod=a.modifiers.new('Union adjoining wing','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=b
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(b,do_unlink=True)
fuse(front,wing)
rear=box('Envelope Hodge return',((-281.0-276.1)/2,(y0-38.94)/2,base+5.75),(-276.1+281.0,-38.94-y0,11.5),brick)
fuse(front,rear)
# Two hip volumes intersect at their L junction. Boolean union removes hidden
# overlapping roof faces so that each exposed valley has a single owner.
def hip(name,xa,xb,ya,yb,eave,ridge,axis):
 # The raised mansard has a steep lower tier, a set-back upper tier,
 # then a shallow roof cap; both attic rows have actual support behind them.
 m=Mesh(name);inset=min(1.65,(xb-xa)/4,(yb-ya)/4);br=eave+2.0;upper_h=br+1.65
 v=[(xa,ya,eave),(xb,ya,eave),(xb,yb,eave),(xa,yb,eave),
    (xa+inset,ya+inset,br),(xb-inset,ya+inset,br),(xb-inset,yb-inset,br),(xa+inset,yb-inset,br),
    (xa+inset,ya+inset,upper_h),(xb-inset,ya+inset,upper_h),(xb-inset,yb-inset,upper_h),(xa+inset,yb-inset,upper_h)]
 if axis=='x':
  d=min((yb-ya-2*inset)/2,(xb-xa-2*inset)/2)
  v += [(xa+inset+d,(ya+yb)/2,ridge),(xb-inset-d,(ya+yb)/2,ridge)]
  top=[(8,9,13,12),(9,10,13),(10,11,12,13),(11,8,12)]
 else:
  d=min((xb-xa-2*inset)/2,(yb-ya-2*inset)/2)
  v += [((xa+xb)/2,ya+inset+d,ridge),((xa+xb)/2,yb-inset-d,ridge)]
  top=[(8,9,12),(9,10,13,12),(10,11,13),(11,8,12,13)]
 v += [(xa,ya,eave-.15),(xb,ya,eave-.15),(xb,yb,eave-.15),(xa,yb,eave-.15)]
 faces=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),
        (4,5,9,8),(5,6,10,9),(6,7,11,10),(7,4,8,11)]+top+[(0,14,15,1),(1,15,16,2),(2,16,17,3),(3,17,14,0),(17,16,15,14)]
 m.add(v,faces);return finish(m,slate)
roof=hip('Roof front wing',x0,x1,-32.7,y1,base+11.5,base+16.2,'x')
roof2=hip('Roof Eastbank wing',-276.1,x1,y0,-29.0,base+11.5,base+16.5,'y')
fuse(roof,roof2)
roof3=hip('Roof Hodge return',-281.0,-271.1,y0,-38.94,base+11.5,base+16.2,'x')
fuse(roof,roof3)
# Open the set-back upper tier behind each gable for its small canted bay.
for axis,u in [('x',-281.65),('x',-271.85),('y',-34.15),('y',-41.35)]:
 cutter_mesh=Mesh('Attic bay cutter')
 centre=(u,y1-1.75,base+14.5) if axis=='x' else (x1-1.75,u,base+14.5)
 size=(1.20,1.30,1.15) if axis=='x' else (1.30,1.20,1.15)
 cutter_mesh.box(centre,size);cutter=cutter_mesh.finish([slate],c)
 bpy.context.view_layer.objects.active=roof;mod=roof.modifiers.new('Attic bay opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# The dormer housings own their roof openings. Cut each pocket through the
# sloping shell before the housings are installed, avoiding buried faces and
# slate projecting through the lower edges of the windows.
for axis, rows in [('x',((-280.8,-277.5,-270.9),(-280.0,-277.0,-269.5))),('y',((-28.5,-34.5,-38.0,-44.0),(-28.5,-36.0,-38.2,-44.0)))]:
 for row,positions in enumerate(rows):
  for u in positions:
   depth=.35 if row==0 else 1.65; z=12.5 if row==0 else 14.5
   centre=(u,y1-depth,base+z) if axis=='x' else (x1-depth,u,base+z)
   size=((1.22,.62,1.67) if axis=='x' else (.62,1.22,1.67)) if row==0 else ((1.22,.52,1.57) if axis=='x' else (.52,1.22,1.57))
   cutter_mesh=Mesh('Dormer pocket cutter');cutter_mesh.box(centre,size);cutter=cutter_mesh.finish([slate],c)
   bpy.context.view_layer.objects.active=roof
   mod=roof.modifiers.new('Dormer roof pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
   bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# Real apertures in both street elevations; the back-facing glass lies in
# the cutout and does not cover wall faces. Positions are approximate from
# the two dated street views, not a survey.
cuts=[]
def cut_box(centre,size):cuts.append((centre,size))
front_windows=[(-283.0,2.2),(-279.3,1.15),(-276.3,1.15),(-273.2,2.2),(-269.8,1.15)]
side_first=[(-29.2,1.15),(-32.8,2.2),(-36.4,1.15),(-40.0,2.2),(-43.5,2.2)]
side_second=[(-29.2,1.15),(-32.8,1.15),(-36.4,1.15),(-40.0,1.15),(-43.5,2.2)]
for z in (5.55,9.0):
 for x,w in front_windows:cut_box((x,y1-.12,base+z),(w,.85,2.55))
 for y,w in (side_first if z==5.55 else side_second):cut_box((x1-.12,y,base+z),(.85,w,2.55))
# Separate the corner turret from the main wall before constructing its faceted skin.
cut_box((x1-1.2,y1-1.2,base+7.55),(2.4,2.4,8.0))
# Shop openings and entry: clear entire frontage under the canopy.
cut_box(((-285.8-267.0)/2,y1-.45,base+1.8),(18.8,1.50,3.6))
cut_box((x1-.45,(-45.5-26.2)/2,base+1.8),(1.50,19.3,3.6))
for i,(centre,size) in enumerate(cuts):
 cutter_mesh=Mesh('Cutter %d'%i);cutter_mesh.box(centre,size);cutter=cutter_mesh.finish([brick],c)
 bpy.context.view_layer.objects.active=front
 mod=front.modifiers.new('Street aperture %d'%i,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# Recessed sashes and painted joinery. The two selected wider windows on
# each face are polygonal bay projections and retain a glazed front and sides.
def sash(name,u,z,w,axis,plane):
 # Four genuine panes bounded by independent edge and meeting rails.
 # Coordinates are local elevation coordinates before site shear.
 def point(v,h):return (v,plane,base+h) if axis=='x' else (plane,v,base+h)
 for u0,u1 in ((u-w/2+.08,u-.03),(u+.03,u+w/2-.08)):
  for h0,h1 in ((z-1.19,z+.68),(z+.76,z+1.19)):
   m=Mesh('Window '+name+' glass');m.add([point(u0,h0),point(u1,h0),point(u1,h1),point(u0,h1)],[(3,2,1,0) if axis=='x' else (0,1,2,3)]);finish(m,glass)
 for v in (u-w/2+.04,u,u+w/2-.04):
  if axis=='x':box('Trim '+name+' stile',(v,plane+.09,base+z),(.06,.15,2.38),cream)
  else:box('Trim '+name+' stile',(plane+.09,v,base+z),(.15,.06,2.38),cream)
 for h in (z-1.23,z+.72,z+1.23):
  for u0,u1 in ((u-w/2+.08,u-.03),(u+.03,u+w/2-.08)):
   if axis=='x':box('Trim '+name+' rail',((u0+u1)/2,plane+.09,base+h),(u1-u0,.15,.08),cream)
   else:box('Trim '+name+' rail',(plane+.09,(u0+u1)/2,base+h),(.15,u1-u0,.08),cream)
def window_front(x,z,w):sash('front',x,z,w,'x',y1-.22)
def window_side(y,z,w):sash('side',y,z,w,'y',x1-.22)
for z in (5.55,9.0):
 for x,w in front_windows:
  if w<2:window_front(x,z,w)
 for y,w in (side_first if z==5.55 else side_second):
  if w<2:window_side(y,z,w)
# Buff sills and shallow segmental heads complete the French-window reveals.
def sash_dressings(u,z,w,axis):
 if axis=='x':box('Trim front sash sill',(u,y1+.10,base+z-1.34),(w+.24,.20,.13),cream)
 else:box('Trim side sash sill',(x1+.10,u,base+z-1.34),(.20,w+.24,.13),cream)
 m=Mesh('Trim segmental sash head');n=8
 def p(v,h):return (v,y1+.025,base+h) if axis=='x' else (x1+.025,v,base+h)
 for i in range(n):
  t0=-1+2*i/n;t1=-1+2*(i+1)/n
  def h(t):return z+1.275+.12*(1-t*t)
  v=[p(u+t0*w/2,h(t0)),p(u+t1*w/2,h(t1)),p(u+t1*w/2,h(t1)+.09),p(u+t0*w/2,h(t0)+.09)]
  m.add(v,[(3,2,1,0) if axis=='x' else (0,1,2,3)])
 finish(m,cream)
for z in (5.55,9.0):
 for x,w in front_windows:
  if w<2:sash_dressings(x,z,w,'x')
 for y,w in (side_first if z==5.55 else side_second):
  if w<2:sash_dressings(y,z,w,'y')
# Terracotta pilaster panels flank the main Lord Street oriels at the upper
# storey. Their repeated low-relief diamond motif approximates photographed
# ornament without reproducing a photographic surface.
def pilaster_panel(x):
 box('Trim Lord pilaster',(x,y1+.07,base+8.85),(.32,.14,2.55),cream)
 box('Trim terracotta panel backing',(x,y1+.15,base+9.02),(.27,.035,1.12),brick)
 m=Mesh('Fine terracotta panel relief')
 for j in range(4):
  h=base+8.62+j*.26;outer=.115;inner=.070
  o=[(x,y1+.17,h+outer),(x+outer,y1+.17,h),(x,y1+.17,h-outer),(x-outer,y1+.17,h)]
  q=[(x,y1+.17,h+inner),(x+inner,y1+.17,h),(x,y1+.17,h-inner),(x-inner,y1+.17,h)]
  m.add(o+q,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 finish(m,cream)
for x in (-284.35,-281.65,-274.55,-271.85):pilaster_panel(x)
# Faceted bay envelopes project from the facade and replace the wide sash
# units; panes are quads with rods along their outlines, not coplanar wall skins.
def bar_between(name,a,b,r,material):
 d=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
 ob=box(name,(0,0,0),(r,r,d.length),material);ob.location=mid;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=d.to_track_quat('Z','Y');return ob
def bay(points,z,reverse=False,height=2.55):
 low=base+z-height/2;high=base+z+height/2
 panel_top=low+min(.40,height*.16);transom=high-min(.62,height*.24)
 for i,(a,b) in enumerate(zip(points,points[1:])):
  # The opaque painted base panels and two separate glazed lights own
  # disjoint surfaces; horizontal joinery covers their meeting edges.
  for name,h0,h1,material in [('Trim bay base panel',low,panel_top,cream),('Window polygonal bay glazing',panel_top,transom,glass),('Window polygonal bay glazing',transom,high,glass)]:
   m=Mesh(name);m.add([(a[0],a[1],h0),(b[0],b[1],h0),(b[0],b[1],h1),(a[0],a[1],h1)],[(3,2,1,0) if reverse else (0,1,2,3)]);finish(m,material)
  d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized()*.04
  for h in (low,panel_top,transom,high):
   bar_between('Trim bay horizontal',(a[0]+d.x,a[1]+d.y,h),(b[0]-d.x,b[1]-d.y,h),.075,cream)
  # Upper lights have a small central division as seen in the dated photo.
  mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
  bar_between('Trim bay upper mullion',(mid[0],mid[1],transom+.04),(mid[0],mid[1],high-.04),.045,cream)
  # Leaded upper lights are subdivided into small squares. Rails stop at
  # the mullion so the visible joinery does not have coincident end faces.
  for j in (1,2):
   h=transom+(high-transom)*j/3
   for p,q in ((a,mid),(mid,b)):
    vec=Vector((q[0]-p[0],q[1]-p[1],0)).normalized()*.025
    bar_between('Trim bay upper light rail',(p[0]+vec.x,p[1]+vec.y,h),(q[0]-vec.x,q[1]-vec.y,h),.035,cream)

 # Two projecting moulding courses finish the top of each oriel.
 for a,b in zip(points,points[1:]):
  d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized()*.10
  for h,width in ((high+.08,.14),(high+.23,.12)):
   bar_between('Trim bay crown moulding',(a[0]+d.x,a[1]+d.y,h),(b[0]-d.x,b[1]-d.y,h),width,cream)
 for x,y in points:bar_between('Trim bay stile',(x,y,low),(x,y,high),.08,cream)
 for height in (low,high):
  cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
  inset=[]
  for x,y in points:
   d=Vector((cx-x,cy-y));d.normalize();inset.append((x+d.x*.12,y+d.y*.12,height))
  m=Mesh('Trim bay cap');m.add(inset,[tuple(range(len(inset)))]);finish(m,cream)
for z in (5.55,9.0):
 for x in (-283.0,-273.2):bay([(x-1.1,y1),(x-.95,y1+.40),(x-.65,y1+.75),(x+.65,y1+.75),(x+.95,y1+.40),(x+1.1,y1)],z,True)
 for y in ((-32.8,-40.0,-43.5) if z==5.55 else (-43.5,)):bay([(x1,y-1.1),(x1+.40,y-.95),(x1+.75,y-.65),(x1+.75,y+.65),(x1+.40,y+.95),(x1,y+1.1)],z)
# The second attic tier has smaller five-sided bays set back behind gables.
for x in (-281.65,-271.85):bay([(x-.60,y1-1.65),(x-.52,y1-1.45),(x-.36,y1-1.27),(x+.36,y1-1.27),(x+.52,y1-1.45),(x+.60,y1-1.65)],14.5,True,1.1)
for y in (-34.15,-41.35):bay([(x1-1.65,y-.60),(x1-1.45,y-.52),(x1-1.27,y-.36),(x1-1.27,y+.36),(x1-1.45,y+.52),(x1-1.65,y+.60)],14.5,False,1.1)

# The street shopfronts are framed as separate window bays with a wooden
# stallriser. The two Lord Street openings are recessed with returns.
def front_display(a,b):
 m=Mesh('Shop Lord display glass');m.add([(a+.04,y1-.24,base+.4),(b-.04,y1-.24,base+.4),(b-.04,y1-.24,base+3.54),(a+.04,y1-.24,base+3.54)],[(3,2,1,0)]);finish(m,glass)
 box('Shop Lord stallriser',((a+b)/2,y1-.20,base+.20),(b-a,.12,.40),wood)
 if a not in (-283.625,-279.725):box('Shop Lord display stile',(a,y1-.16,base+1.97),(.075,.16,3.14),wood)
 box('Shop Lord display head',((a+b)/2,y1-.16,base+3.58),(b-a,.16,.08),wood)
 box('Shop Lord transom rail',((a+b)/2,y1-.16,base+2.88),(b-a-.08,.12,.055),wood)
 for i in range(max(1,int((b-a)/.13))):
  xx=a+.065+i*.13
  if xx<b-.04:box('Shop Lord stallriser bead',(xx,y1-.115,base+.20),(.035,.04,.34),wood)
for a,b in [(-285.8,-284.975),(-283.625,-282.15),(-282.15,-280.675),(-279.725,-277.2),(-277.2,-274.65),(-274.65,-272.1),(-272.1,-269.55),(-269.55,-267.0)]:front_display(a,b)
def side_display(a,b):
 m=Mesh('Shop Eastbank display glass');m.add([(x1-.24,a+.04,base+.4),(x1-.24,b-.04,base+.4),(x1-.24,b-.04,base+3.54),(x1-.24,a+.04,base+3.54)],[(0,1,2,3)]);finish(m,glass)
 box('Shop Eastbank stallriser',(x1-.20,(a+b)/2,base+.2),(.12,b-a,.4),wood)
 box('Shop Eastbank display stile',(x1-.16,a,base+1.97),(.16,.075,3.14),wood)
 box('Shop Eastbank display head',(x1-.16,(a+b)/2,base+3.58),(.16,b-a,.08),wood)
 box('Shop Eastbank transom rail',(x1-.16,(a+b)/2,base+2.88),(.12,b-a-.08,.055),wood)
 for i in range(max(1,int((b-a)/.13))):
  yy=a+.065+i*.13
  if yy<b-.04:box('Shop Eastbank stallriser bead',(x1-.115,yy,base+.20),(.04,.035,.34),wood)
for a,b in zip((-45.5,-42.3,-39.1,-35.9,-32.7,-29.5),(-42.3,-39.1,-35.9,-32.7,-29.5,-26.2)):side_display(a,b)
box('Shop Lord end stile',(-267.0,y1-.16,base+1.97),(.075,.16,3.14),wood)
box('Shop Eastbank end stile',(x1-.16,-26.2,base+1.97),(.16,.075,3.14),wood)
# Faceted corner turret, separated from the main shell. Window grids in its
# three exposed faces are actual openings through the skin.
turret=[(x1-2.4,y1),(x1-.8,y1),(x1,y1-.8),(x1,y1-2.4),(x1-2.4,y1-2.4)]
for i,(a,b) in enumerate(zip(turret,turret[1:]+turret[:1])):
 def pt(t,h):return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,base+h)
 mesh=Mesh('Envelope turret facet')
 if i<3:
  us=[0,.13,.87,1];zs=[3.55,4.35,6.80,7.72,10.15,11.95,13.4,14.65]
  for u0,u1 in zip(us,us[1:]):
   for z0,z1 in zip(zs,zs[1:]):
    if u0==.13 and z0 in (4.35,7.72,11.95):continue
    mesh.add([pt(u0,z0),pt(u1,z0),pt(u1,z1),pt(u0,z1)],[(3,2,1,0)])
  for low,hi in ((4.35,6.80),(7.72,10.15),(11.95,13.4)):
   win=Mesh('Window turret glazing');win.add([pt(.13,low),pt(.87,low),pt(.87,hi),pt(.13,hi)],[(3,2,1,0)]);finish(win,glass)
   for u in (.13,.5,.87):bar_between('Trim turret stile',pt(u,low+.04),pt(u,hi-.04),.06,cream)
   dt=.035/math.hypot(b[0]-a[0],b[1]-a[1])
   for h in (low,(low+hi)/2,hi):
    for left,right in ((.13,.5),(.5,.87)):
     bar_between('Trim turret rail',pt(left+dt,h),pt(right-dt,h),.06,cream)
 else:mesh.add([pt(0,3.55),pt(1,3.55),pt(1,14.65),pt(0,14.65)],[(3,2,1,0)])
 finish(mesh,brick)
 # Pale stone bands wrap each exposed turret face; offset from brick so
 # the band owns its outer surface rather than coinciding with the wall.
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);ox,oy=-dy/length*.025,dx/length*.025
 for h in (3.65,7.15,11.10,13.70,14.55):
  m=Mesh('Trim turret band');m.add([(a[0]+ox,a[1]+oy,base+h-.14),(b[0]+ox,b[1]+oy,base+h-.14),(b[0]+ox,b[1]+oy,base+h+.14),(a[0]+ox,a[1]+oy,base+h+.14)],[(3,2,1,0)]);finish(m,cream)
# Swept, faceted slate turret cap and the open iron crest visible above it.
roofmesh=Mesh('Roof turret crown');cx,cy=x1-1.2,y1-1.2
rings=[[(cx+(x-cx)*scale,cy+(y-cy)*scale,base+height) for x,y in turret] for scale,height in ((1,14.65),(.55,15.8),(.24,16.35),(.14,16.63))]
for lower,upper in zip(rings,rings[1:]):
 for i in range(len(turret)):
  j=(i+1)%len(turret);roofmesh.add([lower[i],lower[j],upper[j],upper[i]],[(0,1,2,3)])
apex=(cx,cy,base+16.82)
for i in range(len(turret)):
 j=(i+1)%len(turret);roofmesh.add([rings[-1][i],rings[-1][j],apex],[(0,1,2)])
finish(roofmesh,slate)
for dx in (-.16,.16):
 box('Roof turret crest upright',(cx+dx,cy,base+17.12),(.035,.035,.65),iron)
for h in (16.92,17.19,17.42):
 box('Roof turret crest crossbar',(cx,cy,base+h),(.28,.035,.035),iron)
# Floor bands and main cornice terminate at the corner, so no caps overlap.
for z,h,d in ((3.7,.15,.22),(7.35,.14,.22),(10.95,.25,.48),(11.35,.18,.60)):
 box('Trim Lord course',((x0+x1)/2,y1+d/2,base+z),(x1-x0,d,h),cream)
 box('Trim Eastbank course',(x1+d/2,(y0+y1)/2,base+z),(d,y1-y0,h),cream)
# White modillions beneath the projecting cornice, placed between openings.
for i in range(30):
 x=x0+.35+i*((x1-x0-.7)/29)
 box('Trim Lord cornice modillion',(x,y1+.20,base+10.71),(.22,.50,.34),cream)
for i in range(31):
 y=y0+.35+i*((y1-y0-.7)/30)
 box('Trim Eastbank cornice modillion',(x1+.20,y,base+10.71),(.50,.22,.34),cream)
# The first rail sits on the veranda roof. The second balcony has its own
# projecting floor and corbelled soffit. Rails stop at oriels and turret.
def intervals(lo,hi,gaps):
 out=[];start=lo
 for a,b in sorted(gaps):
  a=max(lo,a);b=min(hi,b)
  if a>start:out.append((start,a))
  start=max(start,b)
 if start<hi:out.append((start,hi))
 return out
def rail_rings(a,b,constant,z,axis,count):
 m=Mesh('Balcony iron scroll rings')
 for j in range(count):
  centre=a+(b-a)*(j+.5)/count;outer=min(.11,(b-a)/count*.38);inner=outer-.018
  def p(u,h):return (u,constant,base+z+h) if axis=='x' else (constant,u,base+z+h)
  for i in range(12):
   t0=2*math.pi*i/12;t1=2*math.pi*(i+1)/12
   v=[p(centre+outer*math.cos(t0),.49+outer*math.sin(t0)),p(centre+outer*math.cos(t1),.49+outer*math.sin(t1)),p(centre+inner*math.cos(t1),.49+inner*math.sin(t1)),p(centre+inner*math.cos(t0),.49+inner*math.sin(t0))]
   m.add(v,[(3,2,1,0) if axis=='x' else (0,1,2,3)])
 finish(m,iron)
front_gaps=[(-284.1,-281.9),(-274.3,-272.1),(-268.64,-266.24)]
for z in (4.46,7.58):
 if z>7:
  box('Balcony Lord slab',((x0+x1)/2,y1+.745,base+z),(x1-x0,.99,.12),cream)
  box('Balcony Eastbank slab',(x1+.745,(-35.0+y1)/2,base+z),(.99,y1+35.0,.12),cream)
  for x in (-284.7,-281.0,-277.3,-273.6,-269.9):box('Balcony Lord corbel',(x,y1+.48,base+z-.22),(.30,.75,.32),cream)
  for y in (-33.4,-29.7):box('Balcony Eastbank corbel',(x1+.48,y,base+z-.22),(.75,.30,.32),cream)
 fg=intervals(x0,x1,front_gaps)
 side_gaps=[(-44.6,-42.4),(-27.85,-25.45)]
 if z<7:side_gaps += [(-33.9,-31.7),(-41.1,-38.9)]
 sg=intervals(-35.0,y1,side_gaps)
 for a,b in fg:
  box('Balcony Lord handrail',((a+b)/2,y1+1.18,base+z+.95),(b-a,.06,.06),iron)
  count=max(1,int((b-a)/.33))
  for i in range(count+1):box('Balcony Lord spindle',(a+(b-a)*i/count,y1+1.18,base+z+.50),(.035,.035,.90),iron)
  rail_rings(a,b,y1+1.18,z,'x',count)
 for a,b in sg:
  box('Balcony Eastbank handrail',(x1+1.18,(a+b)/2,base+z+.95),(.06,b-a,.06),iron)
  count=max(1,int((b-a)/.33))
  for i in range(count+1):box('Balcony Eastbank spindle',(x1+1.18,a+(b-a)*i/count,base+z+.50),(.035,.035,.90),iron)
  rail_rings(a,b,x1+1.18,z,'y',count)
# Curved topped gables over the major bays, silhouetted against slate.
def gable(u,axis):
 # Smooth Dutch shoulder profile, inset painted coping separated from the
 # brick gable skin by its real forward projection.
 controls=[(-1.55,11.5),(-1.48,12.05),(-1.05,12.48),(-.95,13.60),(-.60,14.70),(0,15.10),(.60,14.70),(.95,13.60),(1.05,12.48),(1.48,12.05),(1.55,11.5)]
 curve=smooth_path(controls,4)
 def point(v,h,depth=0):return (u+v,y1+depth,base+h) if axis=='x' else (x1+depth,u+v,base+h)
 face=Mesh('Roof Dutch gable');face.add([point(v,h) for v,h in curve],[tuple(reversed(range(len(curve)))) if axis=='x' else tuple(range(len(curve)))]);finish(face,brick)
 edge=Mesh('Trim Dutch gable coping')
 inner=[]
 for v,h in curve:
  d=Vector((-v,12.2-h));d.normalize();inner.append((v+d.x*.10,h+d.y*.10))
 for i in range(len(curve)-1):
  p=[point(*curve[i],.04),point(*curve[i+1],.04),point(*inner[i+1],.04),point(*inner[i],.04)]
  edge.add(p,[(0,1,2,3) if axis=='x' else (3,2,1,0)])
 finish(edge,cream)
 band=Mesh('Trim gable curved band');n=20
 for i in range(n):
  v0=-1.02+2.04*i/n;v1=-1.02+2.04*(i+1)/n
  def height(v):return 12.55+.55*(1-(v/1.02)**2)
  points=[point(v0,height(v0),.055),point(v1,height(v1),.055),point(v1,height(v1)+.085,.055),point(v0,height(v0)+.085,.055)]
  band.add(points,[(3,2,1,0) if axis=='x' else (0,1,2,3)])
 finish(band,cream)
for x in (-283.0,-273.2):gable(x,'x')
for y in (-32.8,-40.0):gable(y,'y')
# Small attic windows are set within the prominent street-facing gables.
for x in (-283.0,-273.2):
 box('Window gable front glass',(x,y1+.018,base+12.35),(1.20,.03,1.25),glass)
 for dx in (-.59,-.20,.20,.59):box('Trim gable front stile',(x+dx,y1+.055,base+12.35),(.055,.08,1.20),cream)
 for zz in (11.72,12.14,12.56,12.98):
  for a,b in ((-.59,-.20),(-.20,.20),(.20,.59)):
   box('Trim gable front rail',(x+(a+b)/2,y1+.055,base+zz),(b-a-.06,.08,.055),cream)
for y in (-32.8,-40.0):
 box('Window gable side glass',(x1+.018,y,base+12.35),(.03,1.20,1.25),glass)
 for dy in (-.59,-.20,.20,.59):box('Trim gable side stile',(x1+.055,y+dy,base+12.35),(.08,.055,1.20),cream)
 for zz in (11.72,12.14,12.56,12.98):
  for a,b in ((-.59,-.20),(-.20,.20),(.20,.59)):
   box('Trim gable side rail',(x1+.055,y+(a+b)/2,base+zz),(.08,b-a-.06,.055),cream)
# Pedimented lower dormers and smaller upper dormers are visible on the
# raised mansard. Shapes and placement remain estimates pending comparison.
def dormer_front(x,row):
 y=y1-(.35 if row==0 else 1.65);z=12.5 if row==0 else 14.5
 box('Roof front dormer casing',(x,y,base+z),(1.20,.50,1.55),cream)
 # Subdivided panes in a shallow white casing, with a small pediment below.
 for dx in (-.33,0,.33):
  for dz in (-.54,-.18,.18,.54):
   m=Mesh('Window front dormer glass');m.add([(x+dx-.145,y+.26,base+z+dz-.15),(x+dx+.145,y+.26,base+z+dz-.15),(x+dx+.145,y+.26,base+z+dz+.15),(x+dx-.145,y+.26,base+z+dz+.15)],[(3,2,1,0)]);finish(m,glass)
 if row==0:
  m=Mesh('Roof dormer pediment');m.add([(x-.7,y+.27,base+z+.78),(x+.7,y+.27,base+z+.78),(x,y+.27,base+z+1.12)],[(0,1,2)]);finish(m,cream)
def dormer_side(y,row):
 x=x1-(.35 if row==0 else 1.65);z=12.5 if row==0 else 14.5
 box('Roof side dormer casing',(x,y,base+z),(.50,1.20,1.55),cream)
 for dy in (-.33,0,.33):
  for dz in (-.54,-.18,.18,.54):
   m=Mesh('Window side dormer glass');m.add([(x+.26,y+dy-.145,base+z+dz-.15),(x+.26,y+dy+.145,base+z+dz-.15),(x+.26,y+dy+.145,base+z+dz+.15),(x+.26,y+dy-.145,base+z+dz+.15)],[(0,1,2,3)]);finish(m,glass)
for row,positions in enumerate(((-280.8,-277.5,-270.9),(-280.0,-277.0,-269.5))):
 for x in positions:dormer_front(x,row)
for row,positions in enumerate(((-28.5,-34.5,-38.0,-44.0),(-28.5,-36.0,-38.2,-44.0))):
 for y in positions:dormer_side(y,row)
# Distinct tall brick chimney stacks are visible in the overhead obliques.
for x,y in [(-282.4,-30.2),(-272.6,-35.0),(-271.5,-43.0)]:
 box('Roof chimney',(x,y,base+16.1),(.8,.8,4.0),brick)
 box('Roof chimney cap',(x,y,base+18.14),(1.0,1.0,.16),cream)
 # Terracotta pots are individually spaced on the visible stack tops.
 pots=Mesh('Roof chimney pots')
 for dx in (-.29,0,.29):
  for dy in (-.20,.20):
   vertices=[]
   for z,radius in ((18.22,.07),(18.60,.07)):
    vertices.extend((x+dx+radius*math.cos(2*math.pi*i/8),y+dy+radius*math.sin(2*math.pi*i/8),base+z) for i in range(8))
   faces=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]+[tuple(range(8,16))]
   pots.add(vertices,faces)
 finish(pots,brick)
# Lord Street and Eastbank veranda, within this corner building only.
# Pavement belongs to the public-realm asset; no ground slab is added.
def veranda_post(x,y):
 # Dark turned base and slender painted column, with their common ring
 # owned only by side surfaces. Small rings suggest the capital and foot.
 def profile(name,rings,material):
  m=Mesh(name);n=12
  vertices=[(x+r*math.cos(2*math.pi*i/n),y+r*math.sin(2*math.pi*i/n),base+h) for h,r in rings for i in range(n)]
  faces=[]
  for k in range(len(rings)-1):
   for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
  m.add(vertices,faces);finish(m,material)
 profile('Veranda shaped base',[(0,.15),(.10,.15),(.16,.12),(.48,.09),(.62,.07)],iron)
 profile('Veranda column and capital',[(.62,.07),(3.46,.07),(3.52,.11),(3.62,.11),(3.70,.08)],white)
for x in (-285.7,-281.1,-276.5,-271.9,-267.3):veranda_post(x,y1+2.4)
for y in (-45.2,-40.5,-35.8,-31.1,-26.4):veranda_post(x1+2.4,y)
# Each veranda column carries an openwork bracket: slender curved ribs
# rise from its capital toward a small rosette under the fascia. The exact
# casting geometry remains an approximation of the photographed motif.
def bracket(x,y,axis):
 m=Mesh('Veranda bracket openwork')
 def point(u,h):return (x+u,y,base+h) if axis=='x' else (x,y+u,base+h)
 def sheet(points):
  p=[point(u,h) for u,h in points]
  signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
  indices=tuple(range(len(p)))
  m.add(p,[tuple(reversed(indices)) if (signed>0)==(axis=='x') else indices])
 for sign in (-1,1):
  # Separate narrow rays avoid multiple owners for their visible surfaces.
  for k in range(3):
   a=.08+k*.12;b=.36+k*.12;w=.035
   sheet([(sign*(a-w/2),3.24),(sign*(a+w/2),3.24),(sign*(b+w/2),3.675),(sign*(b-w/2),3.675)])
  centre=sign*.82;outer=.18;inner=.145
  for i in range(16):
   t0=2*math.pi*i/16;t1=2*math.pi*(i+1)/16
   sheet([(centre+outer*math.cos(t0),3.51+outer*math.sin(t0)),(centre+outer*math.cos(t1),3.51+outer*math.sin(t1)),(centre+inner*math.cos(t1),3.51+inner*math.sin(t1)),(centre+inner*math.cos(t0),3.51+inner*math.sin(t0))])
  # Six pierced petals within each annulus suggest the photographed rose.
  for petal in range(6):
   angle=2*math.pi*petal/6;pu=centre+.075*math.cos(angle);ph=3.51+.075*math.sin(angle)
   for i in range(8):
    t0=2*math.pi*i/8;t1=2*math.pi*(i+1)/8;ro=.03;ri=.018
    sheet([(pu+ro*math.cos(t0),ph+ro*math.sin(t0)),(pu+ro*math.cos(t1),ph+ro*math.sin(t1)),(pu+ri*math.cos(t1),ph+ri*math.sin(t1)),(pu+ri*math.cos(t0),ph+ri*math.sin(t0))])

 finish(m,white)
for x in (-285.7,-281.1,-276.5,-271.9,-267.3):bracket(x,y1+2.4,'x')
for y in (-45.2,-40.5,-35.8,-31.1,-26.4):bracket(x1+2.4,y,'y')
box('Veranda Lord fascia',((x0+x1)/2,y1+2.4,base+3.95),(x1-x0,.16,.55),white)
box('Veranda Eastbank fascia',(x1+2.4,(y0+y1)/2,base+3.95),(.16,y1-y0,.55),white)
# Sloping framed glass is authored as individual panes separated by ribs.
# It rises from the fascia to a flashing against the street wall.
def canopy_panel(name,points):
 m=Mesh(name);m.add(points,[(0,1,2,3)]);finish(m,glass)
for a,b in zip((-286.4,-281.1,-276.5,-271.9,-267.3),(-281.1,-276.5,-271.9,-267.3,-266.24)):
 canopy_panel('Veranda Lord roof glass',[(a+.04,y1,base+4.65),(b-.04,y1,base+4.65),(b-.04,y1+2.48,base+4.225),(a+.04,y1+2.48,base+4.225)])
for x in (-286.4,-281.1,-276.5,-271.9,-267.3,-266.24):bar_between('Veranda Lord roof rib',(x,y1,base+4.65),(x,y1+2.48,base+4.225),.065,white)
for a,b in zip((-46.42,-40.5,-35.8,-31.1,-26.4),(-40.5,-35.8,-31.1,-26.4,-25.45)):
 canopy_panel('Veranda Eastbank roof glass',[(x1,a+.04,base+4.65),(x1+2.48,a+.04,base+4.225),(x1+2.48,b-.04,base+4.225),(x1,b-.04,base+4.65)])
for y in (-46.42,-40.5,-35.8,-31.1,-26.4,-25.45):bar_between('Veranda Eastbank roof rib',(x1,y,base+4.65),(x1+2.48,y,base+4.225),.065,white)
# Secondary glazing bars sit above the panes, with the wider supports at
# column centres retained separately. Their spacing is an image estimate.
for i in range(1,32):
 x=x0+(x1-x0)*i/32
 if min(abs(x-v) for v in (-286.4,-281.1,-276.5,-271.9,-267.3,-266.24))>.08:
  bar_between('Veranda Lord glazing bar',(x,y1,base+4.70),(x,y1+2.48,base+4.275),.035,white)
for i in range(1,33):
 y=y0+(y1-y0)*i/33
 if min(abs(y-v) for v in (-46.42,-40.5,-35.8,-31.1,-26.4,-25.45))>.08:
  bar_between('Veranda Eastbank glazing bar',(x1,y,base+4.70),(x1+2.48,y,base+4.275),.035,white)
# The two arms meet at the outside corner, not at a duplicate square slab.
canopy_panel('Veranda corner roof glass',[(x1,y1,base+4.65),(x1+2.32,y1,base+4.225),(x1+2.32,y1+2.32,base+4.225),(x1,y1+2.32,base+4.225)])
box('Veranda corner fascia Lord',(x1+1.2,y1+2.4,base+3.95),(2.4,.16,.55),white)
box('Veranda corner fascia Eastbank',(x1+2.4,y1+1.16,base+3.95),(.16,2.32,.55),white)
veranda_post(x1+2.4,y1+2.4)
# The actual fascia lettering was legible in the August 2024 panorama.
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
label=text_object('Sign June the Florist','JUNE THE FLORIST',(-276.6,y1+2.49,base+3.95),(0,1,0),.38,8.0,font,iron,collection=c)
bpy.ops.object.select_all(action='DESELECT');label.select_set(True);bpy.context.view_layer.objects.active=label;bpy.ops.object.convert(target='MESH')
label=text_object('Sign Eastbank June the Florist','JUNE THE FLORIST',(x1+2.49,-30.5,base+3.95),(1,0,0),.38,6.0,font,iron,collection=c)
bpy.ops.object.select_all(action='DESELECT');label.select_set(True);bpy.context.view_layer.objects.active=label;bpy.ops.object.convert(target='MESH')
# Two entrance recesses have connected wall returns, leaf, transom and
# timber casing. The surrounding pavement owns the floor.
def front_door(name,x,width):
 front_y=y1-.18;back_y=y1-.65;h=2.42
 box('Shop '+name+' shadow',(x,back_y,base+h/2),(width-.18,.05,h-.18),iron)
 box('Shop '+name+' glass leaf',(x,back_y+.035,base+1.32),(width-.17,.025,1.95),glass)
 for xx in (x-width/2+.045,x+width/2-.045):
  box('Shop '+name+' jamb',(xx,(front_y+back_y)/2,base+h/2),(.09,front_y-back_y,h),wood)
 for zz in (.06,2.42):box('Shop '+name+' leaf rail',(x,back_y+.06,base+zz),(width,.10,.09),wood)
 box('Shop '+name+' transom',(x,back_y+.035,base+2.99),(width-.12,.035,1.05),glass)
 box('Shop '+name+' handle',(x+width*.29,back_y+.10,base+1.05),(.025,.045,.26),cream)
front_door('florist entrance',-280.2,.95)
front_door('chamber entrance',-284.30,1.35)
# Mitred border and inset glazing each own a distinct part of the pediment.
outer=[(-285.35,4.23),(-284.30,4.95),(-283.25,4.23)]
inner=[(-285.11,4.29),(-284.30,4.84),(-283.49,4.29)]
def pedpoint(p):return (p[0],y1+2.49,base+p[1])
m=Mesh('Veranda chamber pediment glass');m.add([pedpoint(p) for p in inner],[(2,1,0)]);finish(m,glass)
m=Mesh('Veranda pediment border');m.add([pedpoint(p) for p in outer+inner],[(3,4,1,0),(4,5,2,1),(5,3,0,2)]);finish(m,white)
for text,z,size in [('WESTMINSTER',4.49,.13),('MANSIONS',4.34,.12)]:
 ob=text_object('Sign chamber pediment '+text,text,(-284.30,y1+2.51,base+z),(0,1,0),size,1.1,font,white,collection=c)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
# Merge decorative ribs after authoring to keep exported object count bounded.
brackets=[o for o in c.objects if o.type=='MESH' and o.name.startswith('Veranda bracket')]
if brackets:
 bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT')
 for ob in brackets:ob.select_set(True)
 bpy.context.view_layer.objects.active=brackets[0];bpy.ops.object.join();brackets[0].name='Veranda openwork brackets'
# Roof bottoms and the narrow eave skirts are internal to the wall shell;
# remove them after Boolean unions so the wall owns the shared surfaces.
bm=bmesh.new();bm.from_mesh(roof.data)
internal=[face for face in bm.faces if all(v.co.z<=base+11.50001 for v in face.verts)]
bmesh.ops.delete(bm,geom=internal,context='FACES');bm.to_mesh(roof.data);bm.free();roof.data.update()
# Boolean cuts can create invalid inherited UV interpolation; rebuild metric
# UVs and triangulate the resulting shell and roof after all operations.
for ob in (front,roof):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 while ob.data.uv_layers:ob.data.uv_layers.remove(ob.data.uv_layers[0])
 uv=ob.data.uv_layers.new(name='metric rebuilt')
 for face in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
  for li in face.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/(1.8 if ob==front else 2.4),v[axes[1]]/(.6 if ob==front else 2.2))
# Align the Eastbank return to the OSM/aerial skew: east edge shifts
# approximately 0.77 m west over its 21 m depth. It is an estimate.
bpy.context.view_layer.update()
shear=Matrix(((1,.0367,0,-.0367*y1),(0,1,0,0),(0,0,1,0),(0,0,0,1)))
for obj in c.objects:
 if obj.type=='MESH':
  obj.data.transform(shear@obj.matrix_world)
  obj.matrix_world=Matrix.Identity(4)
  obj.data.update()
# Verify individual component ownership before semantic batching. The surface
# digest proves the resulting export preserves exactly those triangles and
# their material assignments, including winding.
sys.path.insert(0,str(ROOT/'scripts'))
from source_checks import validate as validate_source
from batch import digest,batch
bpy.context.view_layer.update();validate_source()
source_digest,source_count=digest([o for o in c.objects if o.type=='MESH'])
batch(c);bpy.context.view_layer.update()
export_digest,export_count=digest([o for o in c.objects if o.type=='MESH'])
assert (source_digest,source_count)==(export_digest,export_count), 'Batching changed checked surfaces'
s['source_surface_digest']=source_digest;s['source_triangle_count']=source_count
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.76,1)
light=bpy.data.lights.new('Sun','SUN');light.energy=2.5;o=bpy.data.objects.new('Sun',light);s.collection.objects.link(o);o.rotation_euler=(-.45,.6,.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=900
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/westminster-chambers.blend'))
