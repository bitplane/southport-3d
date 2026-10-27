import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh
from southport3d.conform import conform
from southport3d.planar import subtract
from southport3d.elevation import Elevations
D=json.loads((R/'research/layout.json').read_text());p=D['footprint'];surface=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/west-street.json').surface('west-street-pavement');height=surface.height(-70,112)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;c=bpy.data.collections.new('building');s.collection.children.link(c)
def mat(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);return m
brick=mat('Red brick',(.47,.20,.15));tx=brick.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(R/'textures/brick.png'));brick.node_tree.links.new(tx.outputs['Color'],brick.node_tree.nodes['Principled BSDF'].inputs['Base Color']);white=mat('White cladding',(.75,.76,.74));roof=mat('Flat roof',(.65,.66,.64));glass=mat('Stair glazing',(.10,.17,.19));frame=mat('White painted joinery',(.82,.84,.81));dark=mat('Parking shadow',(.16,.17,.16));iron=mat('Black painted gate',(.026,.031,.030));joint=mat('Cladding standing seam',(.56,.58,.57));cope=mat('Dark roof edge',(.21,.23,.23))
def finish(m,material):
 ob=m.finish([material],c);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='metric')
 for f in ob.data.polygons:
  ax=sorted(sorted(range(3),key=lambda k:abs(f.normal[k]))[:2])
  for i in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[i].vertex_index].co;uv.data[i].uv=(v[ax[0]]/1.8,v[ax[1]]/.6) if material==brick else (v[ax[0]],v[ax[1]])
 return ob
