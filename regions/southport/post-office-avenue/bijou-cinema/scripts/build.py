"""Bijou Cinema: photographically measured frontage and traced compound footprint."""
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

def window(name,F,u,lo,hi,w=1.05,paint=white):
 box('Glazing '+name,(u,(lo+hi)/2,-.18),(w,hi-lo,.055),'joinery',glass,F)
 for x in (-w/2+.027,w/2-.027):box('Frame '+name,(u+x,(lo+hi)/2,-.075),(.054,hi-lo,.10),'joinery',paint,F)
 for z in (lo+.027,hi-.027,(lo+hi)/2):box('Frame '+name,(u,z,-.065),(w-.06,.054,.10),'joinery',paint,F)
 box('Sill '+name,(u,lo-.065,.07),(w+.16,.13,.29),'walls',stone,F)

from components import ellipse_arch
W=D['front_width'];H=D['eaves'];u=D['door_u'];poly=D['footprint_uv']
archbrick=material('Gauged red entrance brick',(.40,.12,.065));doortrim=material('Black door mouldings',(.065,.075,.075))
cream=material('Warm painted stone',(.68,.63,.50));red=material('Bijou burgundy signs',(.36,.018,.025));rooflead=material('Weathered lead',(.24,.27,.27))
# Front wall is cut around every observed opening, not covered with dark stickers.
front_holes=[rect(x-.43,4.78,x+.43,6.60) for x in (1.3,2.75,8.1,9.55)]
front_holes+=[ellipse_arch(u,0,2.36,.82,.82,24)]
front_holes+=[rect(x-.37,1.2,x+.37,2.5) for x in (8.2,9.75)]
F=wall('west frontage',(0,0),(W,0),H-.12,front_holes,mat=brick)
for i,x in enumerate((1.3,2.75,8.1,9.55)):window('upper '+str(i),F,x,4.78,6.60,.86)
for x in (8.1,9.55):
 box('Upper sash centre bar',(x,5.69,-.06),(.028,1.78,.08),'joinery',white,F)
for i,x in enumerate((8.2,9.75)):window('ground '+str(i),F,x,1.2,2.5,.74)
# Other walls follow the measured skew and northern step. Hidden openings stay
# restrained rather than receiving a fabricated repeating window pattern.
for i in range(1,len(poly)):
 a=poly[i];b=poly[(i+1)%len(poly)];wall('perimeter '+str(i),a,b,H-.12)
# Compound roof. A western hip joins the narrower eastern gable section at the
# real north step; these vertices are shared, so no intersecting roof boxes.
A=(0,0,H);B=(W,0,H);RC=(13.38,18.47,H);D1=(2.25,19.11,H);E=(1.68,9.09,H);G=(-.87,9.15,H)
S=(12.49,9.12,H);R0=(5.8,4.5,D['ridge']);R1=(6.2,9.12,D['ridge']);R2=(7.815,18.79,D['ridge'])
roof_faces=[[A,B,R0],[B,S,R1,R0],[S,RC,R2,R1],[D1,E,R1,R2],[E,G,R1],[G,A,R0,R1]]
m=Mesh('Roof compound slate')
for face in roof_faces:m.add(face,[tuple(range(len(face)))])
finish(m,'roof',slate)
m=Mesh('Wall eastern gable');m.add([RC,D1,R2],[(0,1,2)]);finish(m,mat=rear)
# Shallow eaves fascia closes the junction to masonry.
for i,a in enumerate(poly):
 b=poly[(i+1)%len(poly)];m=Mesh('Roof eaves');m.add([(*b,H),(*a,H),(*a,H-.12),(*b,H-.12)],[(0,1,2,3)]);finish(m,'roof',slate)
# Blocked arched upper opening, visible beyond the supermarket service canopy.
a,b=poly[2],poly[3];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);EF=face_matrix((*a,0),(dy/length,-dx/length,0));centre=length*.5
m=Mesh('Rear blocked arch');arc(m,centre,6.30,.64,.72,.22,out=.035,depth=.045,steps=24);finish(m,mat=brick,frame=EF)
for x0,x1 in [(centre-1.45,centre-.64),(centre+.64,centre+1.45)]:box('Rear stone impost',((x0+x1)/2,6.30,.04),(x1-x0,.22,.08),'walls',cream,EF)
box('Rear blocked sill',(centre,4.38,.065),(2.9,.16,.13),'walls',cream,EF)
# West photograph shows continuous stone strings and modest eaves moulding.
for z,h,out in [(4.70,.085,.035),(6.66,.07,.025),(7.10,.14,.07)]:box('Front stone band',(W/2,z,out/2),(W,h,out),'walls',cream,F)
# Upper segmental white headers and small shoulders at each window.
for x in (1.3,2.75,8.1,9.55):
 m=Mesh('Window gauged brick header');arc(m,x,6.59,.45,.06,.19,out=.03,depth=.04,steps=16);finish(m,mat=brick,frame=F)
 box('Window head cream',(x,6.64,.065),(1.02,.075,.13),'walls',cream,F)
