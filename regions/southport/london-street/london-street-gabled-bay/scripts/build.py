"""London/Chapel corner: continuous two-storey envelope, four gables and clock."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path.insert(0,str(REPO/'lib'))
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from corner_plan import frame,roof_faces,world,signed_area
D=json.loads((ROOT/'research/layout.json').read_text());P=D['corner_footprint'];E=D['wall_height'];R=D['ridge_height']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ['architecture','roof','shopfront','rear']:
 C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,col,tex=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.75
 if tex:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/(tex+'.png')));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
brick=material('Red brick',(.5,.22,.15),'brick');slate=material('Blue grey slate',(.12,.15,.16),'slate');cream=material('Weathered cream render',(.63,.61,.53));white=material('White frames',(.78,.79,.75));glass=material('Opaque exterior glazing',(.10,.17,.18));black=material('Dark painted metal',(.025,.033,.034));felt=material('Weathered flat membrane',(.42,.43,.40));metal=material('Lead and plant metal',(.40,.44,.46));blue=material('Hays blue',(.025,.12,.43));gold=material('Yellow brass',(.82,.62,.12))
def finish(m,mat=brick,part='architecture',F=None):
 o=m.finish([mat],C[part])
 if F:o.matrix_world=F
 # Consistent UVs: facade brick courses follow elevation, roof slate rows the
 # horizontal contour of each slope (rather than one world-axis projection).
 uv=o.data.uv_layers.new(name='Metric authored UV')
 for f in o.data.polygons:
  n=f.normal
  if mat==slate:
   across=Vector((n.y,-n.x,0));across=across.normalized() if across.length>.01 else Vector((1,0,0));up=n.cross(across).normalized()
   if up.z<0:up=-up
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if mat==slate:uv.data[li].uv=(v.dot(across)/2.4,v.dot(up)/2.2)
   elif F:uv.data[li].uv=(v.x/1.8,v.y/.6)
   else:
    axes=sorted(sorted(range(3),key=lambda k:abs(n[k]))[:2]);uv.data[li].uv=(v[axes[0]]/1.8,v[axes[1]]/.6)
 return o

def box(name,c,size,mat=brick,part='architecture',F=None):
 m=Mesh(name);m.box(c,size);return finish(m,mat,part,F)

def surface(name,points,mat=brick,part='architecture',F=None):
 m=Mesh(name);m.add(points,[tuple(range(len(points)))]);return finish(m,mat,part,F)

# Use a right-handed facade frame: local u runs opposite the clockwise outline.
def facade_frame(i):
 a,u,n,w=frame(P,i);b=P[(i+1)%len(P)];F=face_matrix((*b,0),(*n,0));return F,w

def rect_wall(name,w,h,holes,F,gables=(),part='architecture'):
 xs=sorted(set([0,w]+[v for q in holes for v in q[:2]]+[w-c+t for c,r in gables for t in (-r,r)]));zs=sorted(set([0,h,4.0]+[v for q in holes for v in q[2:]]));mats={brick:Mesh('Wall '+name+' brick'),cream:Mesh('Wall '+name+' cream')}
 for a,b in zip(xs,xs[1:]):
  for lo,hi in zip(zs,zs[1:]):
   u,z=(a+b)/2,(lo+hi)/2
   if any(x<u<X and y<z<Y for x,X,y,Y in holes):continue
   mat=cream if z>=4 and any(abs(u-(w-c))<r for c,r in gables) else brick
   m=mats[mat];m.add([(a,lo,0),(b,lo,0),(b,hi,0),(a,hi,0)],[(0,1,2,3)])
   m.add([(a,lo,-.25),(a,hi,-.25),(b,hi,-.25),(b,lo,-.25)],[(0,1,2,3)])
 # Each opening has one continuous reveal; no internal caps between fragments.
 for a,b,lo,hi in holes:
  v=[(a,lo),(b,lo),(b,hi),(a,hi)]
  for A,B in zip(v,v[1:]+v[:1]):mats[brick].add([(*A,0),(*A,-.25),(*B,-.25),(*B,0)],[(0,1,2,3)])
 for mat,m in mats.items():
  if m.faces:finish(m,mat,part,F)

def window(F,u,z,w=1.0,h=1.45,part='architecture'):
 box('Window glazing',(u,z,-.12),(w,h,.025),glass,part,F)
 for x in (u-w/2+.03,u+w/2-.03):box('Trim window stile',(x,z,-.05),(.055,h,.085),white,part,F)
 for y in (z-h/2+.025,z+.04,z+h/2-.025):box('Trim window rail',(u,y,-.035),(w-.06,.05,.09),white,part,F)
 box('Trim sill',(u,z-h/2-.055,.055),(w+.12,.11,.25),cream,part,F)

fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';font=bpy.data.fonts.load(fontpath)
def letters(body,u,z,width,height,F,mat=white):
 pos=F@Vector((u,z,.10));normal=F.to_3x3()@Vector((0,0,1));o=text_object('Fine sign '+body,body,pos,normal,height,width,font,mat,extrude=.002,collection=C['shopfront']);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
 if not o.data.uv_layers:o.data.uv_layers.new(name='Text UV')

for i in range(len(P)):
 F,w=facade_frame(i);f=next((f for f in D['facades'] if f['edge']==i),None)
 if f:
  holes=[(w-u-.5,w-u+.5,4.8,6.25) for u in f['windows']]
  holes += [(w-b,w-a,.15,3.2) for a,b,name in f['shops']]
  rect_wall(f['name'],w,E-.1202,holes,F,f['gables'])
  for u in f['windows']:window(F,w-u,5.525)
  for c,r in f['gables']:
   u=w-c;surface('Wall gable '+str(i),[(u-r,E-.1202,0),(u+r,E-.1202,0),(u,R-.1202,0)],cream,F=F)
   # Narrow red brick border follows both rakes, matching the visible photo.
   for A,B in [((u-r,E),(u,R)),((u,R),(u+r,E))]:
    du,dz=B[0]-A[0],B[1]-A[1];M=F@Matrix.Translation(((A[0]+B[0])/2,(A[1]+B[1])/2,.055))@Matrix.Rotation(math.atan2(dz,du),4,'Z');box('Trim red gable rake',(0,0,0),(math.hypot(du,dz),.16,.12),brick,F=M)
   box('Trim gable base',(u,4.03,.045),(r*2,.16,.13),brick,F=F)
   box('Fine gable slot',(u,7.72,.012),(.075,.42,.025),brick,F=F)
  for a,b,name in f['shops']:
   left,right=w-b,w-a;ww=right-left;u=(left+right)/2;is_hays=name=='Hays Travel';trim=blue if is_hays else black
   box('Shop fascia',(u,3.58,.025),(ww,.72,.15),white if is_hays or name=='RIVER ISLAND' else black,'shopfront',F)
   if name:letters(name,u,3.58,ww-.35,.36,F,blue if is_hays else black if name=='RIVER ISLAND' else white)
   # Large display panels, recessed entrance at the end for the known shop.
   n=max(2,round(ww/1.6));step=ww/n
   for k in range(n):
    x=left+(k+.5)*step;dep=-.32 if k==n-1 and not is_hays else -.13
    box('Shop glazing',(x,1.64,dep),(step-.035,2.97,.025),glass,'shopfront',F)
   for k in range(n+1):box('Shop mullion',(left+k*step,1.65,-.06),(.045,3.0,.085),trim,'shopfront',F)
   for z in (.18,3.13):box('Shop rail',(u,z,-.055),(ww,.065,.09),trim,'shopfront',F)
   box('Shop plinth',(u,.09,-.03),(ww,.18,.22),black,'shopfront',F)
   if is_hays:
    box('Shop blue transom',(u,2.75,-.04),(ww,.72,.04),blue,'shopfront',F);box('Trim yellow strip',(u,2.38,-.015),(ww,.07,.035),gold,'shopfront',F)
   # Door reveals close the deeper entrance; no unmodelled interior holes.
   else:
    x=right-step;surface('Shop entry reveal',[(x,.15,-.05),(x,.15,-.34),(x,3.14,-.34),(x,3.14,-.05)],black,'shopfront',F)
    box('Shop entry soffit',(right-step/2,3.14,-.20),(step,.035,.29),black,'shopfront',F)
  # Piers and downpipes at visual bay boundaries; no deep classical columns.
  for a,b,name in f['shops']:
   u=w-a-.12;box('Trim brick pier',(u,3.62,.04),(.18,7.24,.08),brick,F=F)
   box('Fine downpipe',(u-.17,3.55,.10),(.065,7.1,.08),black,F=F)
 elif i==1:
  holes=[(.2,w-.2,0,3.12)] if w>.7 else []
  if w>1.5:holes.append((w/2-.47,w/2+.47,4.8,6.25))
  rect_wall('corner '+str(i),w,E-.1202,holes,F)
  if w>1.5:window(F,w/2,5.525,.94)
  box('Shop corner door',(w/2,1.55,-.19),(w-.4,3.1,.05),blue,'shopfront',F)
  box('Shop corner door glass',(w/2,1.65,-.15),(max(.2,w-.58),2.4,.025),glass,'shopfront',F)
  box('Shop corner number panel',(w/2,3.55,.025),(w-.35,.72,.15),black,'shopfront',F)
  if i==1:letters('57',w/2,3.55,w-.55,.42,F)
 elif i==2:rect_wall('corner plain return',w,E-.1202,[],F)
 else:rect_wall('unobserved rear '+str(i),w,E-.1202,[],F,part='rear')

# Roof strips are an exact planar partition of the footprint, including hips
# at the chamfer and the four cross-gable valleys. No intersecting roof boxes.
faces=roof_faces(D);tops={}
for name,vs in faces:
 key='flat' if name.startswith('inner') else 'slate';m=tops.setdefault(key,Mesh('Roof '+key));m.add(vs,[tuple(range(len(vs)))])
conformed,info=conform(tops)
for key,m in conformed.items():
 finish(m,felt if key=='flat' else slate,'roof')
# Give the roof an underside and outer rim with exactly the top boundary.
# These are shallow closing surfaces, not a second roof crossing neighbours.
for key,m in conformed.items():
 under=Mesh('Roof underside '+key);under.add([(x,y,z-.12) for x,y,z in m.vertices],[tuple(reversed(f)) for f in m.faces]);finish(under,felt,'roof')
# Roof boundary follows variable gable height and the sampled strip breaks.
edges={}
for m in conformed.values():
 for face in m.faces:
  for a,b in zip(face,face[1:]+face[:1]):
   A,B=tuple(m.vertices[a]),tuple(m.vertices[b]);k=tuple(sorted((A,B)));edges.setdefault(k,[]).append((A,B))
for pair,occ in edges.items():
 if len(occ)==1:
  a,b=occ[0];surface('Roof perimeter rim',[a,(a[0],a[1],a[2]-.12),(b[0],b[1],b[2]-.12),b],slate,'roof')
# Raised rear plant/access range seen in all four 3D orbits. Hidden elevations
# receive no guessed windows; exact equipment arrangements remain provisional.
x,X,y,Y=D['roof_room']['bounds'];hh=D['roof_room']['height']
box('Architecture roof service room',((x+X)/2,(y+Y)/2,(E+hh)/2),(X-x,Y-y,hh-E),brick,'roof')
box('Architecture roof service coping',((x+X)/2,(y+Y)/2,hh+.04),(X-x+.12,Y-y+.12,.08),cream,'roof')
for x,y,w,l in [(-22,-114,1.5,2.2),(-24,-120,1.8,2.0),(-20,-124,1.2,1.5)]:
 box('Fine roof cabinet',(x,y,E+.40),(w,l,.8),metal,'roof')
 for k in range(7):box('Fine cabinet louvre',(x-w/2-.015,y,E+.12+k*.09),(.025,l*.8,.025),black,'roof')
# Clock turret with lead skirt, four clock faces, tapered cap and weather vane.
cx,cy=-15.7,-127.9;z=R+.45
box('Architecture clock skirt',(cx,cy,z-.3),(1.1,1.1,.8),metal,'roof')
box('Architecture clock case',(cx,cy,z+.50),(1.0,1.0,1.0),cream,'roof')
for zz in (z,z+1.02):box('Trim clock cornice',(cx,cy,zz),(1.18,1.18,.10),white,'roof')
for n in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
 F=face_matrix((cx+n[0]*.51,cy+n[1]*.51,z+.51),n);m=Mesh('Fine clock dial');m.add([(0,0,.006)]+[(.36*math.cos(k*math.tau/40),.36*math.sin(k*math.tau/40),.006) for k in range(40)],[(0,k+1,(k+1)%40+1) for k in range(40)]);finish(m,black,'roof',F)
 for k in range(12):
  t=k*math.tau/12;M=F@Matrix.Translation((.29*math.sin(t),.29*math.cos(t),.025))@Matrix.Rotation(-t,4,'Z');box('Fine clock hour',(0,0,0),(.025,.075,.02),gold,'roof',M)
 for t,l in [(math.radians(60),.26),(math.radians(-60),.20)]:
  M=F@Matrix.Translation((l*.5*math.sin(t),l*.5*math.cos(t),.04))@Matrix.Rotation(-t,4,'Z');box('Fine clock hand',(0,0,0),(.026,l,.025),gold,'roof',M)
m=Mesh('Architecture clock cap');m.add([(cx-.62,cy-.62,z+1.07),(cx+.62,cy-.62,z+1.07),(cx+.62,cy+.62,z+1.07),(cx-.62,cy+.62,z+1.07),(cx,cy,z+1.65)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)]);finish(m,metal,'roof')
box('Fine vane spindle',(cx,cy,z+2.0),(.03,.03,.8),black,'roof');box('Fine vane arm',(cx,cy,z+2.15),(1.2,.025,.025),black,'roof')

# Apply the common geographic registration once, then batch compatible sources
# so atlas bakes do not traverse hundreds of tiny objects independently.
a=D['registration_radians'];px,py=D['registration_pivot'];reg=Matrix.Translation((px,py,D['base_z']))@Matrix.Rotation(a,4,'Z')@Matrix.Translation((-px,-py,0))
for o in list(s.objects):
 if o.type=='MESH':o.matrix_world=reg@o.matrix_world
families={}
for o in list(s.objects):
 if o.type=='MESH':families.setdefault((o.users_collection[0].name,'Fine' if o.name.startswith('Fine ') else 'Shell' if o.name.startswith(('Wall ','Roof ')) else 'Architecture'),[]).append(o)
for (part,kind),obs in families.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 obs[0].name=kind+' '+part
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.5;sun.rotation_euler=(.6,-.4,-.5)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-gabled-bay.blend'))
print('Corner roof conformance',info)
