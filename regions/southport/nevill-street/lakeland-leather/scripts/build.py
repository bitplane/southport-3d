"""355–357 Lord Street: measured frontage, observed oriel and reserved rear uncertainty."""
import json,math,os,sys,re
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,text_object,face_matrix
from southport3d.conform import conform
from components import rect,cuts,ellipse_arch,arc,moulding,beam
from ground_contact import post_base
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('facades','roof','frontage','verandah'):
 C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,c,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough
 return m
stone=material('Honey sandstone',(.46,.39,.25));edge=material('Carved sandstone',(.49,.42,.29));darkstone=material('Weathered mouldings',(.33,.29,.20))
rear=material('Unsurveyed rear masonry',(.40,.35,.29));slate=material('Grey slate',(.18,.20,.21));lead=material('Lead flashings',(.24,.25,.25))
white=material('Ivory painted joinery',(.83,.84,.78),.45);iron=material('White painted cast iron',(.79,.83,.79),.4);green=material('Dark green trim',(.045,.10,.085),.5)
glass=material('Opaque window grey blue',(.15,.21,.23),.24);curtain=material('Oriel pale glass and curtains',(.42,.48,.47),.5);black=material('Recessed shop glazing',(.035,.065,.064),.23)
brown=material('Lakeland brown fascia',(.32,.15,.09));granite=material('Polished grey granite',(.24,.27,.25),.28)
# Deterministic mineral map, never reference pixels.
n=granite.node_tree.nodes;tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/granite.png'));tex.image.pack();granite.node_tree.links.new(tex.outputs['Color'],n['Principled BSDF'].inputs['Base Color'])
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)));F=T@face_matrix((0,0,0),(0,-1,0))
def finish(m,part='facades',mat=None,frame=None):
 if m.name.startswith('Wall '):m=conform({'wall':m})[0]['wall']
 ob=m.finish([mat or stone],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 frame=frame if frame is not None else T;ob['face_frame']=[list(row) for row in frame];ob.data.transform(frame);return ob

def box(name,c,size,part='facades',mat=None,frame=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,mat,frame)
def text(name,body,u,z,out,height,width,part='frontage',mat=white):
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
 ob=text_object('Sign '+name,body,(0,0,0),(0,0,1),height,width,font,mat,extrude=.004,collection=C[part],fit_bounds=True)
 local=Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(F@local);ob.matrix_world=Matrix.Identity(4)
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='Lettering')
def wall(poly,holes,name,back=-.35,front=0):
 m=Mesh('Wall '+name)
 for p in cuts(poly,holes):
  m.add([(u,z,front) for u,z in p],[tuple(range(len(p)))])
  m.add([(u,z,back) for u,z in p],[tuple(reversed(range(len(p))))])
 for p in holes:
  for a,b in zip(p,p[1:]+p[:1]):
   if abs(a[1])+abs(b[1])<1e-8:continue
   m.add([(*a,front),(*b,front),(*b,back),(*a,back)],[(0,1,2,3)])
 return m
holes=[rect(.40,0,6.60,3.9),rect(.67,4.6,6.33,7.16),ellipse_arch(3.5,7.92,8.12,2.5,2.5)]
for u in (1.9,5.1):holes.append(ellipse_arch(u,12.03,13.,1.,1.))
finish(wall(rect(0,0,W,16.3),holes,'front'),frame=F)
# Registered side/rear shell. Unknown openings remain explicitly unrepresented.
for x,rev in [(0,True),(W,False)]:
 m=Mesh('Wall main side '+str(x));p=[(x,0,0),(x,9.2,0),(x,9.2,13.3),(x,0,15.5)];m.add(p,[tuple(reversed(range(4))) if rev else tuple(range(4))]);finish(m,mat=rear)
# Lower rear roof slopes toward the passage; its outline has an observed rear notch.
back_outline=[(0,9.2),(7,9.2),(7,18.8),(2.1,18.8),(2.1,15.5),(0,15.5)]
def rz(x):return 13.3-x*(2.7/7)
for i,(a,b) in enumerate(zip(back_outline,back_outline[1:]+back_outline[:1])):
 if i==0:continue
 m=Mesh('Wall rear range '+str(i));m.add([(a[0],a[1],3.4),(b[0],b[1],3.4),(b[0],b[1],rz(b[0])),(a[0],a[1],rz(a[0]))],[(0,1,2,3)]);finish(m,mat=rear)
# Main rear wall above the descending wing roof.
m=Mesh('Wall main rear');m.add([(0,9.2,13.3),(7,9.2,10.6),(7,9.2,13.3)],[(2,1,0)]);finish(m,mat=rear)
# Ground volume under the range and low roofs beyond; no courtyard invention.
for x,rev in [(0,True),(7,False)]:
 m=Mesh('Wall low side '+str(x));m.add([(x,9.2,0),(x,30.8,0),(x,30.8,3.4),(x,9.2,3.4)],[(3,2,1,0) if rev else (0,1,2,3)]);finish(m,mat=rear)
