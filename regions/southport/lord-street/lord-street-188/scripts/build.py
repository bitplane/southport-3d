"""Temporary neutral massing for footprint and silhouette comparison."""
from pathlib import Path
import bpy,os,sys
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(REPO/'lib'))
from southport3d.geometry import Mesh
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
m=bpy.data.materials.new('Pale roof');m.diffuse_color=(.62,.63,.61,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.62,.63,.61,1)
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
def box(name,low,high,col):
 mesh=Mesh(name);mesh.box(tuple((a+b)/2 for a,b in zip(low,high)),tuple(b-a for a,b in zip(low,high)));mesh.finish([m],col)
for name,x0,x1,y0,y1 in [('front-tower',442.7,470.45,-27.3,-9.8),('middle-tower',442,469.49,-56.31,-40.2)]:
 c=collection(name);box('Massing '+name,(x0,y0,0),(x1,y1,18.0),c);box('Setback penthouse '+name,(x0+1.5,y0+1.5,18),(x1-1.5,y1-1.5,20.3),c);box('Top roof '+name,(x0+.7,y0+.7,20.42),(x1-.7,y1-.7,20.55),c)
c=collection('rear-block');box('Massing rear',(450.3,-105.3,0),(462.5,-74.1,8.3),c)
mesh=Mesh('Hipped rear roof');x0,x1=449.95,462.85;y0,y1=-105.65,-73.75;xm=(x0+x1)/2;z=8.3;h=10.0;v=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),(xm,y0+5,h),(xm,y1-5,h)];mesh.add(v,[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)]);mesh.finish([m],c)
# Detached facade prototype: one representative mid-level balcony and joinery.
# It is for comparison only and must be removed before publication.
from southport3d.planar import subtract
from mathutils.geometry import tessellate_polygon
C=collection('prototype')
def material(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);return m
brick=material('Red brick',(.38,.15,.11)); pale=material('Pale stone',(.61,.57,.49)); frame=material('White window frames',(.86,.86,.82));glass=material('Window glass',(.20,.29,.31)); rail=material('Balcony metal',(.12,.14,.14));slab=material('Grey balcony edges',(.34,.35,.33));blue=material('Blue entrance metal',(.025,.10,.15));glassblock=material('Frosted glass blocks',(.44,.56,.54));panel=material('Balcony glass',(.49,.59,.57));panel.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.38;panel.diffuse_color=(.49,.59,.57,.38);panel.surface_render_method='DITHERED'
nt=brick.node_tree; tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/brick.png'));nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
nt=pale.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/stone.png'));nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def face(name,p,mat,y=0):
 me=Mesh(name);vv=[Vector((x,z)) for x,z in p]
 for tri in tessellate_polygon([vv]):
  q=[vv[i] if isinstance(i,int) else i for i in tri];me.add([(550+v.x,y,v.y) for v in q],[(0,1,2)])
 ob=me.finish([mat],C);uv=ob.data.uv_layers.new(name='Metric')
 for f in ob.data.polygons:
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/1.0,v.z/1.2)
def pbox(name,x,y,z,sx,sy,sz,mat):
 me=Mesh(name);me.box((550+x,y,z),(sx,sy,sz));me.finish([mat],C)
holes=[rect(.65,.25,1.8,2.55),rect(3.3,.25,4.8,2.55),rect(6.35,.25,7.08,2.55)]
polys=[rect(0,0,8,3.0)]
for hole in holes:polys=[q for poly in polys for q in subtract(poly,hole)]
for poly in polys:face('Prototype cut brick wall',poly,brick)
for a,b,c,d in [(.65,.25,1.8,2.55),(3.3,.25,4.8,2.55),(6.35,.25,7.08,2.55)]:
 face('Prototype recessed glass',rect(a,b,c,d),glass,-.16)
 # Depth returns own the aperture perimeter; glazing is recessed behind the skin.
 me=Mesh('Prototype reveals');me.add([(550+a,0,b),(550+c,0,b),(550+c,0,d),(550+a,0,d),(550+a,-.16,b),(550+c,-.16,b),(550+c,-.16,d),(550+a,-.16,d)],[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]);me.finish([brick],C)
 for x in (a+.035,c-.035):pbox('Prototype frame stile',x,-.08,(b+d)/2,.07,.12,d-b,frame)
 pbox('Prototype central mullion',(a+c)/2,-.08,(b+d)/2,.07,.12,d-b-.14,frame)
 for z in (b+.035,d-.035):pbox('Prototype frame rail',(a+c)/2,-.08,z,c-a-.14,.12,.07,frame)
