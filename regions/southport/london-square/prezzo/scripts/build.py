"""Observed street elevations; rear envelope and dimensions remain estimates."""
import bpy,sys,os,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'));sys.path.insert(0,str(ROOT/'scripts'))
from southport3d.geometry import Mesh,face_matrix,text_object
from components import window,pilaster,rectangle_frame
from surface_cleanup import clean
from detail import coursed_surface,rusticated_corner,arch_stones,architrave,cornice_ring,london_menu_stonework
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
C={}
for name in ['architecture','roof','shopfront']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);C[name]=c

def material(name,color,texture=None,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
wallstone=material('Coursed wall at reduced levels',(.57,.55,.50),'stone');stone=material('Pale weathered stone',(.57,.55,.50),'ashlar0');trim=material('Pale painted sash',(.76,.75,.69));glass=material('Opaque blue grey glazing approximation',(.09,.12,.125),rough=.27);slate=material('Slate roof',(.12,.15,.17),'slate');lead=material('Flat roof weathering',(.17,.18,.18));dark=material('Dark entrance joinery',(.025,.027,.027));white=material('Lettering',(.86,.85,.77));red=material('Terracotta chimney pots',(.34,.12,.075));brick=material('Rear masonry estimate',(.26,.18,.14));base=material('Dark stone plinth',(.20,.21,.20))
mats=[stone,trim,glass,dark,white]
shopglass=material('Dark restaurant glazing',(.018,.025,.027),rough=.30)
shopmats=[stone,trim,shopglass,dark,white]
# Detail blocks use unjointed stone variation; their actual edges define the joints.
ashlar=[material('Ashlar tone '+str(i),(.60+i*.009,.58+i*.009,.53+i*.009),'ashlar'+str(i)) for i in range(4)]
brass=material('Warm door hardware',(.38,.29,.13),rough=.30)
lantern=material('Lantern pale glazing',(.61,.51,.29),rough=.35)

def finish(m,part='architecture',materials=None,matrix=None):
 o=m.finish(materials or [stone],C[part])
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 if not m.name.startswith(('Stonework ','Roof mansard')):o['coplanar_faces_resolved']=clean(o.data)
 uv=o.data.uv_layers.new(name='Metric repeat')
 for f in o.data.polygons:
  axes=sorted(range(3),key=lambda i:abs(f.normal[i]))[:2]
  for i in f.loop_indices:
   v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v[axes[0]]/3.6,v[axes[1]]/1.8)
 if matrix is not None:o.matrix_world=matrix
 return o

prototypes={}
def instance(key,mesh,part,matrix,materials=None):
 if key not in prototypes:ob=finish(mesh,part,materials or mats,matrix);prototypes[key]=ob
 else:
  ob=prototypes[key].copy();ob.data=prototypes[key].data;C[part].objects.link(ob);ob.name=mesh.name;ob.matrix_world=matrix
 return ob

