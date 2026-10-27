"""Provisional measured massing; no assertion of finished construction."""
import json, os, sys, math
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]; REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(REPO/'tools'),str(ROOT/'scripts')]
from southport3d.geometry import Mesh,text_object
from surface_owner import partition
from components import cut,rect,arch
D=json.loads((ROOT/'research/layout.json').read_text()); X,Y,Z=D['origin'];W=D['width'];L=D['length'];F=D['front_depth'];A=D['arcade_wing_width'];B=W-D['corp_range_width'];E=D['wing_eave'];R=D['wing_ridge'];Q=D['range_eave'];S=D['range_ridge']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';collections={}
for n in ('frontage','rear','roof'):
 c=bpy.data.collections.new(n);s.collection.children.link(c);collections[n]=c
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.8
 texture={'Red brick':'brick','Slate':'slate','Mansard clay tiles':'clay-tile'}.get(n)
 if texture:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')),check_existing=True);m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
 return m
pale=mat('Pale masonry',(.69,.67,.62));brick=mat('Red brick',(.42,.22,.16));slate=mat('Slate',(.19,.20,.21));flat=mat('Flat roof',(.35,.36,.35)); dark=mat('Black painted joinery',(.04,.045,.05)); glass=mat('Dark glazing',(.055,.08,.09)); cream=mat('Ivory trim',(.78,.75,.67)); timber=mat('Dark gable timber',(.09,.07,.055)); columnstone=mat('Gallery grey stone',(.34,.33,.31)); tile=mat('Mansard clay tiles',(.40,.19,.14)); blue=mat('Blue retained lettering',(.025,.07,.27)); red=mat('Red shop sign',(.48,.03,.04))
def world(p):
 u,v,z=p;t=v/L;q=u/W
 return (X+u+t*(2.189*(1-q)+.498*q),Y+v+(1-t)*2.862*(1-q)+t*(-.016+.694*q),Z+z)
def finish(m,part,material):
 o=m.finish([material],collections[part]);uv=o.data.uv_layers.new(name='metric')
 for poly in o.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(poly.normal[i]))[:2])
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/1.8,v[axes[1]]/.6)
 for vert in o.data.vertices:vert.co=world(vert.co)
 o.data.update();return o
def box(name,x0,y0,z0,x1,y1,z1,part,material):
 m=Mesh('Shell '+name);m.box(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0));finish(m,part,material)
def face(name,verts,part,material):
 m=Mesh('Shell '+name);m.add(verts,[tuple(range(len(verts)))]);finish(m,part,material)
# Wall surfaces are cut around glazed openings. Plane axes are facade u and height.
def wall(name,width,height,holes,axis,fixed,part,material,unglazed=()):
 def point(u,z,d=0):return (u,fixed+d,z) if axis=='x' else (fixed-d,u,z)
 m=Mesh('Shell '+name)
 for q in cut(rect(0,0,width,height),holes):m.add([point(*v) for v in q],[tuple(range(len(q)))])
 for h in holes:
  for a,b in zip(h,h[1:]+h[:1]):m.add([point(*a),point(*b),point(*b,.18),point(*a,.18)],[(0,1,2,3)])
 finish(m,part,material)
 for i,h in enumerate(holes):
  if h in unglazed:continue
  m=Mesh('Glazing '+name+' '+str(i));m.add([point(*v,.18) for v in h],[tuple(range(len(h)))]);finish(m,part,glass)
# Revision 01 composition follows its documented evidence schedule.
exec(compile((ROOT/'scripts'/'facade_revision.py').read_text(),str(ROOT/'scripts'/'facade_revision.py'),'exec'),globals())
# Cylindrical vertical circulation tower at head of the court, not a solid court infill.
m=Mesh('Shell rounded tower');m.lathe((A+2.1,F+1.5),[(0,1.8),(16.4,1.8)],segments=24);finish(m,'rear',pale)
# Glazing bands follow the rounded tower shown from Corporation Street.
for z in [4.3,8.0,11.7]:
 for j in range(12):
  t0=math.pi*j/12;t1=math.pi*(j+1)/12;r=1.81;cx=A+2.1;cy=F+1.5
  m=Mesh('Glazing rounded tower');m.add([(cx+r*math.cos(t0),cy+r*math.sin(t0),z),(cx+r*math.cos(t1),cy+r*math.sin(t1),z),(cx+r*math.cos(t1),cy+r*math.sin(t1),z+2.5),(cx+r*math.cos(t0),cy+r*math.sin(t0),z+2.5)],[(0,1,2,3)]);finish(m,'rear',glass)
# Long arcade wing: repeated upper apertures and a continuous shop range.
winglen=L-F
wingholes=[rect(.25,.25,winglen-.25,3.4)]
for u in [2+4*i for i in range(6)]:
 for z in [9.0]:wingholes.append(rect(u-.5,z,u+.5,z+2.25))
# Shift facade-local y distances to global asset-local y.
def wingpoint(u,z,d=0):return (d,F+u,z)
m=Mesh('Shell Arcade front')
for q in cut(rect(0,0,winglen,E),wingholes):m.add([wingpoint(*v) for v in q],[tuple(range(len(q)))])
for h in wingholes:
 for a,b in zip(h,h[1:]+h[:1]):m.add([wingpoint(*a),wingpoint(*b),wingpoint(*b,.18),wingpoint(*a,.18)],[(0,1,2,3)])
finish(m,'rear',pale)
for h in wingholes:
 m=Mesh('Glazing arcade');m.add([wingpoint(*v,.18) for v in h],[tuple(range(len(h)))]);finish(m,'rear',glass)