pbox('Prototype balcony slab',4,.58,.08,8,1.16,.16,pale)
face('Prototype glass balustrade',rect(.08,.2,7.92,1.25),panel,1.14)
for x in (.08,1.4,2.8,4,5.4,6.8,7.92):pbox('Prototype metal post',x,1.16,.73,.035,.035,1.1,rail)
pbox('Prototype handrail',4,1.16,1.28,8,.05,.05,rail)
for x in (.08,7.92):
 pbox('Prototype side glass',x,.57,.72,.025,1.10,1.0,panel)
 pbox('Prototype side handrail',x,.57,1.28,.05,1.16,.05,rail)
# Apply researched facade to front tower; other elevations remain massing.
from architecture import build_front
col=bpy.data.collections['front-tower'];bpy.data.objects.remove(bpy.data.objects['Massing front-tower'],do_unlink=True)
wall=Mesh('Shell three provisional elevations');wall.add([(442.7,-27.3,0),(470.45,-27.3,0),(470.45,-9.8,0),(442.7,-9.8,0),(442.7,-27.3,18),(470.45,-27.3,18),(470.45,-9.8,18),(442.7,-9.8,18)],[(0,1,5,4),(1,2,6,5),(3,0,4,7)]);wall.finish([brick],col)
build_front(col,(442.7,470.45,-9.8),{'brick':brick,'stone':pale,'white':frame,'glass':glass,'rail':rail,'balcony':panel,'slab':slab,'blue':blue,'glassblock':glassblock})
# Setback white penthouse and stepped roof terrace, calibrated from the front photo.
bpy.data.objects.remove(bpy.data.objects['Setback penthouse front-tower'],do_unlink=True)
a,b=444.2,468.95; yb,yf=-25.8,-11.3
for name,verts in [('rear',[(a,yb,18),(b,yb,18),(b,yb,20.3),(a,yb,20.3)]),('left',[(a,yb,18),(a,yf,18),(a,yf,20.3),(a,yb,20.3)]),('right',[(b,yf,18),(b,yb,18),(b,yb,20.3),(b,yf,20.3)])]:
 me=Mesh('Shell penthouse '+name);me.add(verts,[(0,1,2,3)]);me.finish([pale],col)
poly=[rect(a,18,b,20.3)]
windows=[rect(447,18.5,449.3,20.1),rect(455.3,18.5,457.6,20.1),rect(463.2,18.5,465.5,20.1)]
for h in windows:poly=[q for p in poly for q in subtract(p,h)]
for p in poly:
 me=Mesh('Shell penthouse front');v=[Vector((x,z))for x,z in p]
 for tri in tessellate_polygon([v]):
  q=[v[i]if isinstance(i,int)else i for i in tri];me.add([(t.x,yf,t.y)for t in q],[(0,1,2)])
 me.finish([pale],col)
for h in windows:
 (a0,z0),(a1,_),(_,z1),_=h
 me=Mesh('Glazing penthouse');me.add([(a0,yf-.12,z0),(a1,yf-.12,z0),(a1,yf-.12,z1),(a0,yf-.12,z1)],[(0,1,2,3)]);me.finish([glass],col)
 for x in (a0+.035,a1-.035,(a0+a1)/2):
  me=Mesh('Joinery penthouse');me.box((x,yf-.05,(z0+z1)/2),(.07,.1,z1-z0-.14));me.finish([frame],col)
 for z in (z0+.035,z1-.035):
  me=Mesh('Joinery penthouse');me.box(((a0+a1)/2,yf-.05,z),(a1-a0,.1,.07));me.finish([frame],col)
