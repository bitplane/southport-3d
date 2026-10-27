"""Jacksons: evidenced corner, shopfront, projecting bays and shallow roof."""
import json,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix
import math
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh, face_matrix
from southport3d.planar import subtract
from plan import outline,roofs
D=json.loads((ROOT/'research/layout.json').read_text());x,y,z=D['origin'];T=Matrix(((-.056,-1,0,x),(1,0,0,y),(0,0,1,z),(0,0,0,1)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof','projecting-sign'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);return m
wall=material('Painted render',(.77,.76,.71));slate=material('Slate',(.23,.25,.25));brick=material('Red brick',(.38,.15,.11));tan=material('Corner tile',(.48,.30,.21));dark=material('Black joinery',(.035,.04,.04));glass=material('Glazing',(.10,.16,.17));white=material('Painted white joinery',(.85,.85,.80))
def finish(name,vertices,faces,part,mat,frame=T):
 m=Mesh(name);m.add(vertices,faces);o=m.finish([mat],C[part]);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));
 if part=='roof':bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update();uv=o.data.uv_layers.new(name='Metric UV')
 for p in o.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 o.data.transform(frame);return o
e=D['eave'];m=D['main_depth'];w=D['width'];dep=D['depth']
def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def skin(name,polygon,holes,frame,part,mat=wall):
 pieces=[polygon]
 for h in holes:pieces=[v for p in pieces for v in subtract(p,h)]
 verts=[];faces=[]
 for piece in pieces:
  off=len(verts);verts.extend([(*p,0) for p in piece]);faces.append(tuple(range(off,len(verts))))
 for hole in holes:
  for a,b in zip(hole,hole[1:]+hole[:1]):
   off=len(verts);verts.extend([(*a,0),(*b,0),(*b,-.15),(*a,-.15)]);faces.append(tuple(range(off,off+4)))
 return finish('Shell '+name,verts,faces,part,mat,frame)
def box(name,centre,size,frame,part,mat):
 mesh=Mesh(('Fine ' if name in ('fascia rib','door handle') else 'Architecture ')+name);mesh.box(centre,size);return finish(mesh.name,mesh.vertices,mesh.faces,part,mat,frame)
def glazing(name,a,b,c,d,frame,part,material=dark,columns=2):
 finish('Glazing '+name,[(a,b,-.11),(c,b,-.11),(c,d,-.11),(a,d,-.11)],[(0,1,2,3)],part,glass,frame)
 t=.055
 for z in (b,d-t):box(name+' rail',((a+c)/2,z+t/2,-.03),(c-a,t,.12),frame,part,material)
 for x in [a,c-t]+[a+(c-a)*i/columns-t/2 for i in range(1,columns)]:box(name+' post',(x+t/2,(b+d)/2,-.03),(t,d-b-2*t,.12),frame,part,material)
 for i in range(columns):
  aa=a+t if i==0 else a+(c-a)*i/columns+t/2;bb=c-t if i==columns-1 else a+(c-a)*(i+1)/columns-t/2
  box(name+' transom',((aa+bb)/2,b+(d-b)*.72,-.03),(bb-aa,.045,.12),frame,part,material)
def bay_slab(name,line,lo,hi,mat):
 # The slab follows the angled bay, with an explicit outer fascia and back edge.
 poly=[(line[0][0],0),line[1],line[2],(line[3][0],0)];n=len(poly)
 v=[(u,h,z) for h in (lo,hi) for u,z in poly]
 faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 finish('Architecture bay '+name,v,faces,'frontage',mat,F)
F=T@face_matrix((1,0,0),(0,-1,0));S=T@face_matrix((0,m,0),(-1,0,0));K=T@face_matrix((0,1,0),(-1,-1,0));front=w-1
# Each glazing or bay aperture removes its supporting skin; reveals own the side surfaces.
front_open=[rect(.20,-.2,5.65,2.56),rect(5.90,.05,7.02,2.56),rect(7.25,-.2,9.10,2.56)]
bays=[(.35,2.45),(5.10,7.25)]
front_open += [rect(a,3.68,b,5.12) for a,b in bays]
skin('Nevill lower brick',rect(0,-.2,front,2.65),front_open[:3],F,'frontage',brick)
skin('Nevill upper',rect(0,2.65,front,e),front_open[3:],F,'frontage')
for a,b in bays:
 # Three distinct angled faces of each projected upper bay.
 line=[(a,0),(a+.25,.32),(b-.25,.32),(b,0)]
 for j,(A,B) in enumerate(zip(line,line[1:])):
  du=B[0]-A[0];dv=B[1]-A[1];ln=math.hypot(du,dv);frame=F@Matrix(((du/ln,0,-dv/ln,A[0]),(0,1,0,0),(dv/ln,0,du/ln,A[1]),(0,0,0,1)))
  glazing('upper bay '+str(a)+' '+str(j),.09,3.68,ln-.09,5.12,frame,'frontage',white,2 if j==1 else 1)
 bay_slab('sill',line,3.56,3.64,white)
 bay_slab('cap',line,5.14,5.25,dark)