# Facade apertures: restrained patterns from Street View and low-resolution 3D.
# Each opening is cut through its wall skin, with returns and inset glazing.
window_layout={0:[(.22,1.8)],1:[(.20,.64),(.78,.64)],2:[(.45,1.75)],5:[(.32,1.1),(.72,1.1)],6:[(.23,.65),(.60,1.05)],7:[(.25,.55),(.65,.55)],8:[(.88,.95)]}
def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def face_point(a,dx,dy,normal,u,z,offset=0):return (a[0]+dx*u+normal[0]*offset,a[1]+dy*u+normal[1]*offset,height+z)
for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
 dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);dx/=L;dy/=L;normal=(-dy,dx)
 lo=D['brick_base'] if i in (0,1,7,8) else 0
 windows=[]
 for f,w in window_layout.get(i,[]):
  u=L*f;w=min(w,L*(.55 if i==2 else (.4 if i==0 else .24)))
  for z in (3.8,6.4):windows.append((u-w/2,z,u+w/2,z+1.55))
  if i not in (5,6):windows.append((u-w/2,9.45,u+w/2,10.75))
 if i in (5,6):windows.append((.12*L,9.35,.88*L,10.85))
 for z0,z1,material in [(lo,D['clad_base'],brick),(D['clad_base'],D['wall_top'],white)]:
  setback=-.8 if i in (5,6) and z0>=D['clad_base'] else 0
  if setback:z1-=.08 # recessed wall meets the roof slab underside
  holes=[rect(x0,y0,x1,y1) for x0,y0,x1,y1 in windows if z0<=y0 and y1<=z1]
  parts=[rect(0,z0,L,z1)]
  panel=rect(.76*L,3.5,L,8.35) if i==8 and z0<D['clad_base'] else None
  if panel:parts=[q for part in parts for q in subtract(part,panel)]
  for hole in holes:parts=[q for part in parts for q in subtract(part,hole)]
  m=Mesh('Shell wall '+str(i))
  for q in parts:m.add([face_point(a,dx,dy,normal,u,z,setback) for u,z in q],[tuple(reversed(range(len(q))))])
  for h in holes:
   for A,B in zip(h,h[1:]+h[:1]):m.add([face_point(a,dx,dy,normal,*A,setback),face_point(a,dx,dy,normal,*B,setback),face_point(a,dx,dy,normal,*B,setback-.16),face_point(a,dx,dy,normal,*A,setback-.16)],[(0,1,2,3)])
  finish(m,material)
  if panel:
   panelparts=[panel]
   for hole in holes:panelparts=[q for part in panelparts for q in subtract(part,hole)]
   pm=Mesh('Architecture white corner panel')
   for q in panelparts:pm.add([face_point(a,dx,dy,normal,u,z) for u,z in q],[tuple(reversed(range(len(q))))])
   finish(pm,white)
 for j,(x0,z0,x1,z1) in enumerate(windows):
  off=-.8 if i in (5,6) and z0>=D['clad_base'] else 0
  m=Mesh('Glazing window');q=rect(x0,z0,x1,z1);m.add([face_point(a,dx,dy,normal,u,z,off-.16) for u,z in q],[(3,2,1,0)]);finish(m,glass)
  # One planar frame; separate pane apertures ensure no duplicate surface ownership.
  outer=rect(x0,z0,x1,z1);cols=5 if z0>9 and i in (5,6) else (3 if i==0 else (1 if i in (1,8) else 2));rows=2 if i in (0,2,8) and z0<9 else 1;inner=[rect(x0+.055+k*(x1-x0-.11)/cols+.025,z0+.055+j*(z1-z0-.11)/rows+.02,x0+.055+(k+1)*(x1-x0-.11)/cols-.025,z0+.055+(j+1)*(z1-z0-.11)/rows-.02) for k in range(cols) for j in range(rows)];parts=[outer]
  for h in inner:parts=[q for part in parts for q in subtract(part,h)]
  m=Mesh('Architecture window frame')
  for q in parts:m.add([face_point(a,dx,dy,normal,u,z,off-.045) for u,z in q],[tuple(reversed(range(len(q))))])
  finish(m,frame)
  # Three-dimensional sill under the aperture, with side returns and a drip lip.
  m=Mesh('Architecture window sill');u0=x0-.035;u1=x1+.035;za=z0-.075;zb=z0-.015
  corners=[face_point(a,dx,dy,normal,u,z,off+t) for t in (.015,.13) for u,z in [(u0,za),(u1,za),(u1,zb),(u0,zb)]]
  m.add(corners,[(0,1,5,4),(4,5,6,7),(7,6,2,3),(0,4,7,3),(1,2,6,5)]);finish(m,frame)
 # Fine metal standing seams on the opaque parts of the upper cladding. The
 # strips stop at the openings and sit on, rather than duplicate, the wall.
 if i not in (5,6):
  m=Mesh('Fine cladding seams');num=max(1,int(L/.13))
  for k in range(1,num):
   u=L*k/num;intervals=[(D['clad_base']+.015,D['wall_top']-.04)]
   for x0,z0,x1,z1 in windows:
    if x0-.018<u<x1+.018:
     intervals=[v for a0,b0 in intervals for v in ((a0,min(b0,z0-.01)),(max(a0,z1+.01),b0)) if v[1]-v[0]>.02]
   for a0,b0 in intervals:
    q=rect(u-.006,a0,u+.006,b0);m.add([face_point(a,dx,dy,normal,uu,zz,.007) for uu,zz in q],[(3,2,1,0)])
  finish(m,joint)
# Recess the upper court-facing walls behind a narrow balcony. Parallel
# offsets are joined with short returns at each end and the internal corner.
insets=[]
for i in (5,6):
 a,b=p[i],p[(i+1)%len(p)];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);dx/=L;dy/=L;normal=(-dy,dx)
 A=(a[0]-.8*normal[0],a[1]-.8*normal[1]);B=(b[0]-.8*normal[0],b[1]-.8*normal[1]);insets.append((A,B))
 m=Mesh('Architecture balcony floor');m.add([(a[0],a[1],height+9),(b[0],b[1],height+9),(B[0],B[1],height+9),(A[0],A[1],height+9)],[(0,1,2,3)]);finish(m,roof)
 # A single cut plane owns the handrail and upright strips, avoiding rail/bar overlap.
 outer=rect(0,9,L,10.05);holes=[]
 for j in range(5):holes.append(rect(j*L/5+.045,9.09,(j+1)*L/5-.045,9.97))
 parts=[outer]
 for hole in holes:parts=[q for part in parts for q in subtract(part,hole)]
 m=Mesh('Architecture balcony railing')
 for q in parts:m.add([face_point(a,dx,dy,normal,u,z,.015) for u,z in q],[tuple(reversed(range(len(q))))])
 finish(m,frame)