for p in subtract(rect(442.7,-27.3,470.45,-9.8),rect(444.2,-25.8,468.95,-11.3)):
 me=Mesh('Roof terrace');v=[Vector((x,y))for x,y in p]
 for tri in tessellate_polygon([v]):
  q=[v[i]if isinstance(i,int)else i for i in tri];me.add([(t.x,t.y,18)for t in q],[(0,1,2)])
 me.finish([pale],col)

# Match both towers' observed courtyard/parking elevations and end walls.
from architecture import build_side
mats={'brick':brick,'stone':pale,'white':frame,'glass':glass,'rail':rail,'balcony':panel,'slab':slab,'blue':blue,'glassblock':glassblock}
bpy.data.objects.remove(bpy.data.objects['Shell three provisional elevations'],do_unlink=True)
def rear_facade(col,x0,x1,y):
 before=set(col.objects);build_front(col,(x0,x1,y),mats,entrance=False)
 for ob in set(col.objects)-before:
  for v in ob.data.vertices:v.co.y=2*y-v.co.y
  ob.data.flip_normals()
rear_facade(col,442.7,470.45,-27.3)
build_side(col,442.7,-27.3,-9.8,mats,-1);build_side(col,470.45,-27.3,-9.8,mats)
mid=bpy.data.collections['middle-tower']
for n in ('Massing middle-tower','Setback penthouse middle-tower','Top roof middle-tower'):bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
build_front(mid,(442,469.49,-40.2),mats,entrance=False);rear_facade(mid,442,469.49,-56.31)
build_side(mid,442,-56.31,-40.2,mats,-1);build_side(mid,469.49,-56.31,-40.2,mats)
# The two roof plans match in 3D; copy only the independently modelled crown.
for ob in list(col.objects):
 if ob.name.startswith(('Shell penthouse','Glazing penthouse','Joinery penthouse','Roof terrace','Top roof front-tower')):
  dup=ob.copy();dup.data=ob.data.copy();mid.objects.link(dup);dup.location.x-=.7;dup.location.y-=30.4
# Rear garden block: retain actual dark hipped roof and open surroundings.
from architecture import build_garden
rear=bpy.data.collections['rear-block'];bpy.data.objects.remove(bpy.data.objects['Massing rear'],do_unlink=True)
slate=material('Rear slate roof',(.19,.21,.22));bpy.data.objects['Hipped rear roof'].data.materials.clear();bpy.data.objects['Hipped rear roof'].data.materials.append(slate)
wall=Mesh('Shell rear block obscured elevations');wall.add([(450.3,-105.3,0),(462.5,-105.3,0),(462.5,-74.1,0),(450.3,-74.1,0),(450.3,-105.3,8.3),(462.5,-105.3,8.3),(462.5,-74.1,8.3),(450.3,-74.1,8.3)],[(0,1,5,4),(2,3,7,6)]);wall.finish([brick],rear)
build_garden(rear,462.5,-105.3,-74.1,mats)
from architecture import build_service
build_service(rear,450.3,-105.3,-74.1,mats)
# Two flush rooflights visible on the service-side roof slope in the 3D orbit.
for yy in (-98,-81):
 a,b=452.6,453.5
 def roofz(x):return 8.3+(x-449.95)*1.7/(456.4-449.95)+.035
 corners=[(a,yy-.55,roofz(a)),(b,yy-.55,roofz(b)),(b,yy+.55,roofz(b)),(a,yy+.55,roofz(a))]
 me=Mesh('Roof glazing rear');me.add(corners,[(0,1,2,3)]);me.finish([glass],rear)
 for p,q in zip(corners,corners[1:]+corners[:1]):
  me=Mesh('Fine rooflight frame');me.tube([p,q],.035,sides=6);me.finish([rail],rear)

# Small central roof structures seen in both 3D orbits.
for c,dx,dy in ((col,0,0),(mid,-.7,-30.4)):
 box('Roof headhouse',(452.2+dx,-21.0+dy,20.55),(460.2+dx,-16.2+dy,21.2),c)