m=Mesh('Wall low rear');m.add([(0,30.8,0),(0,30.8,3.4),(7,30.8,3.4),(7,30.8,0)],[(0,1,2,3)]);finish(m,mat=rear)
m=Mesh('Roof front plane');m.add([(0,0,15.5),(7,0,15.5),(7,9.2,13.3),(0,9.2,13.3)],[(0,1,2,3)]);finish(m,'roof',slate)
m=Mesh('Roof rear range');m.add([(x,y,rz(x)) for x,y in back_outline],[tuple(range(len(back_outline)))]);finish(m,'roof',slate)
m=Mesh('Roof low rear');m.add([(0,15.5,3.4),(2.1,15.5,3.4),(2.1,18.8,3.4),(7,18.8,3.4),(7,30.8,3.4),(0,30.8,3.4)],[tuple(range(6))]);finish(m,'roof',lead)
m=Mesh('Roof parapet back and cap');m.add([(0,0,16.3),(7,0,16.3),(7,.35,16.3),(0,.35,16.3)],[(0,1,2,3)]);finish(m,'roof',stone)
# Windows are real holes with recessed glazing, never painted on a blocking wall.
for label,u,lo,spring,r in [('great',3.5,7.92,8.12,2.5),('upper left',1.9,12.03,13,1),('upper right',5.1,12.03,13,1)]:
 m=Mesh('Glazing '+label);m.outline(ellipse_arch(u,lo,spring,r,r),-.23,-.18);finish(m,'frontage',glass,F)
# Rounded-corner oriel; the centre remains straight in plan.
def out_at(x):
 if x<1.35:return .08+math.sqrt(max(0,.68**2-(x-1.35)**2))
 if x>5.65:return .08+math.sqrt(max(0,.68**2-(x-5.65)**2))
 return .76
path=[(.67+.68*(1-math.cos(math.pi*i/16)),.08+.68*math.sin(math.pi*i/16)) for i in range(9)]
path += [(5.65,.76)]+[(5.65+.68*math.sin(math.pi*i/16),.08+.68*math.cos(math.pi*i/16)) for i in range(1,9)]
m=Mesh('Glazing curved oriel')
for (a,o),(b,p) in zip(path,path[1:]):m.add([(a,4.6,o-.06),(b,4.6,p-.06),(b,7.16,p-.06),(a,7.16,o-.06)],[(0,1,2,3)])
finish(m,'frontage',curtain,F)
for name,z,extra,reverse in [('base',4.48,.05,True),('balcony floor',7.44,.08,False)]:
 m=Mesh('Oriel horizontal '+name);points=[(x,z,o+extra) for x,o in path]+[(6.33,z,0),(.67,z,0)];m.add(points,[tuple(reversed(range(len(points)))) if reverse else tuple(range(len(points)))]);finish(m,mat=edge,frame=F)
# Recessed display windows and central doorway, with real reveals.
for name,a,b,out in [('left display',.4,2.5,-.18),('entrance',2.5,4.5,-.72),('right display',4.5,6.6,-.18)]:
 m=Mesh('Shop glazing '+name);m.add([(a,0,out+.03),(b,0,out+.03),(b,3.,out+.03),(a,3.,out+.03)],[(0,1,2,3)]);finish(m,'frontage',black,F)
for x in (2.5,4.5):
 m=Mesh('Shop recess return');m.add([(x,0,-.15),(x,0,-.69),(x,3.,-.69),(x,3.,-.15)],[(0,1,2,3) if x==2.5 else (3,2,1,0)]);finish(m,'frontage',black,F)
box('Shop fascia',(3.5,3.45,-.03),(6.2,.90,.18),'frontage',green)
box('Shop threshold',(3.5,-.025,-.45),(2,.05,.6),'frontage',darkstone)
# Canopy massing retains posts and open access at every viewing level.
for k,x in enumerate((.12,1.9,5.1,6.88)):
 m=Mesh('Verandah column '+str(k));m.lathe((x,-2.40),[(post_base(D,x),.11),(.25,.11),(.32,.075),(3.05,.065),(3.18,.12),(3.30,.14)],16);finish(m,'verandah',iron,F@Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1))))
box('Verandah fascia',(3.5,3.5,2.40),(7,.34,.13),'verandah',iron)
# Translucency is omitted deliberately: pale blue-grey glass is consistent in baked levels.
canopyglass=material('Canopy pale weathered glass',(.45,.56,.57),.28)
m=Mesh('Verandah glass roof');m.add([(0,0,4.32),(7,0,4.32),(7,-2.5,3.65),(0,-2.5,3.65)],[(3,2,1,0)]);finish(m,'verandah',canopyglass)
# Detail is authored after the shape comparison.
if DETAIL:
 exec(compile((ROOT/'scripts/detail.py').read_text(),str(ROOT/'scripts/detail.py'),'exec'))
# Batch repeated families for efficient deterministic bakes.
families={}
for ob in list(s.objects):
 if ob.type=='MESH':families.setdefault((ob.users_collection[0].name,re.sub(r'\.\d{3}$','',ob.name)),[]).append(ob)
for (part,name),objects in families.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=name
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.4,-.5);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1100;s.render.resolution_y=1500;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/lakeland-leather.blend'))