# Entrance porch: independent brick face, open round-headed door and deep reveal.
# Its projection is evidenced by the side-lit arch photograph.
porch_left=u-1.55;porch_right=u+1.55;door=ellipse_arch(u,0,2.36,.82,.82,24)
m=Mesh('Porch brick frontage')
for p in cuts(rect(porch_left,0,porch_right,3.42),[door]):m.add([(x,z,.75) for x,z in p],[tuple(range(len(p)))])
for a,b in zip(door,door[1:]+door[:1]):m.add([(*a,.75),(*b,.75),(*b,.18),(*a,.18)],[(0,1,2,3)])
for x in (porch_left,porch_right):m.add([(x,0,0),(x,0,.75),(x,3.42,.75),(x,3.42,0)],[(0,1,2,3) if x==porch_right else (3,2,1,0)])
finish(m,mat=brick,frame=F)
if DETAIL:
 # Real curved arch mouldings, cream impost consoles, triangular pediment.
 m=Mesh('Entrance gauged arch')
 for i in range(25):arc(m,u,2.36,.82,.82,.29,out=.79,depth=.10,steps=2,start=i*math.pi/25+.003,end=(i+1)*math.pi/25-.003)
 finish(m,mat=archbrick,frame=F)
 for sign in (-1,1):
  x=u+sign*1.32
  box('Porch console',(x,2.85,.83),(.42,.60,.24),'walls',cream,F)
  for z,w,h in [(2.53,.59,.10),(3.13,.57,.10),(3.22,.66,.08)]:box('Porch console moulding',(x,z,.85),(w,h,.30),'walls',cream,F)
  m=Mesh('Porch console rosette');arc(m,x,2.86,.06,.06,.025,out=.98,depth=.025,steps=20,start=0,end=math.tau);finish(m,mat=stone,frame=F)
 m=Mesh('Porch pediment brick');m.outline([(u-1.63,3.24),(u+1.63,3.24),(u,4.12)],.70,.89);finish(m,mat=brick,frame=F)
 # Continuous diagonal moulding sections meet at the apex.
 for sign in (-1,1):
  x0=u+sign*1.72;x1=u;z0=3.22;z1=4.18
  m=Mesh('Porch pediment cornice');m.outline([(x0,z0),(x1,z1),(x1,z1+.12),(x0,z0+.12)],.80,1.03);finish(m,mat=cream,frame=F)
 m=Mesh('Porch keystone');m.outline([(u-.10,3.08),(u+.10,3.08),(u+.16,3.60),(u-.16,3.60)],.80,.98);finish(m,mat=cream,frame=F)
 # Stepped brick backing behind pediment, rather than a floating triangular trim.
 for x0,x1,z in [(u-1.55,u-1.05,3.56),(u-1.05,u+1.05,4.28),(u+1.05,u+1.55,3.56)]:
  box('Porch stepped backing',((x0+x1)/2,(3.42+z)/2,.40),(x1-x0,z-3.42,.80),'walls',brick,F)
  box('Porch backing coping',((x0+x1)/2,z+.035,.42),(x1-x0+.04,.07,.86),'walls',cream,F)
 # Closed black outer leaves correspond to the2024 street photograph.
 box('Door black leaves',(u,1.14,.23),(1.61,2.28,.12),'joinery',black,F)
 for x in (u-.84,u+.84):box('Door cream jamb',(x,1.17,.33),(.10,2.34,.12),'joinery',cream,F)
 box('Door head rail',(u,2.34,.33),(1.80,.14,.14),'joinery',cream,F)
 m=Mesh('Door fanlight');m.outline(ellipse_arch(u,2.36,2.36,.79,.79,32),.23,.28);finish(m,'joinery',glass,F)
 m=Mesh('Fanlight curved frame');arc(m,u,2.36,.75,.75,.045,out=.34,depth=.08,steps=32);finish(m,'joinery',cream,F)
 for angle in (math.pi/6,math.pi/3,math.pi/2,2*math.pi/3,5*math.pi/6):
  from components import beam
  m=Mesh('Fanlight radial bar');beam(m,(u,2.36,.34),(u+.74*math.cos(angle),2.36+.74*math.sin(angle),.34),.026,.06);finish(m,'joinery',cream,F)
 for side in (-1,1):
  for z in (.4,1.0,1.73):
   x=u+side*.40;box('Door recessed panel',(x,z,.298),(.64,.48,.025),'joinery',black,F)
   for zz in (z-.26,z+.26):box('Door panel rail',(x,zz,.32),(.71,.04,.06),'joinery',doortrim,F)
 box('Door threshold',(u,-.025,.42),(1.82,.05,.90),'walls',stone,F)
 # Twin narrow signs are lettered geometry, independent of the photograph pixels.
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
 def text(name,body,x,z,height,width,out=.935):
  ob=text_object('Sign '+name,body,(0,0,0),(0,0,1),height,width,font,white,extrude=.002,collection=C['joinery'],fit_bounds=True)
  local=Matrix.Translation((x,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(T@F@local);ob.matrix_world=Matrix.Identity(4)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='Sign UV')
 for sign in (-1,1):
  x=u+sign*1.23;box('Sign red panel',(x,1.57,.90),(.40,1.73,.035),'joinery',red,F)
  for i,ch in enumerate('BIJOU'):text('Bijou '+str(sign)+str(i),ch,x,2.25-i*.30,.25,.24)
  text('cinema '+str(sign),'CINEMA',x,.86,.09,.34)
 text('number','8',u,2.13,.12,.13,.313)
else:
 m=Mesh('Massing porch pediment');m.outline([(u-1.63,3.24),(u+1.63,3.24),(u,4.18)],.70,.89);finish(m,mat=cream,frame=F)
 m=Mesh('Massing entrance glazing');m.outline(door,.22,.24);finish(m,'joinery',glass,F)
# Roof vents and stacks directly visible in aerial and west photographs.
for x,y in [(11.8,15.0),(10.0,6.2)]:
 box('Chimney',(x,y,8.85),(.62,.83,1.7),'roof',rear)
 box('Chimney cap',(x,y,9.75),(.76,.97,.12),'roof',brick)
 for dx in (-.17,.17):
  m=Mesh('Chimney pot');m.lathe((x+dx,y),[(9.81,.095),(10.13,.085),(10.18,.11)],16);finish(m,'roof',brick)
m=Mesh('Roof vent');m.lathe((5.8,4.7),[(9.75,.23),(10.12,.23),(10.19,.28)],20);finish(m,'roof',rooflead)
# Low southern lean-to is visible overhead; its hidden windows are deferred.
inner=lambda v:11.63+(13.38-11.63)*v/18.47
v0,v1=1.0,9.1
q=[(inner(v0),v0),(inner(v0)+2.9,v0),(inner(v1)+2.9,v1),(inner(v1),v1)]
wall('lean-to front',q[0],q[1],3.15)
wall('lean-to outer',q[1],q[2],3.15)
wall('lean-to back',q[2],q[3],3.15)
m=Mesh('Roof south lean-to');m.add([(*q[0],4.15),(*q[1],3.15),(*q[2],3.15),(*q[3],4.15)],[(0,1,2,3)]);finish(m,'roof',slate)
for a,b in [(q[0],q[1]),(q[3],q[2])]:
 m=Mesh('Wall lean-to wedge');m.add([(*a,3.15),(*b,3.15),(*a,4.15)],[(0,1,2)]);finish(m,mat=rear)
# Low northern access range bounds the photographed entrance passage. Four
# small white windows face the path; the western attachment is partly hidden.
AF=wall('access range south',(4.10,-10),(4.10,0),3.2,
 [rect(v-.43,2.38,v+.43,3.0) for v in (2.0,3.7,5.4,7.1)],mat=brick)
for i,v in enumerate((2.0,3.7,5.4,7.1)):window('access range '+str(i),AF,v,2.38,3.0,.86)
wall('access range north',(1.0,0),(1.0,-10),3.2)
wall('access range west',(1.0,-10),(4.10,-10),3.2,mat=brick)
m=Mesh('Roof access range');m.add([(1,-10,3.5),(4.10,-10,3.2),(4.10,0,3.2),(1,0,3.5)],[(0,1,2,3)]);finish(m,'roof',slate)
m=Mesh('Wall access range west wedge');m.add([(1,-10,3.2),(4.10,-10,3.2),(1,-10,3.5)],[(0,1,2)]);finish(m,mat=brick)
wall('access range north upper',(1,0),(1,-10),3.5,bottom=3.2)
# Repeated source parts are batched to avoid per-object bake setup overhead.
groups={}
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH':continue
 family='Roof envelope' if ob.name.startswith(('Roof compound slate','Roof eaves')) else 'Wall exterior' if ob.name.startswith('Wall ') else 'Architecture'
 groups.setdefault((ob.users_collection[0].name,family),[]).append(ob)
for (part,family),objects in groups.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=family+' '+part
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.4,-.5);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/bijou-cinema.blend'))