# Occupied penthouse terraces sit forward of the inset top floor.
for c,x0,x1,y1 in ((col,442.7,470.45,-9.8),(mid,442,469.49,-40.2)):
 a,b=x0+2.2,x1-2.2;yy=y1-.12;z=18.05
 me=Mesh('Balcony terrace glass');me.add([(a,yy,z),(b,yy,z),(b,yy,z+.95),(a,yy,z+.95)],[(0,1,2,3)]);me.finish([panel],c)
 for i in range(13):
  xx=a+(b-a)*i/12;me=Mesh('Balcony terrace post');me.box((xx,yy,z+.49),(.045,.045,.98));me.finish([rail],c)
 me=Mesh('Balcony terrace handrail');me.box(((a+b)/2,yy,z+.99),(b-a,.05,.05));me.finish([rail],c)
# Projecting layered roof edge, grey fascia and slatted soffit.
for c,x0,x1,y0,y1 in ((col,442.7,470.45,-27.3,-9.8),(mid,442,469.49,-56.31,-40.2)):
 def trim(name,low,high,mat,omit_y=None):
  me=Mesh(name);me.box(tuple((a+b)/2 for a,b in zip(low,high)),tuple(b-a for a,b in zip(low,high)))
  if omit_y is not None:me.faces.pop(omit_y);me.indices.pop(omit_y)
  me.finish([mat],c)
 trim('Roof upper fascia',(x0+.7,y0+.7,20.3),(x1-.7,y1-.7,20.42),rail)
 for inner,outer,sgn in ((y0+1.5,y0+.7,-1),(y1-1.5,y1-.7,1)):
  lo,hi=sorted((inner,outer))
  for i in range(1,49):
   xx=x0+1.5+i*(x1-x0-3)/49;trim('Fine upper soffit slat',(xx-.025,lo,20.20),(xx+.025,hi,20.24),rail,1 if sgn==1 else 3)
 for y,sgn in ((y0,-1),(y1,1)):
  lo,hi=sorted((y,y+sgn*.32));trim('Roof lower fascia',(x0,lo,17.88),(x1,hi,18.04),rail,1 if sgn==1 else 3)
  for i in range(1,55):
   xx=x0+i*(x1-x0)/55;trim('Fine soffit slat',(xx-.025,lo,17.78),(xx+.025,hi,17.82),rail,1 if sgn==1 else 3)
# The detached feature study was rendered separately and must not enter an export.
for ob in list(C.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(C)
# Embed plinths in the shared rough pavement control surface while leaving
# entrance thresholds above it. Heights are estimated, not a surveyed ramp.
bpy.context.view_layer.update()
for collection,offset in ((col,.18),(mid,.18),(rear,.50)):
 for ob in collection.objects:
  if ob.type=='MESH':
   ob.data.transform(Matrix.Translation((0,0,offset))@ob.matrix_world);ob.matrix_world=Matrix.Identity(4);ob.data.update()
# Untextured primitive surfaces receive stable metric UVs before batching.
for collection in (col,mid,rear):
 for ob in collection.objects:
  if ob.type!='MESH' or ob.data.uv_layers:continue
  uv=ob.data.uv_layers.new(name='Metric')
  for face in ob.data.polygons:
   axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
   for li in face.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]]/1.2)
# Validate the detailed authoring scene before consolidating export batches.
from source_checks import validate as validate_source
from batch import digest,batch
bpy.context.view_layer.update();validate_source()
source_digest,source_count=digest([o for o in s.objects if o.type=='MESH'])
for collection in (col,mid,rear):batch(collection)
bpy.context.view_layer.update();batched_digest,batched_count=digest([o for o in s.objects if o.type=='MESH'])
assert (source_digest,source_count)==(batched_digest,batched_count), 'Batch changed checked surface triangles or materials'
s['source_surface_digest']=source_digest;s['source_triangle_count']=source_count
s.render.engine='CYCLES';s.cycles.samples=16;s.world=bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.7,.73,.77,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.6);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));c.data.type='ORTHO';s.collection.objects.link(c);s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/building.blend'))
