"""15–21 Anchor Street: measured four-premise terrace and stepped rear wings."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix
from southport3d.conform import conform
from components import rect,cuts,arc,moulding
from southport3d.geometry import text_object
D=json.loads((ROOT/'research/layout.json').read_text());DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('walls','roof','joinery'):
 C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,c,r=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;return m
brick=material('Warm red frontage brick',(.37,.16,.105));rear=material('Weathered rear brick',(.28,.19,.14));white=material('Painted ivory frames',(.79,.79,.73));glass=material('Opaque grey glazing',(.115,.16,.18),.28);slate=material('Blue grey slate',(.145,.17,.19));black=material('Recess and rainwater',(.035,.043,.049));blue=material('Number15 blue paint',(.025,.07,.15));stone=material('Pale stone sills',(.50,.47,.39))
for mat,name in [(brick,'front-brick'),(rear,'rear-brick'),(slate,'slate')]:
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures'/f'{name}.png'));tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
a=math.radians(D['rotation_degrees']);T=Matrix.Translation((*D['origin_site_xy'],D['base_z']))@Matrix.Rotation(a,4,'Z')
def finish(m,part='walls',mat=brick,frame=None):
 if m.name.startswith('Wall '):m=conform({'wall':m})[0]['wall']
 ob=m.finish([mat],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   if mat==slate:
    along=Vector((-p.normal.y,p.normal.x,0))
    if along.length<1e-6:along=Vector((1,0,0))
    along.normalize();slope=p.normal.cross(along).normalized()
    uv.data[li].uv=(v.dot(along)/2.4,v.dot(slope)/1.2)
   else:uv.data[li].uv=(v[axes[0]]/2.25,v[axes[1]]/.60) if mat in (brick,rear) else (v[axes[0]],v[axes[1]])
 ob.data.transform(T@(frame if frame is not None else Matrix.Identity(4)));return ob

def box(name,c,size,part='walls',mat=brick,frame=None):
 m=Mesh(name);m.box(c,size);return finish(m,part,mat,frame)

def wall(name,start,end,height,holes=(),bottom=0,mat=rear):
 dx=end[0]-start[0];dy=end[1]-start[1];w=math.hypot(dx,dy)
 # CCW plan edge: outward normal is right of its tangent.
 F=face_matrix((*start,0),(dy/w,-dx/w,0));m=Mesh('Wall '+name)
 for p in cuts(rect(0,bottom,w,height),holes):
  m.add([(u,z,0) for u,z in p],[tuple(range(len(p)))])
  m.add([(u,z,-.24) for u,z in p],[tuple(reversed(range(len(p))))])
 for hole in holes:
  for A,B in zip(hole,hole[1:]+hole[:1]):m.add([(*A,0),(*B,0),(*B,-.24),(*A,-.24)],[(0,1,2,3)])
 finish(m,mat=mat,frame=F);return F

def window(name,F,u,lo,hi,w=1.05,paint=white,split=None,sill=stone):
 box('Glazing '+name,(u,(lo+hi)/2,-.18),(w,hi-lo,.055),'joinery',glass,F)
 for x in (-w/2+.027,w/2-.027):box('Frame '+name,(u+x,(lo+hi)/2,-.075),(.054,hi-lo,.10),'joinery',paint,F)
 for z in (lo+.027,hi-.027,hi-min(.48,(hi-lo)*.24) if split is None else lo+(hi-lo)*split):box('Frame '+name,(u,z,-.065),(w-.06,.054,.10),'joinery',paint,F)
 if sill is not None:box('Sill '+name,(u,lo-.065,.07),(w+.16,.13,.29),'walls',sill,F)

W=D['width'];dep=D['main_depth'];H=D['parapet']
# Four premises, with paired upper axes and independent projecting shop bays.
upper=[];holes=[]
for j in range(4):
 for u in (j*5.2+1.35,j*5.2+3.85):
  for lo,hi in ((4.05,6.20),(7.25,8.95)):
   holes.append(rect(u-.525,lo,u+.525,hi));upper.append((u,lo,hi))
 # Shop bays and narrow entrance openings have genuine recesses.
 door=j*5.2+(4.65 if j<2 else .55)
 holes.append(rect(door-.43,0,door+.43,3.05))
 bay=j*5.2+(1.95 if j<2 else 3.05)
 holes.append(rect(bay-1.50,.42,bay+1.50,3.0))
F=wall('front',(0,0),(W,0),H,holes,mat=brick)
for i,(u,lo,hi) in enumerate(upper):window('front '+str(i),F,u,lo,hi,split=.5 if lo<5 or u>15.6 else .76,sill=blue if u>15.6 else stone)
for j in range(4):
 door=j*5.2+(4.65 if j<2 else .55);bay=j*5.2+(1.95 if j<2 else 3.05)
 box('Door recess '+str(j),(door,1.52,-.20),(.86,3.04,.055),'joinery',blue if j==3 else white if j==2 else black,F)
 # Exposed bay front and cheeks. Inner backing avoids an open void around glazing.
 for x in (bay-1.52,bay+1.52):box('Shop bay pier',(x,1.55,.22),(.24,3.10,.44),'walls',brick,F)
 box('Shop bay plinth',(bay,.32,.22),(3.28,.64,.44),'walls',brick,F)
 window('shop '+str(j),F,bay,.65,2.98,2.78,sill=None)
 # Window projects in front of main wall; shift its frame/glass family outward.
 for o in list(C['joinery'].objects):
  if ('shop '+str(j)) in o.name:o.data.transform(T@F@Matrix.Translation((0,0,.58))@(T@F).inverted())
 box('Shop fascia',(bay,3.10,.30),(3.50,.18,.65),'walls',blue if j==3 else black,F)
 m=Mesh('Roof shop canopy '+str(j));m.add([(bay-1.77,0,3.55),(bay+1.77,0,3.55),(bay+1.77,-.69,3.22),(bay-1.77,-.69,3.22)],[(0,3,2,1)]);finish(m,'roof',slate)
# Side walls with observed small side windows at number15.
sideholes=[rect(3.45,z,4.30,z+.90) for z in (4.45,7.25)]
Fr=wall('east main',(W,0),(W,dep),D['eaves'],sideholes)
for i,z in enumerate((4.45,7.25)):window('east main '+str(i),Fr,3.875,z,z+.90,.85)
wall('west main',(0,dep),(0,0),D['eaves'])
# Main rear skin is split around attachment volumes, preserving courtyard gaps.
attached=[rect(v['u'][0],0,v['u'][1],v['eaves']) for v in D['rear_volumes'] if v['v'][0]==dep]
# Rear face runs right-to-left, so opening coordinates are mirrored.
wall('main rear',(W,dep),(0,dep),D['eaves'],[[(W-x,z) for x,z in reversed(p)] for p in attached])
# Closed simple hipped main roof; source facets and District receiver share only dimensions.
def hip(name,x0,x1,y0,y1,eave,ridge,axis='x'):
 swap=axis=='y'
 if swap:x0,x1,y0,y1=y0,y1,x0,x1
 inset=min((x1-x0)*.28,(y1-y0)*.48);cy=(y0+y1)/2
 v=[(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave),(x0+inset,cy,ridge),(x1-inset,cy,ridge)]
 if swap:v=[(y,x,z) for x,y,z in v]
 f=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]
 if swap:f=[tuple(reversed(q)) for q in f]
 m=Mesh('Roof '+name);m.add(v,f)
 for i in range(4):
  j=(i+1)%4;p=[v[j],v[i],(v[i][0],v[i][1],eave-.18),(v[j][0],v[j][1],eave-.18)]
  m.add(p,[(3,2,1,0) if swap else (0,1,2,3)])
 finish(m,'roof',slate)
hip('main',0,W,0,dep,D['eaves'],D['ridge'])
for v in D['rear_volumes']:
 name=v['name'];x,X=v['u'];y,Y=v['v'];h=v['eaves']
 # Internal connecting end at y is omitted; other outside surfaces explicit.
 side=[]
 if name=='east paired upper wing':side=[rect(.30,6.55,1.12,8.55),rect(2.85,7.25,3.65,8.30),rect(1.20,3.65,2.05,5.15),rect(5.20,3.30,6.05,5.25)]
 if name=='east lower wing':side=[rect(1.05,4.05,1.90,5.35)]
 E=wall(name+' east',(X,y),(X,Y),h,side)
 for k,p in enumerate(side):
  lo=p[0][1];hi=p[2][1];u=(p[0][0]+p[1][0])/2;w=p[1][0]-p[0][0]
  if (name=='east paired upper wing' and k in (0,3)):box('Rear blue door '+str(k),(u,(lo+hi)/2,-.13),(w,hi-lo,.10),'joinery',blue,E)
  else:window(name+' '+str(k),E,u,lo,hi,w)
 wall(name+' north',(X,Y),(x,Y),h,bottom=6.5 if name=='east paired upper wing' else 0)
 wall(name+' west',(x,Y),(x,y),h)
 hip(name,x,X,y,Y,h,v['ridge'],axis='y')
# Main parapet top and back meet the roof; front is already owned by facade.
box('Parapet cap',(W/2,.12,H+.035),(W,.27,.07),'walls',brick)
# Front wall's back skin already owns the parapet rear face.
# Observed end/party chimney stacks, measured positions remain approximate.
for u in (.38,5.2,10.4,20.42):
 box('Chimney stack',(u,4.10,10.65),(.55,1.15,3.50),'roof',rear)
 box('Chimney cap',(u,4.10,12.43),(.68,1.29,.16),'roof',brick)

for x in (0,W):
 m=Mesh('Parapet end');m.add([(x,0,D['eaves']),(x,.24,D['eaves']),(x,.24,H),(x,0,H)],[(0,1,2,3) if x==W else (3,2,1,0)]);finish(m,mat=brick)
# Exposed white lower east return stops at the observed blue coping stripe.
box('Paint east ground return',(W+.012,dep/2,1.62),(.025,dep,3.24),'walls',white)
box('Paint east blue line',(W+.029,dep/2,3.27),(.027,dep,.09),'walls',blue)
for j in range(4):
 bay=j*5.2+(1.95 if j<2 else 3.05)
 for x in (bay-1.77,bay+1.77):
  m=Mesh('Shop canopy cheek');m.add([(x,0,3.55),(x,-.69,3.22),(x,0,3.22)],[(0,1,2)]);finish(m,'roof',black)
 box('Shop projecting sill',(bay,.58,.34),(3.18,.14,.72),'walls',blue if j==3 else black,F)
 if j==3:
  for du in (-.47,.47):box('Shop15 mullion',(bay+du,1.815,.50),(.055,2.33,.10),'joinery',white,F)
# Wall bands are shallow brick courses; sills remain locally white or blue.
for z,h in [(3.88,.10),(7.12,.11),(9.65,.10)]:box('Brick string course',(W/2,z,.012),(W,h,.025),'walls',rear,F)
for i,(u,lo,hi) in enumerate(upper):
 # Low segmental gauged brick arch, one continuous ring with real radial joints.
 m=Mesh('Trim window lintel');arc(m,u,hi-.01,.55,.075,.23,out=.045,depth=.065,steps=20);finish(m,mat=brick,frame=F)
# Simple panels, handles and fanlights distinguish door from an opaque void.
for j in range(4):
 u=j*5.2+(4.65 if j<2 else .55);paint=blue if j==3 else white if j==2 else black
 for x in (-.45,.45):box('Door jamb',(u+x,1.55,.015),(.09,3.10,.10),'walls',stone if j==3 else brick,F)
 box('Door fanlight',(u,2.77,-.13),(.77,.42,.05),'joinery',glass,F)
 for z in (() if j==2 else (.40,1.05,1.7,2.35)):
  for x in (-.19,.19):box('Door panel',(u+x,z,-.135),(.29,.49,.035),'joinery',paint,F)
 box('Door handle',(u+.25,1.1,-.08),(.025,.14,.065),'joinery',stone,F)
# Drainpipes are placed at visible unit joints and end returns.
for u in (.09,5.2,10.4,20.72):
 box('Rainwater front pipe',(u,4.87,.07),(.075,9.6,.09),'walls',black,F)
 for z in (1,3.6,6.5,9.2):box('Fine pipe clip',(u,z,.10),(.12,.045,.10),'walls',black,F)
# Main end stacks and rear stacks have actual pots, rather than bare blocks.
for u in (.38,5.2,10.4,20.42):
 for v in (3.78,4.10,4.42):
  m=Mesh('Chimney terracotta pot');m.lathe((u,v),[(12.50,.105),(12.87,.095),(12.91,.12),(12.98,.12)],16);finish(m,'roof',brick)
for u,v,z in [(4.95,11.3,10.9),(15.60,10.7,10.9)]:
 box('Rear chimney',(u,v,z),(.63,1.03,1.10),'roof',rear)
 box('Rear chimney coping',(u,v,z+.60),(.76,1.16,.12),'roof',brick)
 for dy in (-.31,0,.31):
  m=Mesh('Rear chimney pot');m.lathe((u,v+dy),[(z+.66,.10),(z+1.00,.09),(z+1.04,.12)],16);finish(m,'roof',brick)
# A connected open steel stair runs from the first-floor rear landing to the
# second-floor side door. Dimensions estimated from S03, not a ground stair.
steel=material('Weathered black steel',(.075,.085,.09));x=19.32;v0=14.0;v1=8.65;z0=3.30;z1=6.55;n=19
m=Mesh('Escape stair treads')
for k in range(n):
 v=v0+(v1-v0)*(k+.5)/n;z=z0+(z1-z0)*(k+1)/n;m.box((x,v,z-.025),(.96,abs(v1-v0)/n+.01,.05))
finish(m,'joinery',steel)
for v,z in [(v0,z0),(v1,z1)]:box('Escape stair landing',(x,v,z-.045),(1.02,.8,.09),'joinery',steel)
def rod(name,a,b,r=.025,part='joinery'):
 direction=Vector(b)-Vector(a);m=Mesh(name);m.box((0,0,direction.length/2),(r*2,r*2,direction.length));frame=Matrix.Translation(a)@direction.to_track_quat('Z','Y').to_matrix().to_4x4();finish(m,part,steel,frame)
for xx in (x-.46,x+.46):
 rod('Stair stringer',(xx,v0,z0-.12),(xx,v1,z1-.12),.07)
 rod('Stair handrail',(xx,v0,z0+1),(xx,v1,z1+1),.025)
 for k in range(0,n+1,3):
  v=v0+(v1-v0)*k/n;z=z0+(z1-z0)*k/n;rod('Stair baluster',(xx,v,z),(xx,v,z+1),.018)
# Readable identifying text is authored, without copying photographic artwork.
def label(name,body,u,z,out,height,width,mat=white):
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
 ob=text_object('Sign '+name,body,(0,0,0),(0,0,1),height,width,font,mat,extrude=.003,collection=C['joinery'],fit_bounds=True)
 local=Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(T@F@local);ob.matrix_world=Matrix.Identity(4)
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='Sign UV')
label('15','15',16.15,2.33,-.072,.14,.22)
# Gold lettering is on the recessed white spa door in the auction photograph.
gold=material('Spa gold lettering',(.70,.49,.17));bay=13.45
label('spa','Thai',10.95,2.40,-.162,.13,.48,gold)
label('spa house','House',10.95,2.24,-.162,.13,.55,gold)
label('spa massage','SPA',10.95,2.08,-.162,.12,.36,gold)

# Batch material-compatible source families before selected-to-active baking.
# Hundreds of tiny objects otherwise repeat Cycles setup for every atlas pass.
groups={}
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH':continue
 family='Wall exterior' if ob.name.startswith('Wall ') else 'Fine details' if ob.name.startswith('Fine ') else 'Architecture'
 groups.setdefault((ob.users_collection[0].name,family),[]).append(ob)
for (part,family),objects in groups.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=family+' '+part

s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.4,-.5);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/terrace-15-21.blend'))