z0=D['base_z'];top=15.6
# Local facade X increases to the viewer's right, Y is height, Z points outward.
def elevation(label,a,b,centres):
 normal=Vector((b[1]-a[1],a[0]-b[0],0)).normalized();length=math.dist(a,b);frame=face_matrix((a[0],a[1],z0),normal)
 if label=='Lord Street':frame=frame@Matrix.Diagonal((17.6/19.2,1,1,1))
 def fbox(mesh,u,y,w,h,d=.45,out=-.225):mesh.box((u,y,out),(w,h,d))
 shell=Mesh('Envelope '+label)
 openings=[]
 levels=[(.64,5.3,.70,4.75,2.45),(5.3,9.0,6.0,8.35,1.28),(9.0,12.4,9.65,11.8,1.28),(12.4,15.6,13.1,14.7,1.28)]
 for floor,(low,high,sill,head,width) in enumerate(levels):
  if label=='London Street' and floor==0:width=3.2
  fbox(shell,length/2,(low+sill)/2,length,sill-low)
  fbox(shell,length/2,(head+high)/2,length,high-head)
  previous=0
  for u in ([2.8,10.0] if label=='London Street' and floor==0 else centres):
   # The bay away from the corner is a shorter, raised-sill shop window.
   sill=1.55 if label=='London Street' and floor==0 and u==2.8 else levels[floor][2]
   if sill>low and label=='London Street' and floor==0 and u==2.8:
    fbox(shell,u,(.70+sill)/2,width,sill-.70)
   if u-width/2>previous:fbox(shell,(previous+u-width/2)/2,(levels[floor][2]+head)/2,u-width/2-previous,head-levels[floor][2])
   previous=u+width/2
   style=('shop-london-raised' if u==2.8 else 'shop-london') if label=='London Street' and floor==0 else 'shop' if floor==0 else ['','lower','middle','upper'][floor]
   openings.append((u-width/2-.015,sill-.015,u+width/2+.015,head+.015))
   matrix=frame@Matrix.Translation((u,(sill+head)/2,0))
   instance(style,window(width,head-sill,'detail','Window '+style+' '+label,shop_override=floor==0,raised_shop=style=='shop-london-raised',apron_window=floor==1), 'shopfront' if floor==0 else 'architecture',matrix,shopmats if floor==0 else mats)
   # Stone architraves remain real geometry around the receiving window panels.
   trimmesh=Mesh('Dressings '+label)
   for x in [u-width/2-.105,u+width/2+.105]:fbox(trimmesh,x,(sill+head)/2,.15,head-sill+.25,.12,.025)
   fbox(trimmesh,u,head+.10,width+.36,.16,.20,.06)
   if floor==1:
    fbox(trimmesh,u,head+.26,.24,.35,.22,.11)
   finish(trimmesh,'architecture',[stone],frame)
   if floor:
    instance('architrave-'+str(floor),architrave(width,head-sill,'Ornament architrave '+label,sill=floor!=1),'architecture',matrix,[stone])
    if floor==1:
     key=Mesh('Ornament carved keystone '+label)
     key.add([(-.14,head+.05,.10),(.14,head+.05,.10),(.10,head+.46,.10),(-.10,head+.46,.10),(-.12,head+.07,.23),(.12,head+.07,.23),(.08,head+.43,.23),(-.08,head+.43,.23)],[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
     for side0 in [-1,1]:
      key.tube([(side0*(.05+.025*math.sin(t)),head+.22+.13*math.cos(t),.25) for t in [j*math.pi/16 for j in range(17)]],.013,0,6)
     finish(key,'architecture',[stone],frame@Matrix.Translation((u,0,0)))
  if previous<length:fbox(shell,(previous+length)/2,(sill+head)/2,length-previous,head-sill)
 if label=='London Street':
  # Actual shallow pockets, not raised boxes pretending to be recesses.
  for u,cy,w,h in [(6.45,2.18,.84,1.68),(6.45,.99,.94,.67),(2.8,1.05,2.72,.62)]:
   shell.cut_box_from_ashlar((u,cy,-.025),(w,h,.25))
   openings.append((u-w/2,cy-h/2,u+w/2,cy+h/2))
 # First-storey sash surrounds continue as shallow inset aprons to the belt.
 for u in centres:
  shell.cut_box_from_ashlar((u,5.73,-.025),(1.35,.54,.25))
  openings.append((u-.675,5.46,u+.675,6.0))
  apron=Mesh('Dressings first floor inset '+label)
  apron.box((u,5.73,-.135),(1.35,.54,.025))
  for x in [u-.755,u+.755]:apron.box((x,5.76,.025),(.08,.69,.10))
  apron.box((u,5.445,.025),(1.59,.06,.10))
  finish(apron,'architecture',[stone],frame)
 finish(shell,'architecture',[wallstone],frame)
 finish(coursed_surface(length,openings,'Stonework '+label),'architecture',ashlar,frame)
 # Main cornices are swept once around the corner below.
 fine=Mesh('Dentils '+label)
 for u in [i*.30+.12 for i in range(int(length/.30))]:
  for y in [5.23,15.29]:fbox(fine,u,y,.13,.16,.22,.20)
 finish(fine,'architecture',[stone],frame)
 # Rusticated terminal strips, and the shop's fluted Ionic pilasters.
 quoins=Mesh('Quoins '+label)
 for u in [.25,length-.25]:
  for i in range(24):fbox(quoins,u,5.75+i*.39,.48,.35,.10,.025)
 finish(quoins,'architecture',[stone],frame)
 for u in ([.43,4.93,7.87,length-.43] if label=='London Street' else [.43]+[(a+b)/2 for a,b in zip(centres,centres[1:])]+[length-.43]):
  instance('pilaster',pilaster('detail','Pilaster '+label),'shopfront',frame@Matrix.Translation((u,.76,0)),[stone])
 pl=Mesh('Envelope plinth '+label);fbox(pl,length/2,.32,length,.64,.54,-.21)
 finish(pl,'architecture',[base],frame)
 return frame,length

front,flen=elevation('Lord Street',(-12.8,-23.4),(-32,-23.4),[2.05,5.8,9.55,13.3,17.05])
side,slen=elevation('London Street',(-9.6,-39.0),(-9.6,-26.1),[2.35,6.45,10.55])
m=Mesh('Dressings London recessed panels')
for u,cy,w,h in [(6.45,2.18,.84,1.68),(6.45,.99,.94,.67),(2.8,1.05,2.72,.62)]:
 m.box((u,cy,-.135),(w,h,.025),0)
 rectangle_frame(m,u,cy,w+.16,h+.16,.08,.025,.10,0)
 rectangle_frame(m,u,cy,w-.035,h-.035,.035,-.052,.08,0)
# Blank dark menu and lower display: no fabricated unreadable copy.
m.box((6.45,2.18,-.065),(.46,1.40,.045),3)
m.box((6.45,.99,-.065),(.49,.43,.045),3)
finish(m,'shopfront',mats,side)
finish(london_menu_stonework(),'architecture',[stone],side@Matrix.Translation((6.45,3.88,0)))
# Chamfered entrance corner, with a true arched opening and upper windows.
a=(-9.6,-26.1);b=(-12.8,-23.4);normal=Vector((b[1]-a[1],a[0]-b[0],0)).normalized();L=math.dist(a,b);corner=face_matrix((*a,z0),normal)
m=Mesh('Envelope corner');doorw=1.65;spring=3.35;radius=doorw/2
for lo,hi in [(0,(L-doorw)/2),((L+doorw)/2,L)]:m.box(((lo+hi)/2,2.65,-.225),(hi-lo,5.3,.45))
# Fill the spandrel with exact curved lower edges; adjacent strips only share edges.
for i in range(48):
 x=-radius+doorw*i/48;xx=-radius+doorw*(i+1)/48
 h=spring+math.sqrt(max(0,radius*radius-x*x));hh=spring+math.sqrt(max(0,radius*radius-xx*xx))
 verts=[(L/2+x,h,0),(L/2+xx,hh,0),(L/2+xx,5.3,0),(L/2+x,5.3,0)]
 m.add(verts,[(0,1,2,3)])
finish(m,'shopfront',[stone],corner)
# Black double doors with a deep reveal, rails, kickplates and arched fanlight.
m=Mesh('Entrance corner');m.box((L/2,1.65,-.20),(doorw,3.3,.035),3)
for x in [-doorw/4,doorw/4]:
 rectangle_frame(m,L/2+x,1.65,doorw/2-.02,3.3,.10,-.10,.12,3)
 m.box((L/2+x,1.82,-.14),(.57,2.32,.02),2)
 m.box((L/2+x,.28,-.03),(.62,.28,.025),3)
for y in [.49,3.28]:m.box((L/2,y,-.04),(doorw,.10,.12),3)
pts=[(L/2+radius*math.cos(i*math.pi/48),spring+radius*math.sin(i*math.pi/48),-.13) for i in range(49)]
m.add(pts,[tuple(range(len(pts)))],3)
finish(m,'shopfront',shopmats,corner)
finish(arch_stones(L/2,spring,radius+.035,radius+.28),'shopfront',[stone],corner)
m=Mesh('Ornament arch mouldings')
for r,d,thickness in [(radius+.015,.055,.025),(radius+.075,.18,.018)]:
 m.tube([(L/2+r*math.cos(i*math.pi/64),spring+r*math.sin(i*math.pi/64),d) for i in range(65)],thickness,0,8)
finish(m,'shopfront',[stone],corner)
m=Mesh('Hardware entrance handles')
for x in [-.10,.10]:m.tube([(L/2+x,1.17,.005),(L/2+x,1.85,.005)],.022,0,10)
finish(m,'shopfront',[brass],corner)
# Corner upper wall strips around three real openings.
corner_width=1.45;corner_pier=(L-corner_width)/2
for low,high,sill,head in [(5.3,9,6,8.35),(9,12.4,9.65,11.8),(12.4,15.6,13.1,14.7)]:
 m=Mesh('Envelope corner upper')
 for x in [corner_pier/2,L-corner_pier/2]:m.box((x,(low+high)/2,-.225),(corner_pier,high-low,.45))
 for aa,bb in [(low,sill),(head,high)]:m.box((L/2,(aa+bb)/2,-.225),(corner_width,bb-aa,.45))
 if low==5.3:m.cut_box_from_ashlar((L/2,5.73,-.025),(corner_width+.06,.54,.25))
 finish(m,'architecture',[stone],corner)
 style='corner-'+str(low);instance(style,window(corner_width,head-sill,'detail','Window corner '+str(low),apron_window=low==5.3),'architecture',corner@Matrix.Translation((L/2,(sill+head)/2,0)))
apron=Mesh('Dressings corner first floor inset')
apron.box((L/2,5.73,-.135),(corner_width+.06,.54,.025))
for x in [L/2-corner_width/2-.11,L/2+corner_width/2+.11]:apron.box((x,5.76,.025),(.08,.69,.10))
apron.box((L/2,5.445,.025),(corner_width+.30,.06,.10))
finish(apron,'architecture',[stone],corner)
corner_openings=[(L/2-corner_width/2-.03,5.46,L/2+corner_width/2+.03,6.0)]+[(L/2-.79,lo-.04,L/2+.79,hi+.06) for lo,hi in [(6,8.35),(9.65,11.8),(13.1,14.7)]]
finish(rusticated_corner(L,corner_openings,spring,radius+.28),'architecture',[stone],corner)
for sill,head in [(6,8.35),(9.65,11.8),(13.1,14.7)]:
 finish(architrave(corner_width,head-sill,'Ornament corner surround',sill=sill!=6),'architecture',[stone],corner@Matrix.Translation((L/2,(sill+head)/2,0)))
# Segmental pediment hood and its two projecting console supports.
m=Mesh('Dressings corner hood')
for r,zc,depth,rad in [(1.10,8.54,.20,.07),(1.18,8.57,.25,.055)]:
 m.tube([(L/2+r*math.cos(t),zc+.38*math.sin(t),depth) for t in [i*math.pi/48 for i in range(49)]],rad,0,8)
m.box((L/2,8.51,.18),(2.36,.12,.32))
for x in [L/2-.96,L/2+.96]:
 m.box((x,8.24,.14),(.16,.42,.24));m.box((x,8.42,.20),(.25,.09,.35))
finish(m,'architecture',[stone],corner)
# Mitred cornice profiles share corner vertices instead of overlapping end faces.
for name,profile in [('lower',[(5.10,-.08),(5.10,.10),(5.17,.10),(5.17,.24),(5.26,.24),(5.30,.34),(5.39,.38),(5.47,.49),(5.56,.49),(5.58,-.08)]),('upper',[(15.05,-.08),(15.05,.13),(15.15,.13),(15.23,.28),(15.34,.35),(15.44,.50),(15.60,.65),(15.73,.65),(15.75,-.08)])]:
 finish(cornice_ring(D['footprint'],z0,profile,'Cornice continuous '+name),'architecture',[stone])
# Small moulded brackets beneath the eaves; separate Detail-only interpretation.
for frame,length in [(front,flen),(side,slen),(corner,L)]:
 m=Mesh('Ornament eaves consoles')
 for i in range(int(length/.64)):
  u=(i+.5)*length/int(length/.64)
  m.box((u,15.05,.20),(.16,.28,.30))
  m.tube([(u,14.94,.15),(u,15.0,.25),(u,15.13,.32),(u,15.20,.28)],.055,0,8)
 finish(m,'architecture',[stone],frame)
# Simple party/rear envelopes explicitly not researched as finished elevations.
m=Mesh('Envelope rear estimate');m.box((-20.0,-38.75,z0+7.8),(20.8,.45,15.6));m.box((-30.4,-31.425,z0+7.8),(.45,15.15,15.6));finish(m,materials=[brick])
# Mansard only on the three street faces; flat-ended party/rear gables.
poly=D['footprint']
# Parallel inset edges keep the chamfer planar and every eave at the same pitch.
inner=[]
for i,p in enumerate(poly):
 before=Vector(poly[i-1]);here=Vector(p);after=Vector(poly[(i+1)%len(poly)])
 t0=(here-before).normalized();t1=(after-here).normalized()
 n0=Vector((-t0.y,t0.x));n1=Vector((-t1.y,t1.x))
 offset=(n0+n1)*(1.8/(1+n0.dot(n1)))
 inner.append(tuple(here+offset))
# Rear and party boundaries meet vertical end walls instead of hip slopes.
inner[0]=(-30.4,-39);inner[1]=(inner[1][0],-39);inner[4]=(-30.4,inner[4][1])
m=Mesh('Roof mansard')
for i,a in enumerate(poly):
 if i not in (1,2,3):continue
 j=(i+1)%len(poly);b=poly[j];aa=inner[i];bb=inner[j]
 m.add([(a[0],a[1],z0+15.7),(b[0],b[1],z0+15.7),(bb[0],bb[1],z0+18.3),(aa[0],aa[1],z0+18.3)],[(0,1,2,3)])
m.add([(x,y,z0+18.3) for x,y in inner],[tuple(range(len(inner)))],1)
roof=finish(m,'roof',[slate,lead])
# Per-face eave/slope coordinates, independent of triangulation or world axes.
# The old dominant-axis projection turned courses vertically on the chamfer.
for f in roof.data.polygons:
 if f.material_index:continue
 tangent=Vector((-f.normal.y,f.normal.x,0)).normalized()
 for li in f.loop_indices:
  v=roof.data.vertices[roof.data.loops[li].vertex_index].co
  roof.data.uv_layers.active.data[li].uv=(v.dot(tangent)/2.4,(v.z-z0-15.7)*math.hypot(1.8,2.6)/2.6/2.4)
# Visible party gable above the lower neighbouring terrace, and vertical rear
# end. Heights are calibrated to the existing eave/deck, not surveyed.
m=Mesh('Roof end gables')
m.add([(-30.4,y,z0+z) for y,z in [(-39,15.6),(-23.4,15.6),(-23.4,15.7),(-25.2,18.3),(-39,18.3)]],[(4,3,2,1,0)])
m.add([(x,-39,z0+z) for x,z in [(-30.4,15.6),(-9.6,15.6),(-9.6,15.7),(-11.4,18.3),(-30.4,18.3)]],[(0,1,2,3,4)])
finish(m,'roof',[brick])
# Dormer cheeks, frames and flat lead caps; front and London counts corroborated.
for label,frame,centres in [('Lord',front,[2.05,5.8,9.55,13.3,17.05]),('London',side,[2.35,6.45,10.55]),('corner',corner,[L/2])]:
 for u in centres:
  t=frame@Matrix.Translation((u,17.0,-.22));m=Mesh('Roof dormer '+label)
  # Wedge cheeks meet the slate plane, and front frames stand ahead of it.
  for xx in [-.75,.75]:
   x0,x1=xx-.075,xx+.075
   verts=[(x,y,out) for x in [x0,x1] for y,out in [(-.80,.02),(.80,.02),(.80,-1.24),(-.80,-.126)]]
   m.add(verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
  for yy in [-.75,.75]:m.box((0,yy,-.035),(1.35,.10,.14))
  m.box((0,.87,-.61),(1.88,.13,1.47));finish(m,'roof',[stone],t)
  instance('dormer',window(1.35,1.30,'detail','Window dormer '+label),'roof',t@Matrix.Translation((0,0,.04)))
  flashing=Mesh('Ornament dormer flashing');flashing.box((0,.945,-.61),(1.92,.025,1.51));flashing.box((0,-.83,-.015),(1.80,.04,.23));finish(flashing,'roof',[lead],t)
# Chimneys and terracotta pot groups; rear service structure is an estimated envelope.
# Daylight aerial: larger access/headhouse with pale rendered street-facing
# walls, flat coping and sash openings. Exact function/hidden faces unresolved.
access=face_matrix((-20.5,-32.7,z0+18.3),(0,1,0))
m=Mesh('Roof access enclosure')
m.box((3.5,1.3,-2.5),(7,2.6,5))
for u in [2.0,5.0]:m.cut_box_from_ashlar((u,1.35,.0),(1.0,1.5,.65))
finish(m,'roof',[stone],access)
for u in [2.0,5.0]:instance('access-sash',window(.90,1.40,'detail','Window roof access'),'roof',access@Matrix.Translation((u,1.35,.01)))
m=Mesh('Roof access coping');m.box((3.5,2.65,-2.5),(7.2,.13,5.2));finish(m,'roof',[lead],access)
m=Mesh('Hardware roof access vent');rectangle_frame(m,0,0,.60,.45,.035,.015,.04,0)
for y in [-.15,-.075,0,.075,.15]:m.box((0,y,.04),(.53,.025,.06))
finish(m,'roof',[dark],access@Matrix.Translation((.6,.7,.02)))
for spec in D['chimneys']:
 x,y=spec['centre'];length=spec['length'];width=spec['width']
 matrix=Matrix.Translation((x,y,z0))@Matrix.Rotation(math.radians(spec['yaw_degrees']),4,'Z')
 m=Mesh('Roof chimney '+spec['id'])
 m.box((0,0,18.55),(length,width,2.7))
 m.box((0,0,19.91),(length+.18,width+.18,.16))
 finish(m,'roof',[stone],matrix)
 # Dark weathered coping and hollow, collared terracotta pots.
 m=Mesh('Roof coping '+spec['id']);m.box((0,0,20.005),(length+.22,width+.22,.07));finish(m,'roof',[lead],matrix)
 if spec['pots']:
  m=Mesh('Pots '+spec['id']);count=spec['pots']
  for j in range(count):
   u=(j-(count-1)/2)*(length-.30)/(count-1)
   m.lathe((u,0),[(20.04,.12),(20.14,.12),(20.16,.10),(21.12,.095),(21.15,.115),(21.22,.115),(21.22,.075),(20.96,.075)],12)
  finish(m,'roof',[red],matrix)
# One authored text prototype, projected onto a panel at distant LOD.
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
t=text_object('Temporary lettering','PREZZO',(0,0,.035),(0,0,1),.20,1.1,font,white)
bpy.context.view_layer.objects.active=t;t.select_set(True);bpy.ops.object.convert(target='MESH')
m=Mesh('Sign PREZZO');m.box((0,0,0),(1.35,.31,.025),3)
m.add([tuple(t.matrix_world@v.co) for v in t.data.vertices],[tuple(f.vertices) for f in t.data.polygons],4);bpy.data.objects.remove(t,do_unlink=True)
instance('sign',m,'shopfront',corner@Matrix.Translation((L/2,3.75,.08)))
for frame,us in [(front,[2.05,9.55,17.05]),(side,[2.8,10.0])]:
 for u in us:instance('sign',Mesh('Sign PREZZO transom'),'shopfront',frame@Matrix.Translation((u,4.40,.10)))
from frontage_detail import add_frontage
add_frontage(finish,front,side,corner,flen,slen,L,shopmats,brass,lantern,ROOT)
from end_bays import add_end_bays
add_end_bays(finish,instance,z0,mats)
# Remove ground-contact undersides; these overlap at joined wall corners and
# the scene already has a separate walkable pavement asset.
import bmesh
for ob in [o for o in scene.objects if o.type=='MESH']:
 if ob.data.users>1:continue
 bm=bmesh.new();bm.from_mesh(ob.data)
 dead=[f for f in bm.faces if all(abs((ob.matrix_world@v.co).z-z0)<1e-5 for v in f.verts) and (ob.matrix_world.to_3x3()@f.normal).z<-.99]
 if dead:bmesh.ops.delete(bm,geom=dead,context='FACES');bm.to_mesh(ob.data);ob.data.update()
 bm.free()
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.70,.75,1);bg.inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;o=bpy.data.objects.new('Sun',sun);scene.collection.objects.link(o);o.rotation_euler=(-.6,.6,0)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.location=(18,5,25);cam.rotation_euler=(Vector((-20,-30,10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=36
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/prezzo.blend'))
