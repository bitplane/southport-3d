"""Jacksons corner; staged neutral massing before elevation details."""
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
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
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
 mesh=Mesh('Architecture '+name);mesh.box(centre,size);return finish(mesh.name,mesh.vertices,mesh.faces,part,mat,frame)
def glazing(name,a,b,c,d,frame,part,material=dark,columns=2):
 finish('Glazing '+name,[(a,b,-.11),(c,b,-.11),(c,d,-.11),(a,d,-.11)],[(0,1,2,3)],part,glass,frame)
 t=.055
 for z in (b,d-t):box(name+' rail',((a+c)/2,z+t/2,-.03),(c-a,t,.12),frame,part,material)
 for x in [a,c-t]+[a+(c-a)*i/columns-t/2 for i in range(1,columns)]:box(name+' post',(x+t/2,(b+d)/2,-.03),(t,d-b-2*t,.12),frame,part,material)
 for i in range(columns):
  aa=a+t if i==0 else a+(c-a)*i/columns+t/2;bb=c-t if i==columns-1 else a+(c-a)*(i+1)/columns-t/2
  box(name+' transom',((aa+bb)/2,b+(d-b)*.72,-.03),(bb-aa,.045,.12),frame,part,material)
F=T@face_matrix((1,0,0),(0,-1,0));S=T@face_matrix((0,m,0),(-1,0,0));K=T@face_matrix((0,1,0),(-1,-1,0));front=w-1
# Each glazing or bay aperture removes its supporting skin; reveals own the side surfaces.
front_open=[rect(.20,-.2,3.45,2.56),rect(3.75,.05,4.72,2.56),rect(4.95,-.2,8.95,2.56)]
bays=[(.35,2.45),(5.10,7.25)]
front_open += [rect(a,3.68,b,5.12) for a,b in bays]
skin('Nevill lower brick',rect(0,-.2,front,2.65),front_open[:3],F,'frontage',brick)
skin('Nevill upper',rect(0,2.65,front,e),front_open[3:],F,'frontage')
for a,b in bays:
 # Three distinct angled faces of each projected upper bay.
 line=[(a,0),(a+.25,-.32),(b-.25,-.32),(b,0)]
 for j,(A,B) in enumerate(zip(line,line[1:])):
  du=B[0]-A[0];dv=B[1]-A[1];ln=math.hypot(du,dv);frame=F@Matrix(((du/ln,0,dv/ln,A[0]),(0,1,0,0),(-dv/ln,0,du/ln,A[1]),(0,0,0,1)))
  glazing('upper bay '+str(a)+' '+str(j),.09,3.68,ln-.09,5.12,frame,'frontage',white,2 if j==1 else 1)
 box('bay sill',((a+b)/2,3.59,-.08),(b-a,.10,.55),F,'frontage',white)
 box('bay cap',((a+b)/2,5.19,-.08),(b-a,.09,.55),F,'frontage',dark)
for a,b in [(0.20,3.45),(4.95,8.95)]:
 glazing('shop glazing',a,.86,b,2.56,F,'frontage',dark,3)
 box('brick stallriser',((a+b)/2,.35,-.07),(b-a,.96,.13),F,'frontage',brick)
glazing('front door',3.75,.05,4.72,2.56,F,'frontage',dark,1)
# Recessed square shop window on Cable return and upper lights.
sideholes=[rect(2.4,-.2,5.65,2.56),rect(2.55,3.75,4.7,5.1)]
skin('Cable return',rect(0,-.2,m-1,e),sideholes,S,'rear')
glazing('Cable shop',2.4,.86,5.65,2.56,S,'rear',dark,3);box('Cable tiled stallriser',(4.025,.35,-.07),(3.25,.96,.13),S,'rear',tan)
glazing('Cable upper',2.55,3.75,4.7,5.1,S,'rear',white,2)
# Corner shop door, with tile pilasters and sign; no interior detail.
L=math.sqrt(2);skin('splayed corner',rect(0,-.2,L,e),[rect(.16,.04,L-.16,2.55),rect(.16,3.68,L-.16,5.12)],K,'frontage',tan)
glazing('corner door',.16,.04,L-.16,2.55,K,'frontage',dark,1);glazing('corner upper',.16,3.68,L-.16,5.12,K,'frontage',white,1)
# Fascia backing and cornice sit in front of walls, separated from window frame.
for frame,part,a,b in [(F,'frontage',0,front),(S,'rear',0,m-1),(K,'frontage',0,L)]:
 box('black fascia',((a+b)/2,2.95,.10),(b-a,.63,.17),frame,part,dark)
 box('fascia cap',((a+b)/2,3.36,.14),(b-a,.15,.24),frame,part,dark)
# The 2026 readable fascia is authored lettering, not a photo texture.
sign=material('Jacksons fascia',(.94,.92,.88));tex=sign.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/fascia.png'));sign.node_tree.links.new(tex.outputs['Color'],sign.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
def signage(frame,part,a,b):
 o=finish('Architecture fascia lettering',[(a,2.71,.191),(b,2.71,.191),(b,3.18,.191),(a,3.18,.191)],[(0,1,2,3)],part,sign,frame)
 for poly in o.data.polygons:
  for li in poly.loop_indices:
   v=frame.inverted()@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers[0].data[li].uv=((v.x-a)/(b-a),(v.y-2.71)/.47)
signage(F,'frontage',.15,front-.15);signage(S,'rear',2.25,5.9)
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
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.4;sun.rotation_euler=(.4,.5,.4)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/jacksons.blend'))