# Opposite court elevation is visible in the oblique 3D survey: regular tall windows.
courtholes=[]
for u in [F+2.6,F+7.3,F+12.0,F+16.7,F+21.4]:
 for z in [1.2,5.1,9.0]:courtholes.append(rect(u-.75,z,u+.75,z+2.35))
m=Mesh('Shell court wing')
for q in cut(rect(F,0,L,E),courtholes):m.add([(A,u,z) for u,z in q],[tuple(range(len(q)))])
for h in courtholes:
 for a,b in zip(h,h[1:]+h[:1]):m.add([(A,*a),(A,*b),(A-.18,*b),(A-.18,*a)],[(0,1,2,3)])
finish(m,'rear',pale)
for h in courtholes:
 m=Mesh('Glazing courtyard wing');m.add([(A-.18,u,z) for u,z in h],[tuple(range(len(h)))]);finish(m,'rear',glass)
face('Wing rear wall',[(0,L,0),(A,L,0),(A,L,E),(0,L,E)],'rear',pale)
# Corporation Street elevation has the observed brick base and five glazed bays.
for i in range(5):
 y0=F+(L-F)*i/5;y1=F+(L-F)*(i+1)/5
 h=[rect(y0+.45,.05,y0+1.7,3.0)] if i==0 else [rect((y0+y1)/2-1.0,.65,(y0+y1)/2+1.0,2.9)]
 # Facade local coordinates run along the y axis and extend to the actual street plane.
 m=Mesh('Shell Corporation bay');poly=rect(y0,0,y1,3.5)
 for q in cut(poly,h):m.add([(W,u,z) for u,z in q],[tuple(range(len(q)))])
 for opening in h:
  for a,b in zip(opening,opening[1:]+opening[:1]):m.add([(W,*a),(W,*b),(W-.18,*b),(W-.18,*a)],[(0,1,2,3)])
 finish(m,'frontage',brick)
 box('Architecture dark louvre band',W-.12,y0,3.5,W+.03,y1,Q,'frontage',timber)
 for opening in h:
  m=Mesh('Glazing Corporation');m.add([(W-.18,u,z) for u,z in opening],[tuple(range(len(opening)))]);finish(m,'frontage',glass)
face('Corporation court wall',[(B,L,0),(B,F,0),(B,F,Q),(B,L,Q)],'rear',brick)
face('Corporation end wall',[(B,L,0),(W,L,0),(W,L,Q),(B,L,Q)],'rear',brick)
face('Wing western pitch',[(0,F,E),(A/2,F,R),(A/2,L,R),(0,L,E)],'roof',slate)
face('Wing eastern pitch',[(A/2,F,R),(A,F,E),(A,L,E),(A/2,L,R)],'roof',slate)
face('Wing rear gable',[(0,L,E),(A,L,E),(A/2,L,R)],'rear',pale)
# Five gables face Corporation Street; actual bay positions provisional.
for i in range(5):
 y0=F+(L-F)*i/5;y1=F+(L-F)*(i+1)/5;ym=(y0+y1)/2
 face('Gable slope north %d'%i,[(B,y0,Q),(W,y0,Q),(W,ym,S),(B,ym,S)],'roof',slate)
 face('Gable slope south %d'%i,[(B,ym,S),(W,ym,S),(W,y1,Q),(B,y1,Q)],'roof',slate)
 face('Gable face %d'%i,[(W,y0,Q),(W,y1,Q),(W,ym,S)],'frontage',pale)
 face('Court gable %d'%i,[(B,y1,Q),(B,y0,Q),(B,ym,S)],'rear',pale)
 # Half-timber gable tracery and dark vertical louvres observed in 2011.
 def beam(label,a,b,r=.065):
  m=Mesh('Architecture '+label);m.tube([a,b],r,sides=4);finish(m,'frontage',timber)
 beam('gable left', (W+.055,y0,Q),(W+.055,ym,S),.09)
 beam('gable right',(W+.055,ym,S),(W+.055,y1,Q),.09)
 beam('gable tie',(W+.055,y0,Q+.13),(W+.055,y1,Q+.13),.08)
 for t in [.2,.4,.6,.8]:
  yy=y0+t*(y1-y0);top=Q+(S-Q)*(1-abs(2*t-1))
  beam('gable upright',(W+.055,yy,Q+.18),(W+.055,yy,top-.12),.045)

# Detail prototypes and observed low-range features are authored independently.
exec(compile((ROOT/'scripts'/'detail_revision.py').read_text(),str(ROOT/'scripts'/'detail_revision.py'),'exec'),globals())

for _ in range(3):
 if not partition([o for c in collections.values() for o in c.objects])['candidate_pairs']:break
for c in collections.values():
 for o in c.objects:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10 or (len(f.verts)==3 and (f.verts[1].co-f.verts[0].co).cross(f.verts[2].co-f.verts[0].co).length<1e-10)]
  if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
  bm.to_mesh(o.data);bm.free()
# Batch repeated pieces before projection, retaining material and UV ownership.
for part,c in collections.items():
 groups={}
 for ob in list(c.objects):
  if ob.type!='MESH':continue
  name=ob.name.split('.')[0]
  # Shell boxes may have been partitioned and use a different UV layer; never
  # join meshes whose active texture coordinates or material slots differ.
  key=(name,tuple(m.name if m else None for m in ob.data.materials),tuple(u.name for u in ob.data.uv_layers)) if name.startswith('Shell ') else (name,)
  groups.setdefault(key,[]).append(ob)
 for key,obs in groups.items():
  if len(obs)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=key[0]
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.25;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.5;sun.rotation_euler=(.4,-.6,-.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/former-bhs.blend'))
