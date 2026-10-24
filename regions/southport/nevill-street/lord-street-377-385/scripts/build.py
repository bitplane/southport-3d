"""377–385 Lord Street: measured rounded classical corner and iron canopy."""
import json,math,os,sys,re
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from components import rect,cuts,arch,ring,path_profile,outline
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];R=D['radius'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';collections={}
for part in ['facades','roof','frontage','canopy']:
 c=bpy.data.collections.new(part);s.collection.children.link(c);collections[part]=c
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
F=face_matrix((0,0,0),(0,-1,0));S=Matrix(((0,0,-1,0),(1,0,0,0),(0,1,0,0),(0,0,0,1)))
def material(name,rgb,rough=.75):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;return m
stone=material('Warm pale limestone',(.63,.58,.46));trim=material('Cream dressed stone',(.72,.67,.55));joint=material('Stone joint shadow',(.44,.41,.34));rear=material('Unobserved rear masonry',(.39,.33,.28))
white=material('Warm white painted frames',(.79,.79,.70),.46);glass=material('Blue grey opaque glazing',(.10,.155,.17),.24);black=material('Dark green shopfront',(.035,.046,.042),.39)
iron=material('Painted green iron',(.034,.047,.038),.48);canopyglass=material('Muted canopy glazing approximation',(.26,.32,.33),.33);lead=material('Roof membrane',(.21,.27,.32));metal=material('Painted silver ductwork',(.50,.53,.51),.40);shadow=material('Ventilation shadow',(.035,.038,.038));gold=material('Warm sign lettering',(.80,.73,.53),.40)
COL={};FAMILIES={}
def finish(m,part='facades',mat=stone,frame=None,curve=False):
 if not m.faces:return
 if m.name.startswith('Wall '):m=conform({'wall':m})[0]['wall']
 if curve:
  m.vertices=[(R+(R+out)*math.cos(math.pi+u/R),R+(R+out)*math.sin(math.pi+u/R),z) for u,z,out in m.vertices]
 ob=m.finish([mat],collections[part]);bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 if frame is not None and frame.to_3x3().determinant()<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 transform=T@(frame if frame is not None else Matrix.Identity(4));ob.data.transform(transform)
 if m.name.startswith(('Column Ionic','Canopy cast iron post')):
  for p in ob.data.polygons:p.use_smooth=abs(p.normal.z)<.90
 return ob

def box(name,c,size,mat=stone,part='facades',frame=None,curve=False):
 m=Mesh(name);m.box(c,size);return finish(m,part,mat,frame,curve)
def tube(name,points,r,mat=iron,part='canopy',sides=8,frame=None,curve=False):
 m=Mesh(name);m.tube(points,r,sides=sides);return finish(m,part,mat,frame,curve)
def wall(poly,holes,name,frame=None,curve=False):
 m=Mesh('Wall '+name)
 for p in cuts(poly,holes):
  # Subdivide curve-space rectangles into narrow panels before wrapping.
  polys=[p]
  if curve:
   grid=sorted(set([x for h in holes for x,z in h]+[R*math.pi/2*j/32 for j in range(33)]));polys=[]
   for lo,hi in zip(grid,grid[1:]):
    if hi-lo<1e-6:continue
    for q in cuts(p,[rect(-10,-10,lo,30),rect(hi,-10,40,30)]):polys.append(q)
  for q in polys:
   m.add([(*v,0) for v in q],[tuple(range(len(q)))])
   m.add([(*v,-.30) for v in q],[tuple(reversed(range(len(q))))])
 for p in holes:
  for a,b in zip(p,p[1:]+p[:1]):
   splits=[a,b]
   if curve and abs(b[0]-a[0])>1e-8:
    us=[a[0]]+[u for u in grid if min(a[0],b[0])+1e-7<u<max(a[0],b[0])-1e-7]+[b[0]];us.sort(reverse=b[0]<a[0]);splits=[(u,a[1]+(b[1]-a[1])*(u-a[0])/(b[0]-a[0])) for u in us]
   for aa,bb in zip(splits,splits[1:]):m.add([(*aa,0),(*bb,0),(*bb,-.30),(*aa,-.30)],[(0,1,2,3)])
 return finish(m,'facades',stone,frame,curve)

# Street elevations are continuous aperture-bearing skins, not windows pasted
# over solid walls. The corner has one curved upper bay and a chamfered door.
for name,frame,end,bays in [('Lord',F,W,D['front_bays']),('Nevill',S,L,D['side_bays'])]:
 holes=[]
 for b in bays:
  u=b['u'];w=b['w'];holes.append(rect(u-w/2,4.75,u+w/2,8.80))
  holes.append(arch(u,9.55,11.15,w/2,1.10) if b['arch'] else rect(u-w/2,9.55,u+w/2,12.25))
 wall(rect(R,4.55,end,14.10),holes,name,frame)
 for i,b in enumerate(bays):
  u=b['u'];w=b['w']
  for j,(lo,hi) in enumerate([(4.75,8.80),(9.55,12.25)]):
   p=arch(u,lo,11.15,w/2,1.10) if j and b['arch'] else rect(u-w/2,lo,u+w/2,hi)
   m=Mesh('Glazing '+name+' '+str(i)+' '+str(j));m.outline(p,-.27,-.23);finish(m,'frontage',glass,frame)
  # Thin outer frame and triple lights, also required in massing comparison.
  m=Mesh('Frames '+name+' '+str(i))
  for lo,hi in [(4.75,8.80),(9.55,12.25)]:
   for dx in (-w/2+.035,-w/4,w/4,w/2-.035):
    cap=hi
    if lo>9 and b['arch']:cap=11.15+1.1*math.sqrt(max(0,1-(dx/(w/2))**2))
    m.box((u+dx,(lo+cap)/2,-.13),(.055,cap-lo,.12))
   m.box((u,lo+.04,-.13),(w,.08,.12))
   if lo<9:
    m.box((u,7.38,-.11),(w,.085,.12));m.box((u,hi-.04,-.13),(w,.08,.12))
   elif not b['arch']:
    m.box((u,hi-.04,-.13),(w,.08,.12))
    for sign in (-1,1):m.box((u+sign*w*.375,hi-.50,-.115),(w*.25,.035,.10))
   else:ring(m,u,11.15,w/2-.07,1.03,.055,-.18,-.07,n=32)
  finish(m,'frontage',white,frame)
  for z in (4.61,9.43):box('Trim projecting sill',(u,z,.12),(w+.30,.18,.42),trim,frame=frame)
  if b['arch']:
   m=Mesh('Trim upper arch');ring(m,u,11.15,w/2,1.10,.17,-.01,.15,n=40);finish(m,mat=trim,frame=frame)
   m=Mesh('Trim arch keystone');m.outline([(u-.20,12.10),(u+.20,12.10),(u+.29,12.52),(u-.29,12.52)],.12,.28);finish(m,mat=trim,frame=frame)
  # Spandrel is a deep, rectangular stone panel, restrained until detail pass.
  if not b['arch']:box('Trim spandrel',(u,9.13,.035),(w+.04,.59,.07),trim,frame=frame)
 # Solid bay piers: front arched bay flanked by broad pilasters; side arches too.
 for b in [b for b in bays if b['arch']]:
  for sign in (-1,1):box('Pilaster '+name,(b['u']+sign*(b['w']/2+.45),8.80,.10),(.72,8.50,.20),trim,frame=frame)
 # Side/front end piers remain narrow to avoid exceeding neighbouring footprint.
 box('End pier '+name,(end-.30,8.8,.08),(.60,8.5,.16),trim,frame=frame)

arcL=R*math.pi/2;cu=arcL/2;cw=2.45
wall(rect(0,4.55,arcL,14.10),[rect(cu-cw/2,4.75,cu+cw/2,8.80),rect(cu-cw/2,9.55,cu+cw/2,12.25)],'curved corner',curve=True)
for lo,hi in [(4.75,8.80),(9.55,12.25)]:
 m=Mesh('Glazing curved corner')
 for j in range(16):
  a=cu-cw/2+cw*j/16;b=a+cw/16;m.add([(a,lo,-.23),(b,lo,-.23),(b,hi,-.23),(a,hi,-.23)],[(0,1,2,3)])
 finish(m,'frontage',glass,curve=True)
 for dx in (-cw/2+.035,-cw/4,cw/4,cw/2-.035):box('Frames curved mullion',(cu+dx,(lo+hi)/2,-.13),(.055,hi-lo,.12),white,'frontage',curve=True)
 for z in (lo+.04,hi-.04,7.38) if lo<9 else (lo+.04,hi-.04):
  m=Mesh('Frames curved rail')
  for j in range(16):m.box((cu-cw/2+cw*(j+.5)/16,z,-.13),(cw/16,.07,.12))
  finish(m,'frontage',white,curve=True)
box('Trim corner spandrel',(cu,9.13,.035),(cw+.05,.59,.07),trim,curve=True)
# Ionic shafts: smooth shafts with course joints, not invented deep fluting.
columns=[('Nevill A',S,10.5,False),('Nevill B',S,14.0,False),('Corner A',None,.45,True),('Corner B',None,arcL-.45,True)]
for name,frame,u,curved in columns:
 m=Mesh('Column Ionic '+name)
 m.lathe((u,-.20),[(4.55,.50),(4.68,.50),(4.74,.46),(4.82,.46),(4.90,.43),(5.0,.42),(8.8,.395),(11.90,.36),(12.05,.39),(12.13,.44),(12.25,.47),(12.45,.47)],40)
 m.vertices=[(x,z,-y) for x,y,z in m.vertices];ob=finish(m,mat=trim,frame=frame,curve=curved)
 box('Column abacus '+name,(u,12.52,.20),(1.08,.16,.97),trim,frame=frame,curve=curved)
 if DETAIL:
  # Paired scrolls at the front of the Ionic capital, with a connected bolster.
  for sign in (-1,1):
   pts=[]
   for j in range(65):
    a=math.tau*1.65*j/64;rr=.225*(1-j/74);pts.append((u+sign*.32+sign*rr*math.cos(a),12.33+rr*math.sin(a),.62))
   tube('Fine Ionic volute '+name,pts,.030,trim,'facades',8,frame,curved)
  box('Fine Ionic bolster '+name,(u,12.35,.50),(.57,.16,.20),trim,frame=frame,curve=curved)
  for z in (5.65,6.50,7.35,8.20,9.05,9.9,10.75,11.6):
   rr=.42-(z-5)*.06/6.9;m=Mesh('Fine shaft course '+name);m.lathe((u,-.20),[(z-.004,rr+.002),(z+.004,rr+.002)],40);m.vertices=[(x,z,-y) for x,y,z in m.vertices];finish(m,mat=joint,frame=frame,curve=curved)

# Roof and rear boundary: a rear-edge notch stays open above the lower service roof.
poly=outline(W,L,R,32,D['lightwell']);m=Mesh('Roof membrane');m.add([(*v,13.85) for v in poly],[tuple(range(len(poly)))]);finish(m,'roof',lead)
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 if i==0 or i>=7:continue # Street elevations already own these skins.
 low=8.7 if i in (3,4,5) else 0
 m=Mesh('Wall rear boundary '+str(i));m.add([(*a,low),(*b,low),(*b,13.85),(*a,13.85)],[(0,1,2,3)]);finish(m,mat=rear)
well=D['lightwell'];a,b=well['x'];lo,hi=well['y'];m=Mesh('Roof service well floor');m.add([(a,lo,8.7),(b,lo,8.7),(b,hi,8.7),(a,hi,8.7)],[(0,1,2,3)]);finish(m,'roof',lead)
m=Mesh('Wall lower rear below lightwell');m.add([(a,L,0),(a,L,8.7),(b,L,8.7),(b,L,0)],[(0,1,2,3)]);finish(m,mat=rear)
# Continuous cornice follows both straight elevations and the true quarter circle.
path=[(0,L,-1,0),(0,21.45,-1,0),(-.18,21.45,-1,0),(-.18,17.45,-1,0),(0,17.45,-1,0),(0,7.15,-1,0),(-.18,7.15,-1,0),(-.18,R,-1,0)]+[(R+(R+.18)*math.cos(math.pi+i*math.pi/48),R+(R+.18)*math.sin(math.pi+i*math.pi/48),math.cos(math.pi+i*math.pi/48),math.sin(math.pi+i*math.pi/48)) for i in range(1,25)]+[(7.15,-.18,0,-1),(7.15,0,0,-1),(W,0,0,-1)]
profile=[(12.60,0),(12.60,.14),(12.72,.14),(12.78,.24),(12.95,.24),(13.05,.36),(13.18,.36),(13.22,.12),(13.62,.12),(13.68,.28),(13.77,.33),(13.87,.45),(14.00,.45),(14.06,.11),(14.10,0)]
m=Mesh('Trim continuous cornice');path_profile(m,path,profile);finish(m,mat=trim)
# Capped parapet, open balustrade over the rounded corner only.
for name,frame,end,bays in [('Lord',F,W,D['front_bays']),('Nevill',S,L,D['side_bays'])]:
 box('Parapet '+name,((R+end)/2,14.275,-.16),(end-R,.35,.32),stone,frame=frame)
 box('Parapet coping '+name,((R+end)/2,14.48,-.13),(end-R,.12,.43),trim,frame=frame)
 for b in [b for b in bays if b['arch']]:
  u=b['u'];box('Parapet raised panel '+name,(u,14.68,-.10),(3.55,.52,.36),stone,frame=frame)
  box('Parapet panel cap '+name,(u,14.98,-.10),(3.70,.12,.46),trim,frame=frame)
  if DETAIL:
   for z in (14.45,14.86):box('Fine parapet inset border',(u,z,.10),(3.22,.045,.045),trim,frame=frame)
   pts=[(u-1.20+2.4*j/48,14.82-.29*math.sin(math.pi*j/48),.13) for j in range(49)];tube('Fine parapet swag',pts,.035,trim,'facades',8,frame)
   for sign in (-1,1):
    for j in range(4):box('Fine parapet ribbon',(u+sign*(1.12+j*.035),14.70-j*.025,.13),(.035,.20-j*.02,.045),trim,frame=frame)
# Low parapet piers are visible above the two Nevill Ionic shafts. The narrow
# Lord Street end pier rises slightly higher; these are not chimney stacks.
for name,frame,u,width,top in [('Nevill A',S,10.5,.75,14.80),('Nevill B',S,14.0,.75,14.80),('Lord end',F,W-.25,.48,15.10)]:
 box('Parapet pier '+name,(u,(14.44+top)/2,-.08),(width,top-14.44,.36),stone,frame=frame)
 box('Parapet pier cap '+name,(u,top+.05,-.08),(width+.12,.10,.46),trim,frame=frame)
# Short radial piers and rail keep actual openings in the corner balustrade.
for j in range(13):
 u=arcL*j/12
 box('Corner balustrade pier',(u,14.33,-.12),(.14,.43,.25),trim,curve=True)
m=Mesh('Corner balustrade coping');path_profile(m,[(R+R*math.cos(math.pi+i*math.pi/48),R+R*math.sin(math.pi+i*math.pi/48),math.cos(math.pi+i*math.pi/48),math.sin(math.pi+i*math.pi/48)) for i in range(25)],[(14.51,-.30),(14.51,.08),(14.61,.08),(14.61,-.30)]);finish(m,mat=trim)

# Ground glass frontage has a chamfered double door under the rounded stone bay.
for name,frame,end in [('Lord',F,W),('Nevill',S,L)]:
 start=2.0
 m=Mesh('Shopfront glazing '+name);m.add([(start,.195,-.015),(end,.195,-.015),(end,4.045,-.015),(start,4.045,-.015)],[(0,1,2,3)]);finish(m,'frontage',glass,frame)
 box('Shopfront fascia '+name,((start+end)/2,4.28,.05),(end-start,.54,.26),black,'frontage',frame)
 box('Shopfront plinth '+name,((start+end)/2,.16,.015),(end-start,.32,.20),black,'frontage',frame)
 n=max(1,round((end-start)/1.9));m=Mesh('Shopfront frames '+name)
 for j in range(n+1):m.box((start+(end-start)*j/n,2.15,.02),(.075,4.0,.16))
 for z in (.34,3.92):m.box(((start+end)/2,z,.025),(end-start,.08,.17))
 finish(m,'frontage',black,frame)
# Chamfer joins both straight glazing walls without a stray curved wall behind it.
G=face_matrix((1.,1.,0),(-1,-1,0));doorwidth=math.sqrt(8)
box('Entrance glazed screen',(0,2.12,-.065),(doorwidth,3.85,.10),glass,'frontage',G)
box('Entrance fascia',(0,4.28,.05),(doorwidth,.54,.26),black,'frontage',G)
for u in (-doorwidth/2+.04,-.82,0,.82,doorwidth/2-.04):box('Entrance frame',(u,1.50,.015),(.07,2.86,.16),black,'frontage',G)
for z in (.13,2.94,3.96):box('Entrance rail',(0,z,.02),(doorwidth,.08,.17),black,'frontage',G)
for u in (-.13,.13):box('Entrance handle',(u,1.35,.15),(.025,.75,.045),metal,'frontage',G)
box('Entrance threshold',(0,.015,0),(doorwidth,.03,.30),lead,'frontage',G)
# Canopy: a glazed sloping roof, fascia and supports, never a filled arcade block.
# All glazing uses an opaque approximation for the current dielectric bake pipeline.
outer=R+D['canopy_depth'];cp=[(0,L,-1,0),(0,R,-1,0)]+[(R+R*math.cos(math.pi+i*math.pi/64),R+R*math.sin(math.pi+i*math.pi/64),math.cos(math.pi+i*math.pi/64),math.sin(math.pi+i*math.pi/64)) for i in range(1,33)]+[(W,0,0,-1)]
m=Mesh('Canopy roof glazing');path_profile(m,cp,[(4.02,3.05),(4.55,.12),(4.53,.12),(4.00,3.05),(4.02,3.05)]);finish(m,'canopy',canopyglass)
m=Mesh('Canopy outer fascia');path_profile(m,cp,[(3.15,3.05),(3.35,3.05),(3.35,2.96),(3.15,2.96)]);finish(m,'canopy',iron)
m=Mesh('Canopy outer upper rail');path_profile(m,cp,[(4.00,3.02),(4.06,3.02),(4.06,3.10),(4.00,3.10)]);finish(m,'canopy',iron)
m=Mesh('Canopy inner rail');path_profile(m,cp,[(4.49,.10),(4.60,.10),(4.60,.19),(4.49,.19)]);finish(m,'canopy',iron)
for name,frame,end in [('Lord',F,W),('Nevill',S,L)]:
 n=max(1,round((end-R)/.72))
 for j in range(n+1):
  u=R+(end-R)*j/n;tube('Canopy glazing bar '+name,[(u,4.57,.12),(u,4.04,3.08)],.025,iron,'canopy',4,frame)
  box('Canopy vertical frieze bar',(u,3.69,3.055),(.045,.70,.065),iron,'canopy',frame)
 for u in D['canopy_posts_front' if name=='Lord' else 'canopy_posts_side']:
  m=Mesh('Canopy cast iron post '+name);m.lathe((u,-3.05),[(0,.13),(.10,.13),(.14,.10),(.35,.10),(.46,.07),(.52,.07),(2.78,.047),(2.88,.065),(3.02,.085),(3.15,.085)],16);m.vertices=[(x,z,-y) for x,y,z in m.vertices];finish(m,'canopy',iron,frame)
  tube('Canopy structural bracket '+name,[(u,3.05,3.03),(u,4.45,.32)],.043,iron,'canopy',8,frame)
  if DETAIL:
   for phase in (0,math.tau/3,2*math.tau/3):
    pts=[(u+.054*math.cos(phase+math.tau*3*j/72),.56+2.18*j/72,3.05+.054*math.sin(phase+math.tau*3*j/72)) for j in range(73)];tube('Fine canopy spiral shaft',pts,.007,iron,'canopy',5,frame)
   for sign in (-1,1):
    pts=[(u+sign*(.12+.65*i/32),3.01+.13*math.sin(math.pi*i/32),3.055) for i in range(33)];tube('Fine canopy scroll rail',pts,.018,iron,'canopy',6,frame)
    pts=[]
    for j in range(50):
     a=math.tau*1.25*j/49;rr=.22*(1-j/60);pts.append((u+sign*.40+sign*rr*math.cos(a),2.86+rr*math.sin(a),3.055))
    tube('Fine canopy bracket volute',pts,.018,iron,'canopy',6,frame)
for j in range(15):
 a=math.pi+j*math.pi/28;nx,ny=math.cos(a),math.sin(a)
 tube('Canopy radial glazing bar',[(R+(R+.12)*nx,R+(R+.12)*ny,4.57),(R+outer*nx,R+outer*ny,4.04)],.025,iron,'canopy',4)
 tube('Canopy radial frieze bar',[(R+outer*nx,R+outer*ny,3.35),(R+outer*nx,R+outer*ny,4.02)],.025,iron,'canopy',4)
# Identifiable service-roof equipment from the overhead; hidden interfaces estimated.
box('Roof air handling cabinet',(10.7,19.8,14.38),(2.4,3.4,1.06),metal,'roof')
for name,points,low,high in [('main',[(4.16,9.2),(4.64,9.2),(4.64,13.46),(7.34,13.46),(7.34,17.86),(9.9,17.86),(9.9,18.34),(6.86,18.34),(6.86,13.94),(4.16,13.94)],13.96,14.44),('front',[(8.76,3.2),(9.24,3.2),(9.24,5.76),(10.8,5.76),(10.8,6.24),(8.76,6.24)],13.86,14.34)]:
 m=Mesh('Roof silver duct '+name);m.outline(points,low,high);finish(m,'roof',metal)
for x,y in [(3.8,18.2),(4.5,21.0),(10.0,10.0)]:box('Roof dark vent',(x,y,14.08),(.42,.52,.46),shadow,'roof')

# Detailed ornament is added only after a proportion/placement comparison.
if DETAIL:
 for name,frame,end,bays in [('Lord',F,W,D['front_bays']),('Nevill',S,L,D['side_bays']),('Corner',None,arcL,[{'u':cu,'w':cw,'arch':False}])]:
  curved=name=='Corner'
  for b in bays:
   u=b['u'];w=b['w']
   if not b['arch']:
    # Wreath medallion, with the rectangular recessed panel and flanking reeds.
    for zz in (8.91,9.35):box('Fine panel border',(u,zz,.09),(w-.14,.035,.055),trim,frame=frame,curve=curved)
    for xx in (u-w/2+.07,u+w/2-.07):box('Fine panel border',(xx,9.13,.09),(.035,.44,.055),trim,frame=frame,curve=curved)
    m=Mesh('Fine spandrel wreath');ring(m,u,9.13,.18,.18,.045,.075,.14,start=0,end=math.tau,n=40);finish(m,mat=trim,frame=frame,curve=curved)
    m=Mesh('Fine wreath leaves')
    for j in range(16):
     a=math.tau*j/16;cx=u+.215*math.cos(a);cz=9.13+.215*math.sin(a);vx=.060*math.cos(a+.6);vz=.060*math.sin(a+.6);wx=-.023*math.sin(a+.6);wz=.023*math.cos(a+.6);m.outline([(cx-vx,cz-vz),(cx+wx,cz+wz),(cx+vx,cz+vz),(cx-wx,cz-wz)],.10,.155)
    finish(m,mat=trim,frame=frame,curve=curved)
    for sign in (-1,1):
     for j in range(6):box('Fine spandrel reed',(u+sign*(.44+j*.065),9.13,.095),(.018,.21,.045),trim,frame=frame,curve=curved)
   # Frames and window surrounds are narrow; avoid thick fake masonry rims.
   for dx in (-w/2-.055,w/2+.055):box('Trim window bead',(u+dx,6.77,.045),(.07,4.12,.09),trim,frame=frame,curve=curved)
  # Ashlar joints are shallow lines restricted to exposed piers and spandrels.
  if not curved:
   openings=[rect(b['u']-b['w']/2-.20,4.55,b['u']+b['w']/2+.20,12.50) for b in bays]
   for row in range(14):
    z=4.75+row*.57
    for p in cuts(rect(R,z-.004,end,z+.004),openings):
     m=Mesh('Fine ashlar joints');m.outline(p,.001,.008);finish(m,mat=joint,frame=frame)
 # The July 2026 name is still visible in the first-floor windows and fascia.
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
 def lettering(body,name,u,z,out,height,width,frame):
  ob=text_object(name,body,(0,0,0),(0,0,1),height,width,font,gold,extrude=.003,collection=collections['frontage'],fit_bounds=True)
  mat=Matrix.Translation((u,z,out))@(Matrix.Diagonal((-1,1,1,1)) if frame.to_3x3().determinant()<0 else Matrix.Identity(4))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(T@frame@mat);ob.matrix_world=Matrix.Identity(4)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='Lettering')
 for frame,u,width in [(F,7.4,3.45),(S,12.2,3.60)]:lettering('BISTROT PIERRE','Sign fascia lettering',u,4.24,.184,.20,width,frame)
 for frame,u in [(F,5.15),(S,8.75),(S,12.25)]:
  lettering('BISTROT','Sign window upper',u,5.90,-.165,.14,.70,frame);lettering('PIERRE','Sign window name',u,5.61,-.165,.23,1.05,frame)
 # Cabinet louvres and duct seams visible from above, deliberately absent in Walk.
 for j in range(13):box('Fine rooftop louvre',(10.7,18.085,14.05+j*.045),(2.05,.018,.018),shadow,'roof')

# Batch by streaming part and LoD/audit policy, not by individual window.
# Selected-to-active bake cost grows strongly with the number of source objects.
# Keep shell surfaces separate so the overlap guard still checks actual geometry.
families={}
for ob in list(s.objects):
 if ob.type!='MESH':continue
 kind='Fine' if ob.name.startswith('Fine ') else 'Shell' if ob.name.startswith(('Wall ','Roof membrane','Roof silver duct','Roof service well floor')) else 'Architecture'
 families.setdefault((ob.users_collection[0].name,kind),[]).append(ob)
for (part,kind),obs in families.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 obs[0].name=kind+' '+part
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.4,-.5);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/lord-street-377-385.blend'))