m=Mesh('Architecture balcony corner floor');m.add([(p[6][0],p[6][1],height+9),(insets[0][1][0],insets[0][1][1],height+9),(insets[1][0][0],insets[1][0][1],height+9)],[(0,1,2)]);finish(m,roof)
for a,b in [(p[5],insets[0][0]),(insets[0][1],insets[1][0]),(insets[1][1],p[7])]:
 m=Mesh('Shell upper balcony return');m.add([(a[0],a[1],height+9),(b[0],b[1],height+9),(b[0],b[1],height+D['wall_top']-.08),(a[0],a[1],height+D['wall_top']-.08)],[(0,1,2,3)]);finish(m,white)
v=[Vector((x,y,0)) for x,y in p];m=Mesh('Shell roof')
for tri in tessellate_polygon([v]):
 q=[v[k] if isinstance(k,int) else k for k in tri];order=(0,1,2) if (q[1]-q[0]).cross(q[2]-q[0]).z>0 else (2,1,0);m.add([(a.x,a.y,height+D['wall_top']) for a in q],[order])
m=conform({'roof':m})[0]['roof'];finish(m,roof)
# The 80 mm slab underside owns the sheltered balcony ceiling; return walls
# stop here instead of crossing the top plane and shimmering at grazing angles.
m=Mesh('Architecture roof underside')
for tri in tessellate_polygon([v]):
 q=[v[k] if isinstance(k,int) else k for k in tri];order=(2,1,0) if (q[1]-q[0]).cross(q[2]-q[0]).z>0 else (0,1,2);m.add([(a.x,a.y,height+D['wall_top']-.08) for a in q],[order])
m=conform({'underside':m})[0]['underside'];finish(m,roof)
x,y,r=D['tower'];n=48
for z0,z1,material in [(0,3.3,white),(3.3,4.4,white),(4.4,9.35,white),(9.35,10.65,glass),(10.65,11.7,white)]:
 m=Mesh('Architecture tower')
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
  if z0==3.3 and i in (0,1,n-2,n-1):continue
  m.add([(x+r*math.cos(a),y+r*math.sin(a),height+z0),(x+r*math.cos(b),y+r*math.sin(b),height+z0),(x+r*math.cos(b),y+r*math.sin(b),height+z1),(x+r*math.cos(a),y+r*math.sin(a),height+z1)],[(0,1,2,3)])
 finish(m,material)
m=Mesh('Architecture tower upper mullions')
for i in range(0,n,4):
 a=2*math.pi*i/n;d=.012;m.add([(x+(r+.014)*math.cos(a-d),y+(r+.014)*math.sin(a-d),height+9.35),(x+(r+.014)*math.cos(a+d),y+(r+.014)*math.sin(a+d),height+9.35),(x+(r+.014)*math.cos(a+d),y+(r+.014)*math.sin(a+d),height+10.65),(x+(r+.014)*math.cos(a-d),y+(r+.014)*math.sin(a-d),height+10.65)],[(0,1,2,3)])
finish(m,frame)
# Corrugated drum cap, legible at street level; ribs terminate before coping.
m=Mesh('Fine curved cap seams')
for i in range(n):
 a=2*math.pi*i/n;d=.004
 m.add([(x+(r+.009)*math.cos(a-d),y+(r+.009)*math.sin(a-d),height+10.68),(x+(r+.009)*math.cos(a+d),y+(r+.009)*math.sin(a+d),height+10.68),(x+(r+.009)*math.cos(a+d),y+(r+.009)*math.sin(a+d),height+11.66),(x+(r+.009)*math.cos(a-d),y+(r+.009)*math.sin(a-d),height+11.66)],[(0,1,2,3)])
