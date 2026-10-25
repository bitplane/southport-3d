"""Willow Grove joined exterior: Lord palazzo, Boots facade and service range."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix
from southport3d.conform import conform
from components import rect,cuts,arch,ring
from roof_controls import chimney_bounds
D=json.loads((ROOT/'research/layout.json').read_text());A=D['front_left'];W=A+D['front_width'];B=D['back'];Y=D['wing_start'];Z=D['wing_end'];R=D['rear_strip_left'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for p in ['lord','nevill','rear','roof','canopy']:
 c=bpy.data.collections.new(p);s.collection.children.link(c);C[p]=c
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
F=face_matrix((A,0,0),(0,-1,0));N=Matrix(((0,0,-1,0),(1,0,0,Y),(0,1,0,0),(0,0,0,1)))
def material(name,rgb,rough=.75,brick=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;nt=m.node_tree;p=nt.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
 if brick:
  uv=nt.nodes.new('ShaderNodeTexCoord');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures'/('paintbrick.png' if 'White' in name else 'brick.png')));tex.interpolation='Linear';tex.extension='REPEAT';nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 return m
cream=material('Warm off white painted masonry',(.72,.70,.61));white=material('Light dressed mouldings',(.83,.80,.70));stone=material('Boots pale limestone',(.62,.58,.48));shade=material('Recessed stone shadow',(.46,.43,.36));brick=material('Weathered red service brick',(.40,.22,.16),brick=True);paintbrick=material('White painted courtyard brick',(.68,.68,.61),brick=True)
slate=material('Blue grey slate',(.125,.145,.16));lead=material('Dark flat roof membrane',(.15,.17,.18));glass=material('Muted blue grey glazing',(.13,.20,.23),.27);frame=material('Warm pale window frames',(.79,.79,.70),.42);shop=material('Refurbished grey green joinery',(.29,.34,.30),.50);iron=material('Black painted cast iron',(.035,.045,.039),.48);cglass=material('Opaque muted canopy glazing',(.32,.37,.35),.35);metal=material('Galvanised roof fittings',(.45,.49,.48),.4);wood=material('Blank timber fascia 2023',(.31,.24,.17));black=material('Dark vents',(.025,.03,.028));pot=material('Terracotta chimney pots',(.37,.20,.13))
def finish(m,part,mat,frameM=None):
 if not m.faces:return
 if m.name.startswith('Shell wall'):m=conform({'m':m})[0]['m']
 ob=m.finish([mat],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 if frameM is not None and frameM.to_3x3().determinant()<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Metric')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 ob.data.transform(T@(frameM if frameM is not None else Matrix.Identity(4)));return ob

def box(name,c,size,mat=cream,part='lord',M=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,mat,M)
def tube(name,pts,r,mat=white,part='lord',M=F,sides=8):
 m=Mesh(name);m.tube(pts,r,sides=sides);return finish(m,part,mat,M)
def wall(name,poly,holes,mat,part,M):
 m=Mesh('Shell wall '+name)
 for q in cuts(poly,holes):
  m.add([(*v,0) for v in q],[tuple(range(len(q)))]);m.add([(*v,-.24) for v in q],[tuple(reversed(range(len(q))))])
 for q in holes:
  for a,b in zip(q,q[1:]+q[:1]):m.add([(*a,0),(*b,0),(*b,-.24),(*a,-.24)],[(0,1,2,3)])
 return finish(m,part,mat,M)
def panel(name,poly,depth,mat,part,M):
 m=Mesh(name);m.outline(poly,depth-.03,depth);return finish(m,part,mat,M)
def arc(name,u,z,rx,ry,t,out,mat,part,M,n=24):
 m=Mesh(name);ring(m,u,z,rx,ry,t,out-.08,out,n=n);return finish(m,part,mat,M)
def column(name,u,lo,hi,r,out,mat,part,M):
 m=Mesh(name);m.lathe((u,-out),[(lo,r*1.45),(lo+.10,r*1.45),(lo+.18,r),(hi-.20,r*.83),(hi-.13,r*1.32),(hi,r*1.32)],16);m.vertices=[(x,z,-y) for x,y,z in m.vertices];return finish(m,part,mat,M)
# Lord Street: two equal grouped arcades, with genuine openings through the wall.
openings=[]
for bay in D['bay_centres']:
 for off in D['light_offsets']:
  u=bay+off
  for q in [D['first_windows'],D['second_windows']]:openings.append(arch(u,q['bottom'],q['spring'],q['radius'],q['rise'],24))
wall('Lord',rect(0,4.50,D['front_width'],12.4598),openings,cream,'lord',F)
for bay in D['bay_centres']:
 for off in D['light_offsets']:
  u=bay+off
  for floor,q in enumerate([D['first_windows'],D['second_windows']]):
   lo,sp,rx,ry=q['bottom'],q['spring'],q['radius'],q['rise'];panel('Window glazing',arch(u,lo,sp,rx,ry,24),-.205,glass,'lord',F)
   for dx in (-rx+.032,rx-.032):box('Window jamb',(u+dx,(lo+sp)/2,-.135),(.05,sp-lo,.10),frame)
   for z in (lo+.03,sp-.11):box('Window cross rail',(u,z,-.13),(2*rx,.055,.11),frame)
   arc('Window arched frame',u,sp,rx-.055,ry-.055,.045,-.10,frame,'lord',F)
   arc('Moulded window archivolt',u,sp,rx,ry,.13,.16,white,'lord',F)
   if floor==0:arc('Fine outer arch hood',u,sp,rx+.16,ry+.16,.045,.12,white,'lord',F)
   box('Window projecting sill',(u,lo-.075,.12),(1.20,.15,.48),white)
  # Side shafts belong to the individual arcade; neighbouring paired shafts
  # remain thin rather than filling the opening with large generic columns.
  for side in (-1,1):
   x=u+side*.57;column('Arcade colonnettes',x,4.91,7.34,.075,.11,white,'lord',F);column('Short upper colonnettes',x,9.10,10.64,.065,.06,white,'lord',F)
   if DETAIL:
    for zz in (7.22,7.30):
     for j in range(5):
      xx=x+(j-2)*.035;tube('Fine foliate capital',[(xx-.018,zz-.09,.23),(xx,zz,.27),(xx+.018,zz-.05,.23)],.018,white,sides=6)
  if DETAIL:
   # Thin masonry panel edge above each arch; foliated spandrels as authored relief.
   for side in (-1,1):
    xx=u+side*.51
    for j in range(3):tube('Fine spandrel leaf',[(xx,8.04,.075),(xx+side*.07,8.10+j*.045,.14),(xx+side*.12,8.13+j*.045,.09)],.018,white,sides=6)
 for zz in (8.37,8.68):box('Sunk panel rail',(bay,zz,.06),(5.04,.07,.12),white)
 for xx in (bay-2.49,bay+2.49):box('Sunk panel edge',(xx,8.525,.06),(.055,.24,.12),white)
# Pilasters at centre and ends, with single ownership at each boundary.
for u,w in [(.24,.48),(6.22,.65),(D['front_width']-.24,.48)]:
 box('Plain upper pilaster',(u,8.58,.075),(w,7.70,.15))
for z,h,out in [(4.63,.20,.18),(8.83,.15,.15),(11.36,.11,.14),(11.85,.19,.30),(12.18,.18,.42),(12.37,.12,.30)]:box('Continuous Lord course',(D['front_width']/2,z,out/2),(D['front_width'],h,out),white)
# Heavy cornice brackets: tapered corbels below a continuous upper ledge.
for i in range(18):
 u=.35+i*(D['front_width']-.7)/17
 m=Mesh('Cornice consoles');m.outline([(u-.10,11.40),(u+.10,11.40),(u+.15,11.77),(u-.15,11.77)],.04,.30);finish(m,'lord',white,F)
 if DETAIL:box('Fine cornice console step',(u,11.62,.32),(.12,.14,.07),shade)
# Pierced circles cut through real parapet panels; no painted dark discs.
parapet_holes=[]
for bay in D['bay_centres']:
 for j in range(8):
  u=bay-2.24+j*.64;parapet_holes.append([(u+.20*math.cos(math.tau*k/24),12.91+.20*math.sin(math.tau*k/24)) for k in range(24)])
wall('pierced parapet',rect(0,12.46,D['front_width'],13.29),parapet_holes,cream,'lord',F)
for z in (12.48,13.31):box('Parapet horizontal cap',(D['front_width']/2,z,.015),(D['front_width'],.12,.40),white)
for u in (.20,6.22,D['front_width']-.20):box('Parapet pier',(u,12.90,.05),(.43,.84,.35),white)
if DETAIL:
 for hole in parapet_holes:
  u=sum(x for x,z in hole)/len(hole);m=Mesh('Fine roundel border');ring(m,u,12.91,.22,.22,.035,.015,.075,start=0,end=math.tau,n=24);finish(m,'lord',white,F)
# Nevill frontage: three monumental arched windows and two balcony tiers.
NW=Z-Y;holes=[]
for u in D['boots_bays']:holes.extend([rect(u-1.15,4.75,u+1.15,9.0),arch(u,10.05,13.50,1.15,1.22)])
holes.append(rect(NW/2-.95,15.78,NW/2+.95,16.28))
wall('Boots',rect(0,4.45,NW,17.1),holes,stone,'nevill',N)
for u in D['boots_bays']:
 for lo,hi,arched in [(4.75,9,False),(10.05,14.72,True)]:
  p=arch(u,lo,13.50,1.15,1.22) if arched else rect(u-1.15,lo,u+1.15,hi);panel('Boots glass',p,-.20,glass,'nevill',N)
  for dx in (-1.11,-.37,.37,1.11):
   top=13.5+1.22*math.sqrt(max(0,1-(dx/1.15)**2)) if arched else hi
   box('Boots mullions',(u+dx,(lo+top)/2,-.13),(.055,top-lo,.11),frame,'nevill',N)
  for z in ([lo+.04,12.91,13.50] if arched else [lo+.04,7.85,8.92]):box('Boots cross rails',(u,z,-.13),(2.3,.07,.11),frame,'nevill',N)
  if arched:
   arc('Boots window frame',u,13.5,1.09,1.16,.055,-.10,frame,'nevill',N)
   for rx,ry,t,out in [(1.15,1.22,.18,.20),(1.34,1.41,.07,.12)]:arc('Boots arch moulding',u,13.50,rx,ry,t,out,stone,'nevill',N)
  for dx in (-1.29,1.29):box('Boots window surround',(u+dx,(lo+13.5 if arched else lo+hi)/2,.11),(.22,(13.5 if arched else hi)-lo,.22),stone,'nevill',N)
  z=9.66 if arched else 4.53
  box('Boots balcony slab',(u,z,.39),(2.91,.22,1.05),stone,'nevill',N)
  for dx in (-1.20,1.20):
   m=Mesh('Boots carved balcony console');m.outline([(u+dx-.12,z-.85),(u+dx+.12,z-.85),(u+dx+.18,z-.13),(u+dx-.18,z-.13)],.01,.68);finish(m,'nevill',stone,N)
  # Distinct diamond railings have real holes at Detail and Walk.
  for zz in (z+.15,z+.89):tube('Boots balcony rails',[(u-1.38,zz,.91),(u+1.38,zz,.91)],.026,frame,'nevill',N)
  for j in range(4):
   xx=u-1.38+j*.92;tube('Boots balcony posts',[(xx,z+.14,.91),(xx,z+.91,.91)],.025,frame,'nevill',N)
  for j in range(3):
   a=u-1.38+j*.92;b=a+.92
   tube('Boots crossed rails',[(a,z+.18,.91),(b,z+.85,.91)],.018,frame,'nevill',N);tube('Boots crossed rails',[(b,z+.18,.91),(a,z+.85,.91)],.018,frame,'nevill',N)
  for dx in (-1.38,1.38):
   for zz in (z+.15,z+.89):tube('Boots balcony side rail',[(u+dx,zz,.12),(u+dx,zz,.91)],.025,frame,'nevill',N)
# Top central slot in high parapet, and recessed stone panels either side.
panel('Boots attic glass',rect(NW/2-.95,15.78,NW/2+.95,16.28),-.20,glass,'nevill',N)
for dx in (-.92,0,.92):box('Boots attic frames',(NW/2+dx,16.03,-.12),(.055,.50,.12),frame,'nevill',N)
for z,h,out in [(15.22,.13,.26),(15.42,.13,.40),(16.95,.15,.10),(17.1,.12,.18)]:box('Boots cornice',(NW/2,z,out/2),(NW,h,out),stone,'nevill',N)
for u in (1.95,8.83):
 for zz in (15.83,16.48):box('Boots parapet panel border',(u,zz,.025),(2.5,.065,.05),shade,'nevill',N)
 for xx in (u-1.22,u+1.22):box('Boots parapet panel edge',(xx,16.15,.025),(.065,.62,.05),shade,'nevill',N)
if DETAIL:
 for z in [4.65+i*.43 for i in range(29)]:
  for q in cuts(rect(.02,z-.005,NW-.02,z+.005),holes):panel('Fine Boots ashlar',q,.007,shade,'nevill',N)
 for u in D['boots_bays']:
  for dx in (-1.44,1.44):
   for j in range(5):box('Fine Boots arch voussoir',(u+dx,13.4-j*.22,.16),(.16,.035,.12),white,'nevill',N)
# Boot's carved heads and scroll-like balcony brackets are small, evidenced
# features. These are authored approximations, not claimed replicas of sculpture.
if DETAIL:
 for u in D['boots_bays']:
  for dx in (-1.42,1.42):
   m=Mesh('Fine Boots carved mask');m.lathe((u+dx,-.20),[(7.0,.07),(7.08,.13),(7.22,.12),(7.30,.06)],10);m.vertices=[(x,z,-y) for x,y,z in m.vertices];finish(m,'nevill',stone,N)
   for sign in (-1,1):tube('Fine mask brow',[(u+dx+sign*.025,7.21,.32),(u+dx+sign*.075,7.23,.31)],.017,shade,'nevill',N,6)
  for dx in (-1.20,1.20):
   for z in (4.53,9.66):
    pts=[]
    for j in range(24):
     t=j/23;pts.append((u+dx,z-.8+.65*t,.12+.48*t*t))
    tube('Fine balcony carved scroll',pts,.045,white,'nevill',N)
# Narrow rainwater pipes are visible at the boundary pilasters.
for M,part,x,top in [(F,'lord',.075,12.3),(F,'lord',D['front_width']-.075,12.3),(N,'nevill',.075,16.6)]:
 tube('Rainwater pipe',[(x,.35,.19),(x,top,.19)],.040,iron,part,M,10)
 for z in (2.5,5,7.5,10):box('Fine pipe collar',(x,z,.20),(.11,.05,.12),iron,part,M)

# Refurbished ground screens: fascia intentionally blank, not historical name.
for name,M,width,part in [('Lord',F,D['front_width'],'lord'),('Nevill',N,NW,'nevill')]:
 box('Shopfront recessed glazing',(width/2,2.15,-.15),(width-.34,3.90,.08),glass,part,M)
 box('Shopfront plinth',(width/2,.20,.015),(width,.40,.22),shop,part,M)
 box('Shopfront blank fascia',(width/2,4.12,.035),(width,.64,.27),wood if name=='Lord' else shop,part,M)
 n=9 if name=='Lord' else 7
 for j in range(n+1):
  x=.15+(width-.30)*j/n;box('Shopfront upright',(x,2.12,.025),(.105,3.8,.19),shop,part,M)
 for zz in (.40,3.50,3.78):box('Shopfront rail',(width/2,zz,.03),(width-.22,.085,.20),shop,part,M)
 # Central two door leaves are physically recessed another 8cm, with handles.
 for dx in (-.65,.65):
  for z in (.72,2.91):box('Shopfront door rail',(width/2+dx,z,.035),(1.05,.085,.21),shop,part,M)
  box('Shopfront handles',(width/2+dx*.22,1.55,.16),(.035,.68,.055),metal,part,M)
# Ground footprint and external walls; only uncovered upper-party faces are left plain.
outline=[(A,0),(W,0),(W,B),(R,B),(R,Z),(0,Z),(0,Y),(A,Y)]
# Front and Nevill skins above own their whole elevations.
boundaries=[((W,0),(W,9.5),12.3),((W,9.5),(W,Y),10.1),((W,Y),(W,Z),16.1),((W,Z),(W,48),14.25),((W,48),(W,B),17.1),((W,B),(R,B),17.1),((R,B),(R,48),17.1),((R,48),(R,Z),14.25),((R,Z),(0,Z),16.1),((0,Z),(0,Y),17.1),((0,Y),(A,Y),16.1),((A,Y),(A,9.5),10.1),((A,9.5),(A,0),12.3)]
# Rear tower windows and service apertures from Stanley view.
rear_holes=[rect(R+.85,6.5,R+2.1,8.3),rect(R+3.15,7.4,R+4.45,9.45),rect(R+.85,10.1,R+2.1,12.05),rect(R+3.15,10.95,R+4.45,12.85),rect(R+5.8,10.6,R+7.05,12.5),rect(R+.85,14.2,R+2.1,15.95),rect(R+3.15,14.8,R+4.45,16.35),rect(R+5.8,14.0,R+7.05,15.6)]
CM=face_matrix((0,Z,0),(0,1,0));SM=face_matrix((R,0,0),(-1,0,0))
court_holes=[rect(-14.9,z-1,-13.5,z+1) for z in (5.8,11.8)]
side_holes=[rect(-y-.85,5.3,-y+.85,7.2) for y in (40.5,44.8)]
rearM=Matrix(((1,0,0,0),(0,0,1,B),(0,1,0,0),(0,0,0,1)))
for a,b,h in boundaries:
 if a[0]==0 and b[0]==0:continue
 h-=.1202
 if a==(R,Z) and b==(0,Z):
  wall('courtyard backing lower',rect(-R,0,0,14.3),court_holes,paintbrick,'rear',CM)
  wall('courtyard backing upper',rect(-R,14.3,0,h),[],brick,'rear',CM);continue
 if a==(R,48) and b==(R,Z):
  wall('courtyard side lower',rect(-48,0,-Z,4.4),[],paintbrick,'rear',SM)
  wall('courtyard side upper',rect(-48,4.4,-Z,h),side_holes,brick,'rear',SM);continue
 if a[1]==B and b[1]==B:wall('Stanley service tower',rect(R,0,W,h),rear_holes,brick,'rear',rearM);continue
 m=Mesh('Shell wall external');m.add([(*a,0),(*b,0),(*b,h),(*a,h)],[(0,1,2,3)]);finish(m,'rear',paintbrick if a==(R,Z) else brick)
for i,p in enumerate(rear_holes):
 lo=min(z for x,z in p);hi=max(z for x,z in p);a=min(x for x,z in p);b=max(x for x,z in p);vent=i in (1,4)
 panel('Rear opening',p,-.12,black if vent else glass,'rear',rearM)
 box('Rear stone lintel',((a+b)/2,hi+.12,.03),(b-a+.3,.24,.14),stone,'rear',rearM);box('Rear sill',((a+b)/2,lo-.06,.06),(b-a+.20,.12,.25),shade,'rear',rearM)
 for dx in (a+.03,b-.03):box('Rear frames',(dx,(lo+hi)/2,-.065),(.06,hi-lo,.10),shop,'rear',rearM)
 for zz in (lo+.05,(lo+hi)/2,hi-.05):box('Rear cross bar',((a+b)/2,zz,-.04),(b-a,.055,.10),shop,'rear',rearM)
 if vent:
  for j in range(15):box('Rear vent louvres',((a+b)/2,lo+(hi-lo)*(j+.5)/15,.01),(b-a,.035,.075),iron,'rear',rearM)
 else:
  for j in range(7):box('Rear window bars',(a+(b-a)*(j+.5)/7,(lo+hi)/2,.07),(.018,hi-lo,.025),iron,'rear',rearM)
# Closed, nonoverlapping roof sections. Sloped Lord roof is hipped at both ends.
def slab(name,points,mat=lead):
 m=Mesh('Shell roof '+name);m.add(points,[tuple(range(len(points)))]);m.add([(x,y,z-.12) for x,y,z in points],[tuple(reversed(range(len(points))))])
 for a,b in zip(points,points[1:]+points[:1]):m.add([a,(a[0],a[1],a[2]-.12),(b[0],b[1],b[2]-.12),b],[(0,1,2,3)])
 return finish(m,'roof',mat)
e=D['front_eaves'];h=D['front_ridge'];depth=D['roof_front_depth'];hip=2.6;ridge=depth/2
roof_faces=[[(A,.245,e),(W,.245,e),(W-hip,ridge,h),(A+hip,ridge,h)],[(W,.245,e),(W,depth,e),(W-hip,ridge,h)],[(W,depth,e),(A,depth,e),(A+hip,ridge,h),(W-hip,ridge,h)],[(A,depth,e),(A,.245,e),(A+hip,ridge,h)]]
# A single closed roof avoids internal coplanar caps along hip seams.
m=Mesh('Shell roof Lord hip');v=[];fs=[]
for p in roof_faces:
 n=len(v);v.extend(p);fs.append(tuple(range(n,n+len(p))))
p=[(A,.245,e-.12),(A,depth,e-.12),(W,depth,e-.12),(W,.245,e-.12)];n=len(v);v.extend(p);fs.append(tuple(range(n,n+4)))
for a,b in zip([(A,.245),(W,.245),(W,depth),(A,depth)],[(W,.245),(W,depth),(A,depth),(A,.245)]):
 n=len(v);v.extend([(*a,e-.12),(*b,e-.12),(*b,e),(*a,e)]);fs.append(tuple(range(n,n+4)))
m.add(v,fs);finish(m,'roof',slate)
for name,x0,x1,y0,y1,zz in [('link',A,W,depth,Y,10.1),('Boots',.245,W,Y,Z,16.1),('rear service',R,W,Z,48,14.25),('rear tower',R,W,48,B,17.1)]:slab(name,[(x0,y0,zz),(x1,y0,zz),(x1,y1,zz),(x0,y1,zz)])
# Height-step walls belong to roof so no open faces appear when another part changes LoD.
for name,p in [('front back',[(A,depth,10.1),(W,depth,10.1),(W,depth,e-.12),(A,depth,e-.12)]),('Boots front',[(A,Y,10.1),(W,Y,10.1),(W,Y,15.98),(A,Y,15.98)]),('Boots rear',[(R,Z,14.25),(W,Z,14.25),(W,Z,15.98),(R,Z,15.98)]),('tower step',[(R,48,14.25),(W,48,14.25),(W,48,16.98),(R,48,16.98)])]:
 m=Mesh('Shell roof '+name);m.add(p,[(0,1,2,3)]);finish(m,'roof',brick)
# Flat roof perimeter parapet, large pyramidal lantern and service equipment.
for x0,x1,y0,y1,z0,z1 in [(W-.25,W,Y,Z,16.1,16.72),(.25,W-.25,Z-.25,Z,16.1,16.72),(.25,W-.25,Y,Y+.25,16.1,16.72),(R,R+.20,Z,B,14.25,14.70),(W-.20,W,Z,B,14.25,14.7)]:
 # Never extend low rear parapets through the higher end tower.
 if y1==B:y1=48
 box('Roof parapet',((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),brick,'roof',None)
rl=D['rooflight'];x0,x1=rl['x'];y0,y1=rl['y'];zz=rl['base'];ap=rl['apex'];cx=(x0+x1)/2;cy=(y0+y1)/2
box('Rooflight curb',(cx,cy,16.30),(x1-x0+.35,y1-y0+.35,.40),brick,'roof',None)
m=Mesh('Rooflight glazing');m.add([(x0,y0,zz),(x1,y0,zz),(x1,y1,zz),(x0,y1,zz),(cx,cy,ap)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]);finish(m,'roof',cglass)
for a,b in [((x0,y0,zz),(x1,y0,zz)),((x1,y0,zz),(x1,y1,zz)),((x1,y1,zz),(x0,y1,zz)),((x0,y1,zz),(x0,y0,zz))]:
 tube('Rooflight perimeter',[a,b],.045,metal,'roof',None)
 # Each corner-to-apex bar belongs to the edge starting at that corner.
 for j in range(4):
  t=j/4;p=tuple(a[k]*(1-t)+b[k]*t for k in range(3));tube('Rooflight glazing bar',[p,(cx,cy,ap)],.028,metal,'roof',None)
# Front chimney is clearly present behind the Lord parapet, with twin rows of pots.
lo,hi=chimney_bounds(D)
box('Roof chimney shaft',tuple((a+b)/2 for a,b in zip(lo,hi)),tuple(b-a for a,b in zip(lo,hi)),brick,'roof',None)
for zz in (14.6,16.0,16.72):box('Roof chimney course',(W-.60,6.9,zz),(1.25,1.75,.16),shade,'roof',None)
for dx in (-.29,.29):
 for dy in (-.52,0,.52):
  m=Mesh('Roof chimney pot');m.lathe((W-.60+dx,6.9+dy),[(16.78,.14),(17.25,.115),(17.30,.15),(17.40,.15)],12);finish(m,'roof',pot)
  box('Roof pot dark mouth',(W-.60+dx,6.9+dy,17.401),(.17,.17,.008),black,'roof',None)
for x,y in [(3,28),(3,30),(3,32)]:
 box('Roof cooling unit',(x,y,16.60),(1.0,1.15,1.0),metal,'roof',None)
 if DETAIL:
  for j in range(8):box('Fine cooling grille',(x-.506,y,16.23+j*.10),(.012,.85,.025),black,'roof',None)
# Discreet service fixtures, backed by aerial volumes; exact duct routes estimated.
box('Roof link plant',(18,18,10.70),(2.0,3.0,1.2),metal,'roof',None)
tube('Roof flue',[(16,13,10.1),(16,13,12.7),(17,13,12.7)],.18,metal,'roof',None,12)
# The observed court occupies local x11.3..17.1, not the concealed x5..7.
for z in (5.8,11.8):
 u=-14.2;w=1.4;h=2.0
 panel('Courtyard glazing',rect(u-w/2,z-h/2,u+w/2,z+h/2),-.12,glass,'rear',CM)
 for x in (u-w/2+.035,u+w/2-.035):box('Courtyard window jamb',(x,z,-.055),(.07,h,.10),frame,'rear',CM)
 for zz in (z-h/2+.035,z+h/2-.035):box('Courtyard window rail',(u,zz,-.055),(w-.14,.07,.10),frame,'rear',CM)
 for j in range(7):box('Courtyard bars',(u-w/2+(j+.5)*w/7,z,.08),(.025,h,.04),iron,'rear',CM)
 box('Courtyard sill',(u,z-h/2-.06,.12),(w+.18,.12,.24),shade,'rear',CM)
 box('Courtyard lintel',(u,z+h/2+.10,.06),(w+.18,.20,.12),stone,'rear',CM)
for y in (40.5,44.8):
 u=-y;panel('Courtyard vent recess',rect(u-.85,5.3,u+.85,7.2),-.14,black,'rear',SM)
 for j in range(17):box('Courtyard vent blade',(u,5.34+j*.108,-.045),(1.7,.035,.15),iron,'rear',SM)
 for zz in (5.24,7.3):box('Courtyard vent sill',(u,zz,.10),(1.85,.12,.20),shade,'rear',SM)
# Low white-clad shed below the backing windows. Attached rear skin omitted.
m=Mesh('Courtyard low shed')
for p in [[(12.1,Z,0.5),(12.1,Z+3.0,.5),(12.1,Z+3.0,3.0),(12.1,Z,3.2)],[(16.7,Z+3.0,.5),(16.7,Z,.5),(16.7,Z,3.2),(16.7,Z+3.0,3.0)],[(12.1,Z+3.0,.5),(16.7,Z+3.0,.5),(16.7,Z+3.0,3.0),(12.1,Z+3.0,3.0)]]:m.add(p,[(0,1,2,3)])
m.faces=[tuple(reversed(f)) for f in m.faces];finish(m,'rear',frame)
m=Mesh('Courtyard shed roof');m.add([(16.7,Z,3.2),(16.7,Z+3.0,3.0),(12.1,Z+3.0,3.0),(12.1,Z,3.2)],[(0,1,2,3)]);finish(m,'rear',lead)
for j in range(14):box('Fine courtyard cladding joint',(14.4,Z+3.015,.60+j*.17),(4.6,.015,.012),shade,'rear',None)
tube('Courtyard exhaust',[(16.2,Z+.30,.5),(16.2,Z+.30,6.8),(16.2,Z+.20,7.4)],.15,metal,'rear',None,12)
tube('Courtyard downpipe',[(13.05,Z+.08,.5),(13.05,Z+.08,13.8)],.045,iron,'rear',None,8)
# Check attachment/joinery prototypes before repeating them in exports.
# Canopies remain open, with cast-iron posts and scroll brackets.
for name,M,width in [('Lord',F,D['front_width']),('Nevill',N,NW)]:
 depth=3.02;inner=4.58;outer=3.68 if name=='Lord' else 4.00;fascia=outer-.17 if name=='Lord' else 3.25;positions=[.25,4.20,8.80,width-.22] if name=='Lord' else [.28,width-.28]
 m=Mesh('Canopy glazing '+name);m.add([(0,outer,depth),(width,outer,depth),(width,inner,.10),(0,inner,.10)],[(0,1,2,3)]);m.add([(0,inner-.035,.10),(width,inner-.035,.10),(width,outer-.035,depth),(0,outer-.035,depth)],[(0,1,2,3)]);finish(m,'canopy',cglass,M)
 for z,o in [(outer,depth),(inner,.10)]:box('Canopy perimeter rail',(width/2,z,o),(width,.13,.12),iron,'canopy',M)
 box('Canopy fascia',(width/2,fascia,depth),(width,.26,.10),iron,'canopy',M)
 n=round(width/.63)
 for j in range(n+1):tube('Canopy glazing bars',[(width*j/n,outer+.03,depth),(width*j/n,inner+.03,.10)],.027,iron,'canopy',M,4)
 if name=='Nevill':
  for j in range(n+1):box('Canopy frieze bars',(width*j/n,(3.38+outer)/2,depth),(.04,outer-3.38,.065),iron,'canopy',M)
 for u in positions:
  column('Canopy vase post',u,0,fascia-.08,.065,depth,iron,'canopy',M)
  for side in (-1,1):
   tube('Canopy structural bracket',[(u,outer-.45,depth),(u+side*.75,outer-.04,depth)],.026,iron,'canopy',M)
   if DETAIL:
    pts=[]
    for j in range(40):
     a=math.pi*2.8*j/39;r=.29*(1-j/45);pts.append((u+side*(.26+r*math.cos(a)),outer-.22+r*math.sin(a),depth))
    tube('Fine canopy scroll',pts,.015,iron,'canopy',M,6)
  if DETAIL:
   for j in range(6):tube('Fine post foliage',[(u+(j-2.5)*.025,outer-.25,depth+.06),(u+(j-2.5)*.045,outer-.12,depth+.07)],.018,iron,'canopy',M,6)
# Fine slate joints run across each roof slope; bounded topology only in Detail.
if DETAIL:
 for side in (0,1):
  for j in range(1,20):
   yy=D['roof_front_depth']*j/40
   z=e+(h-e)*yy/ridge;cut=hip*yy/ridge
   actual_y=yy if side==0 else D['roof_front_depth']-yy
   tube('Fine slate course',[(A+cut,actual_y,z+.008),(W-cut,actual_y,z+.008)],.007,shade,'roof',None,4)
# Named prototype audit covers each new courtyard shell/fitting interface.
import os
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender([o for o in s.objects if o.type=='MESH' and ('Courtyard' in o.name or 'courtyard' in o.name)])
# Semantic batching keeps bake source object count bounded.
families={}
for ob in list(s.objects):
 if ob.type!='MESH':continue
 kind='Courtyard shells' if ob.name.startswith('Shell wall courtyard') else 'Courtyard fittings' if ob.name.startswith(('Courtyard ','Fine courtyard')) else 'Rooflight bars' if ob.name.startswith('Rooflight glazing bar') else 'Fine' if ob.name.startswith('Fine ') else 'Shell' if ob.name.startswith('Shell ') else 'Architecture'
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
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
(ROOT/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/willow-grove.blend'))