for a,b in [(0.20,5.65),(7.25,9.10)]:
 glazing('shop glazing',a,.86,b,2.56,F,'frontage',dark,3)
 box('brick stallriser',((a+b)/2,.295,-.07),(b-a,.99,.13),F,'frontage',brick)
glazing('front door',5.90,.05,7.02,2.56,F,'frontage',dark,2)
# Recessed square shop window on Cable return and upper lights.
sideholes=[rect(2.4,-.2,5.65,2.56),rect(2.55,3.75,4.7,5.1)]
skin('Cable return',rect(0,-.2,m-1,e),sideholes,S,'rear')
glazing('Cable shop',2.4,.86,5.65,2.56,S,'rear',dark,3);box('Cable tiled stallriser',(4.025,.295,-.07),(3.25,.99,.13),S,'rear',tan)
glazing('Cable upper',2.55,3.75,4.7,5.1,S,'rear',white,2)
# Corner shop door, with tile pilasters and sign; no interior detail.
L=math.sqrt(2);skin('splayed corner lower',rect(0,-.2,L,3.55),[rect(.16,.04,L-.16,2.55)],K,'frontage',tan)
skin('splayed corner upper',rect(0,3.55,L,e),[rect(.16,3.68,L-.16,5.12)],K,'frontage')
glazing('corner door',.16,.04,L-.16,2.55,K,'frontage',dark,1)
# The splayed upper light projects from the wall and has a separate cap and sill.
Kbay=K@Matrix.Translation((0,0,.22));glazing('corner upper',.16,3.68,L-.16,5.12,Kbay,'frontage',white,1)
for x in (.16,L-.16):
 finish('Architecture corner bay return',[(x,3.68,0),(x,5.12,0),(x,5.12,.12),(x,3.68,.12)],[(0,1,2,3)],'frontage',white,K)
box('corner bay sill',(L/2,3.60,.09),(L-.26,.08,.36),K,'frontage',white)
box('corner bay cap',(L/2,5.19,.09),(L-.26,.09,.36),K,'frontage',dark)
# Fascia backing and cornice sit in front of walls, separated from window frame.
for frame,part,a,b in [(F,'frontage',0,front),(S,'rear',2.25,5.9)]:
 box('black fascia',((a+b)/2,2.95,.10),(b-a,.63,.17),frame,part,dark)
 box('fascia cap',((a+b)/2,3.36,.14),(b-a,.15,.24),frame,part,dark)
# Distinct door kick panels and shallow thresholds, isolated from recessed glass.
for frame,part,a,b in [(F,'frontage',5.90,7.02),(K,'frontage',.16,L-.16)]:
 box('door kick panel',((a+b)/2,.35,-.025),(b-a-.12,.46,.07),frame,part,dark)
 box('door threshold',((a+b)/2,.005,.05),(b-a,.05,.27),frame,part,dark)
 box('door handle',(b-.15,1.12,.055),(.045,.19,.07),frame,part,white)
for frame,part,a,b in [(F,'frontage',.2,5.65),(F,'frontage',7.25,9.10),(S,'rear',2.4,5.65)]:
 box('shop sill',((a+b)/2,.82,.055),(b-a+.06,.08,.23),frame,part,dark)