finish(m,joint)
m=Mesh('Glazing stair tower lower window');a=-math.pi/12;b=math.pi/12;m.add([(x+r*math.cos(a)-.06,y+r*math.sin(a),height+3.3),(x+r*math.cos(b)-.06,y+r*math.sin(b),height+3.3),(x+r*math.cos(b)-.06,y+r*math.sin(b),height+4.4),(x+r*math.cos(a)-.06,y+r*math.sin(a),height+4.4)],[(0,1,2,3)]);finish(m,glass)
m=Mesh('Architecture tower window trim');out=rect(-.45,3.26,.45,4.44);hole=rect(-.39,3.32,.39,4.38)
for q in subtract(out,hole):m.add([(x+r*.966-.025,y+u,height+z) for u,z in q],[tuple(range(len(q)))])
finish(m,frame)
m=Mesh('Architecture tower roof');m.add([(x,y,height+11.7)]+[(x+r*math.cos(2*math.pi*i/n),y+r*math.sin(2*math.pi*i/n),height+11.7) for i in range(n)],[(0,1+i,1+(i+1)%n) for i in range(n)]);finish(m,roof)
m=Mesh('Fine roof coping')
def mitre(i,offset):
 prev=p[i-1];v=p[i];nxt=p[(i+1)%len(p)]
 u=Vector((v[0]-prev[0],v[1]-prev[1])).normalized();w=Vector((nxt[0]-v[0],nxt[1]-v[1])).normalized()
 n0=Vector((-u.y,u.x));n1=Vector((-w.y,w.x));delta=(n0+n1)*offset/max(.1,(n0+n1).dot(n1))
 return (v[0]+delta.x,v[1]+delta.y,height+11.405)
for i in range(len(p)):
 j=(i+1)%len(p);m.add([mitre(i,.055),mitre(j,.055),mitre(j,-.055),mitre(i,-.055)],[(0,1,2,3)])
finish(m,cope)
m=Mesh('Fine tower rim')
for i in range(n):
 a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
 m.add([(x+(r+.025)*math.cos(a),y+(r+.025)*math.sin(a),height+11.66),(x+(r+.025)*math.cos(b),y+(r+.025)*math.sin(b),height+11.66),(x+(r+.025)*math.cos(b),y+(r+.025)*math.sin(b),height+11.71),(x+(r+.025)*math.cos(a),y+(r+.025)*math.sin(a),height+11.71)],[(0,1,2,3)])
finish(m,cope)
# Parking soffit and the small sheltered entrance; no invented interior.
m=Mesh('Architecture parking soffit')
for tri in tessellate_polygon([v]):
 q=[v[k] if isinstance(k,int) else k for k in tri];order=(2,1,0) if (q[1]-q[0]).cross(q[2]-q[0]).z>0 else (0,1,2);m.add([(a.x,a.y,height+2.8) for a in q],[order])
finish(m,dark)
# The actual shared entrance is obscured in the available panorama; keep
# the sheltered approach open rather than placing an unsupported door panel.
a,b=p[8],p[0];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);nx=-dy/L*.10;ny=dx/L*.10
m=Mesh('Architecture parking fascia beam');z0=height+2.62;z1=height+2.8
q=[(a[0]+nx,a[1]+ny,z0),(b[0]+nx,b[1]+ny,z0),(b[0]-nx,b[1]-ny,z0),(a[0]-nx,a[1]-ny,z0),(a[0]+nx,a[1]+ny,z1),(b[0]+nx,b[1]+ny,z1),(b[0]-nx,b[1]-ny,z1),(a[0]-nx,a[1]-ny,z1)];m.add(q,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(3,2,1,0)]);finish(m,white)
for xx,yy in [(-63.0,120.2),(-64.0,115.2)]:
 m=Mesh('Architecture parking column');m.box((xx,yy,height+1.4),(.24,.24,2.8));m.faces.pop();m.indices.pop();finish(m,white)
# Black gates and railings across the observed street end. The road axis is
# y=109.73; two unequal side panels and two vehicle leaves preserve access.
gx=-59.0;gy=[104.65,107.0,109.85,112.7,114.75];gz=surface.height(gx,109.73)
gate=Mesh('Architecture street gate')
for y in gy:gate.box((gx,y,gz+.90),(.10,.10,2.04))
for lo,hi in zip(gy,gy[1:]):
 lo+=.05;hi-=.05
 for z in (.07,1.0,1.8):gate.box((gx,(lo+hi)/2,gz+z),(.035,hi-lo,.035))
 count=max(1,int((hi-lo)/.14))
 for j in range(1,count):
  yy=lo+(hi-lo)*j/count
  for z0,z1 in ((.0875,.9825),(1.0175,1.7825)):
   gate.box((gx,yy,gz+(z0+z1)/2),(.035,.025,z1-z0))
finish(gate,iron)
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);cam.data.type='ORTHO';s.camera=cam;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/cable-mews.blend'))
