"""353 Lord Street: measured plot, recessed gallery and independently authored joinery."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,text_object,face_matrix
from southport3d.conform import conform
from components import rect,cuts,beam,moulding,arc
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];fine=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for n in ('shell','frontage','gallery','verandah'):
 C[n]=bpy.data.collections.new(n);s.collection.children.link(C[n])
def mat(n,c,rough=.7):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
brick=mat('Warm red brick',(.46,.19,.13));stone=mat('Weathered golden sandstone',(.48,.39,.24));white=mat('Painted ivory',(.81,.82,.75));timber=mat('Very dark brown gallery timber',(.055,.036,.029));slate=mat('Weathered blue slate',(.16,.19,.21));back=mat('Rear weathered brick',(.27,.19,.15));glass=mat('Muted grey blue glazing',(.12,.19,.21),.27);shopglass=mat('Dark cafe glazing',(.025,.045,.042),.25);grey=mat('Grey green shop joinery',(.20,.26,.25));blue=mat('Nero blue fascia',(.055,.30,.51));black=mat('Black lettering',(.018,.021,.019));gold=mat('Letter edging',(.53,.47,.31));lead=mat('Lead and asphalt',(.22,.23,.24));canopyglass=mat('Weathered canopy glass',(.41,.50,.50),.35)
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)));F=T@face_matrix((0,0,0),(0,-1,0))
def finish(m,part='shell',material=brick,frame=T):
 if m.name.startswith('Wall '):m=conform({'wall':m})[0]['wall']
 o=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 uv=o.data.uv_layers.new(name='Metric')
 for p in o.data.polygons:
  ax=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[ax[0]],v[ax[1]])
 o['face_frame']=[list(r) for r in frame];o.data.transform(frame);return o

def box(n,c,size,part='frontage',material=white,frame=F):
 m=Mesh(n);m.box(c,size);return finish(m,part,material,frame)
def skin(n,points,part='shell',material=brick,frame=T):
 m=Mesh(n);m.add(points,[tuple(range(len(points)))]);return finish(m,part,material,frame)
def wall(n,poly,holes=(),out=0,material=brick,part='shell'):
 m=Mesh('Wall '+n)
 for p in cuts(poly,holes):m.add([(x,z,out) for x,z in p],[tuple(range(len(p)))])
 for h in holes:
  for a,b in zip(h,h[1:]+h[:1]):m.add([(*a,out),(*b,out),(*b,out-.22),(*a,out-.22)],[(0,1,2,3)])
 return finish(m,part,material,F)
def line(n,a,b,w=.08,d=.10,part='frontage',material=white):
 m=Mesh(n);beam(m,a,b,w,d);return finish(m,part,material,F)
def label(n,body,x,z,out,size,width,material=white):
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
 o=text_object(n,body,(0,0,0),(0,0,1),size,width,font,material,extrude=.003,collection=C['frontage'],fit_bounds=True)
 local=Matrix.Translation((x,z,out))@o.matrix_world.copy();bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);o.data.transform(F@local);o.matrix_world=Matrix.Identity(4)
 if not o.data.uv_layers:o.data.uv_layers.new(name='Lettering')
# True front apertures, open attic gallery, and stepped rear volume.
holes=[rect(.30,-.45,W-.30,3.9),rect(.37,4.38,W-.37,7.73)]
for x in (1.26,2.925,4.59):holes.append(rect(x-.48,8.24,x+.48,10.72))
wall('front lower',rect(0,-.45,W,11.6),holes)
# Rear of gallery remains behind open balcony; no wall blocks the void.
wall('gallery back',rect(0,11.6,W,13.3),[rect(2.35,11.6,3.50,13.1)],out=-1.0,material=timber,part='gallery')
skin('Gallery rear door',[(2.35,11.6,-1.23),(3.5,11.6,-1.23),(3.5,13.1,-1.23),(2.35,13.1,-1.23)],'gallery',glass,F)
for x,rev in ((0,True),(W,False)):
 p=[(x,0,-.45),(x,8.9,-.45),(x,8.9,13.3),(x,0,13.3)];skin('Wall tall side '+str(x),p[::-1] if rev else p,material=back)
# Gable roof extends forward over gallery, its ridge runs into the plot.
for a,b,zA,zB in ((-.09,W/2,13.3,17.25),(W/2,W+.09,17.25,13.3)):
 skin('Slate pitched roof',[(a,-.76,zA),(b,-.76,zB),(b,8.9,zB),(a,8.9,zA)],material=slate)
skin('Wall rear gable',[(0,8.9,7.1),(W,8.9,7.1),(W,8.9,13.3),(W/2,8.9,17.25),(0,8.9,13.3)][::-1],material=back)
for x,rev in ((0,True),(W,False)):
 p=[(x,8.9,3.45),(x,18.9,3.45),(x,18.9,6.5),(x,8.9,7.1)];skin('Wall rear range '+str(x),p[::-1] if rev else p,material=back)
skin('Roof lower rear range',[(0,8.9,7.1),(W,8.9,7.1),(W,18.9,6.5),(0,18.9,6.5)],material=slate)
skin('Wall rear range end',[(0,18.9,3.45),(0,18.9,6.5),(W,18.9,6.5),(W,18.9,3.45)],material=back)
for x,rev in ((0,True),(W,False)):
 p=[(x,8.9,-.45),(x,33,-.45),(x,33,3.45),(x,8.9,3.45)];skin('Wall low rear '+str(x),p[::-1] if rev else p,material=back)
skin('Wall low end',[(0,33,-.45),(0,33,3.45),(W,33,3.45),(W,33,-.45)],material=back)
skin('Roof low rear',[(0,18.9,3.45),(W,18.9,3.45),(W,33,3.45),(0,33,3.45)],material=lead)
# White plaster surround and canted replacement oriel observed in current photographs.
wall('white first floor',rect(.37,4.38,W-.37,7.73),[rect(.62,4.60,W-.62,7.48)],out=.025,material=white,part='frontage')
path=[(.62,.04),(1.25,.58),(4.60,.58),(W-.62,.04)]
for i,((a,o),(b,p)) in enumerate(zip(path,path[1:])):
 skin('Oriel glazing '+str(i),[(a,5.02,o-.06),(b,5.02,p-.06),(b,7.35,p-.06),(a,7.35,o-.06)],'frontage',glass,F)
 skin('Oriel apron '+str(i),[(a,4.6,o),(b,4.6,p),(b,5.02,p),(a,5.02,o)],'frontage',white,F)
 for z,h in ((4.58,.10),(5.03,.075),(6.78,.065),(7.39,.12)):
  line('Oriel horizontal', (a,z,o+.025),(b,z,p+.025),h,.10)
 for t in ([.09,.50,.91] if i==1 else [.5]):
  x=a+(b-a)*t;q=o+(p-o)*t
  line('Oriel mullion',(x,5.06,q+.015),(x,7.34,q+.015),.055,.10)
for x,q in path:line('Oriel corner',(x,4.62,q+.045),(x,7.37,q+.045),.085,.12)
# Pentice cap, brackets and opaque sill close the bay projection.
skin('Oriel base',[(a,4.60,o) for a,o in reversed(path)]+[(.62,4.60,0)],'frontage',white,F)
skin('Oriel cap',[(.55,7.68,0),(W-.55,7.68,0),(W-.55,7.50,.75),(.55,7.50,.75)],'frontage',lead,F)
# Three shouldered head windows with sandstone columns and decorated lintels.
for i,x in enumerate((1.26,2.925,4.59)):
 skin('Upper glazing '+str(i),[(x-.48,8.24,-.20),(x+.48,8.24,-.20),(x+.48,10.72,-.20),(x-.48,10.72,-.20)],'frontage',glass,F)
 for u in (x-.48,x+.48):box('Upper frame',(u,9.48,-.09),(.045,2.48,.10))
 for z in (8.27,9.82,10.69):box('Upper sash',(x,z,-.085),(.96,.055,.10))
 box('Stone sill',(x,8.16,.12),(1.18,.17,.34),material=stone)
 for u in (x-.62,x+.62):
  box('Stone jamb',(u,9.48,.07),(.20,2.40,.24),material=stone)
  box('Stone jamb base',(u,8.35,.16),(.25,.20,.32),material=stone)
  box('Stone capital',(u,10.58,.17),(.30,.23,.36),material=stone)
 # Raised shoulder ends and shallow centre arch: asymmetric shoulder form is observed, not Gothic pointed arch.
 m=Mesh('Shouldered stone head');m.outline([(x-.72,10.70),(x-.72,10.99),(x-.45,10.99),(x-.30,11.18),(x+.30,11.18),(x+.45,10.99),(x+.72,10.99),(x+.72,10.70)],-.01,.24);finish(m,'frontage',stone,F)
for x in (.13,W-.13):box('Red brick pier',(x,7.85,.08),(.22,7.4,.25),material=brick)
for z,h in ((4.23,.15),(7.90,.18),(11.38,.17)):box('Dark string course',(W/2,z,.08),(W-.24,h,.20),material=timber)
# Balcony: genuinely open, with return railings; projecting gable is above it.
box('Gallery floor',(W/2,11.64,.25),(W+.12,.18,1.8),'gallery',timber)
wall('half timber gable',[(0,13.30),(W,13.30),(W/2,17.25)],out=.66,material=white,part='gallery')
for x in (.13,W/2,W-.13):
 box('Gallery upright',(x,12.50,.72),(.18,1.58,.20),'gallery',timber)
for z,h in ((11.84,.15),(12.60,.13),(13.3,.22)):
 box('Gallery horizontal',(W/2,z,.69),(W,h,.25),'gallery',timber)
for i in range(27):
 x=.23+i*(W-.46)/26;box('Gallery baluster',(x,12.21,.68),(.055,.67,.075),'gallery',white)
for x in (.13,W-.13):
 for j in range(7):box('Gallery return baluster',(x,12.21,.60-j*.25),(.055,.67,.055),'gallery',white)
 box('Gallery return rail',(x,12.62,-.22),(.14,.11,1.80),'gallery',timber)
# Gable frame is planted ahead of infill, never coplanar with it.
for a,b in [((0,13.3,.72),(W/2,17.25,.72)),((W/2,17.25,.755),(W,13.3,.755)),((W/2,13.3,.78),(W/2,17.25,.78))]:line('Gable main timber',a,b,.16,.14,'gallery',timber)
for side in (-1,1):
 for k in range(1,6):
  x=W/2+side*k*.43;top=17.25-abs(x-W/2)*3.95/(W/2)
  line('Gable stud',(x,13.39,.795),(x,top-.12,.795),.085,.10,'gallery',timber)
  x2=x+side*.39;z2=13.42+(.9 if k%2 else 1.15)
  # Branching is authored in the detail pass from the reference.
# Current cafe frontage: two angled glazing returns lead to the recessed centre door.
shop_path=[(.30,-.10),(1.66,-.10),(2.40,-.70),(3.45,-.70),(4.19,-.10),(W-.30,-.10)]
for i,((a,o),(b,p)) in enumerate(zip(shop_path,shop_path[1:])):
 skin('Shop glass '+str(i),[(a,.45,o-.045),(b,.45,p-.045),(b,2.97,p-.045),(a,2.97,o-.045)],'frontage',shopglass,F)
 skin('Shop lower panel '+str(i),[(a,.05,o),(b,.05,p),(b,.45,p),(a,.45,o)],'frontage',grey,F)
 for z in (.07,.45,2.98):line('Shop horizontal',(a,z,o+.015),(b,z,p+.015),.075,.09,material=grey)
for x,o in shop_path:box('Shop upright',(x,1.52,o+.015),(.09,2.97,.11),material=grey)
box('Cafe fascia',(W/2,3.47,-.005),(W-.60,.88,.17),material=blue)
box('Cafe subtitle band',(W/2,3.08,.12),(W-.60,.18,.04),material=black)
box('Door threshold',(W/2,-.025,-.43),(1.03,.06,.55),material=lead)
# Verandah registered to rough shared road control, without moving the floor.
from southport3d.terrain import GroundControls
g=GroundControls(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/ground-controls.json')
for k,x in enumerate((.10,W-.10)):
 y=D['y']+x*D['shear_y']-2.4;gx=D['x']+x-2.4*D['shear_x'];base=g.height(gx,y)+.12-D['base_z']
 m=Mesh('Verandah post '+str(k));m.lathe((x,-2.4),[(base,.10),(.35,.10),(.42,.06),(3.33,.055),(3.40,.11),(3.56,.12)],12);finish(m,'verandah',white)
box('Verandah fascia',(W/2,3.70,2.4),(W,.32,.13),'verandah',white)
skin('Verandah glass',[(0,0,4.31),(0,-2.47,3.84),(W,-2.47,3.84),(W,0,4.31)],'verandah',canopyglass)
if fine:exec(compile((ROOT/'scripts/detail.py').read_text(),str(ROOT/'scripts/detail.py'),'exec'))
# Consolidate repeated families before package preparation.
families={}
for o in list(s.objects):
 if o.type=='MESH':families.setdefault((o.users_collection[0].name,o.name.split('.')[0]),[]).append(o)
for (part,n),obs in families.items():
 if len(obs)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=n
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.4,-.5);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=900;s.render.resolution_y=1400;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/caffe-nero.blend'))