# Authored tile, brick and slate maps repeat in metric UV space.
for material_obj,texture in [(brick,'brick'),(tan,'tile'),(slate,'slate')]:
 node=material_obj.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));material_obj.node_tree.links.new(node.outputs['Color'],material_obj.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
# The 2026 readable fascia is authored lettering, not a photo texture.
sign=material('Jacksons fascia',(.94,.92,.88));tex=sign.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/fascia.png'));sign.node_tree.links.new(tex.outputs['Color'],sign.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
def signage(frame,part,a,b,mat=sign,z0=2.71,z1=3.18,depth=.191):
 o=finish('Architecture fascia lettering',[(a,z0,depth),(b,z0,depth),(b,z1,depth),(a,z1,depth)],[(0,1,2,3)],part,mat,frame)
 for poly in o.data.polygons:
  for li in poly.loop_indices:
   v=frame.inverted()@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers[0].data[li].uv=((v.x-a)/(b-a),(v.y-z0)/(z1-z0))
def sign_material(name):
 mat=material(name,(1,1,1));node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/(name+'.png')));mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']);return mat
side_sign=sign_material('side-fascia');award=sign_material('award');fish_sign=sign_material('fish-sign')
signage(F,'frontage',.15,front-.15);signage(S,'rear',2.32,5.83,side_sign)
# Award panel above corner door, framed in dark joinery, distinct from the main fascia.
box('corner sign board',(L/2,3.02,.08),(L-.17,.94,.14),K,'frontage',dark)
signage(K,'frontage',.13,L-.13,award,2.60,3.42,.155)
# Square projecting sign at the front edge of the corner, visible from both directions.
box('projecting sign support',(.18,3.05,.46),(.07,.07,.90),F,'projecting-sign',dark)
P=F@Matrix(((0,0,-1,.18),(0,1,0,0),(1,0,0,.85),(0,0,0,1)))
box('projecting sign board',(0,3.15,0),(.70,.70,.09),P,'projecting-sign',dark)
signage(P,'projecting-sign',-.31,.31,fish_sign,2.84,3.46,.046)
Pback=P@Matrix(((-1,0,0,0),(0,1,0,0),(0,0,-1,0),(0,0,0,1)));signage(Pback,'projecting-sign',-.31,.31,fish_sign,2.84,3.46,.046)
# Vertically ribbed cap of the sign fascia. Fine strips are removed at Walk.
for frame,part,a,b in [(F,'frontage',0,front),(S,'rear',2.25,5.9)]:
 for j in range(1,int((b-a)/.20)):
  x=a+j*.20;box('fascia rib',(x,3.36,.265),(.018,.13,.012),frame,part,dark)

for im in bpy.data.images:
 if im.source=='FILE':im.pack()
# Restrained service return and party faces, unseen beneath adjacent buildings.
p=[(w,0),(w,m),(0,m),(0,1)];skin('party',[(0,-.2),(dep,-.2),(dep,3.8),(m,4.1),(m,e),(0,e)],[],T@face_matrix((w,0,0),(1,0,0)),'rear')
skin('rear upper',rect(0,4.1,w,e),[],T@face_matrix((w,m,0),(0,1,0)),'rear')
q=[(0,m),(w,m),(w,dep),(0,dep)]
for i,(a,b) in enumerate(zip(q,q[1:]+q[:1])):
 if i in (0,1):continue
 za=4.1 if a[1]==m else 3.8;zb=4.1 if b[1]==m else 3.8
 finish('Shell extension '+str(i),[(*a,-.2),(*b,-.2),(*b,zb),(*a,za)],[(0,1,2,3)],'rear',wall)
for name,p in roofs(D):finish('Shell roof '+name,p,[tuple(range(len(p)))],'roof',slate)
# Dark roof-edge gutters and the single visible Cable-side downpipe.
def tube(name,a,b,r,part='roof',mat=dark):
 from mathutils import Vector
 A=Vector(a);B=Vector(b);axis=(B-A).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u);n=10
 verts=[tuple(p+r*(math.cos(i*math.tau/n)*u+math.sin(i*math.tau/n)*v)) for p in (A,B) for i in range(n)]
 faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(reversed(range(n))),tuple(range(n,n*2))]
 finish('Architecture '+name,verts,faces,part,mat)
tube('Nevill eaves gutter',(1,-.09,e-.02),(w,-.09,e-.02),.055)
tube('Cable eaves gutter',(-.09,1,e-.02),(-.09,m,e-.02),.055)
tube('Cable downpipe',(-.10,6.75,.10),(-.10,6.75,e-.03),.038,'rear')
tube('ridge cap',(3.5,3.7,D['ridge']+.015),(6.9,3.7,D['ridge']+.015),.035,'roof',slate)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.4;sun.rotation_euler=(.4,.5,.4)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/jacksons.blend'))
