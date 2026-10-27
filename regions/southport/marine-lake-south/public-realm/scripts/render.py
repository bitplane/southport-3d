"""Bounded plan and obliques; exported neighbourhood reviewed separately."""
from pathlib import Path
import math,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
s=bpy.context.scene;s.camera.data.clip_end=10000
requested=set(sys.argv[sys.argv.index('--final')+1:]) if '--final' in sys.argv else set()
for name,pos,target,scale in [('venetian-reference-oblique',(-268.065843,350.912989,18),(-289.253215,393.352301,0),50),('venetian-snag',(-284.967628,368.223911,7.349219),(-285.721635,374.756765,1.137140),10),('venetian-along',(-302.6,487.4,1.84),(-291.4,408.2,1),90),('venetian-kings-landing',(-260,318,9),(-281,335,.4),45),('venetian-stair',(-284,484,6),(-298,479,-.3),18),('venetian-landing',(-320,470,8),(-302,478,0),34),('venetian-lower',(-315,466,1.5),(-301,478,-.8),35),('venetian-plan',(-290,410,400),(-290,410,0),200),('venetian-side-a',(-480,410,12),(-290,410,0),190),('venetian-side-b',(-100,410,12),(-290,410,0),190),('venetian',(-400,340,18),(-290,410,1),185),('plan',(-390,490,1800),(-390,490,0),1100),('oblique',(-1600,-900,1500),(-390,490,0),1300),('lido',(-800,50,300),(-400,390,1),480),('esplanade',(-1000,200,180),(-640,350,2),400)]:
 if requested and name not in requested:continue
 s.camera.data.type='PERSP' if name in ('venetian-along','venetian-snag','venetian-reference-oblique') else 'ORTHO'
 if name in ('venetian-along','venetian-reference-oblique'):s.camera.data.lens=35
 if name=='venetian-snag':
  s.render.resolution_x=1600;s.render.resolution_y=775
  s.camera.data.angle=2*math.atan(math.tan(math.radians(25))*1600/775)
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
# Isolated fitting preview, generated after the ordinary comparison views.
# It is never saved into the master or exported as scene geometry.
import os,sys
if os.environ.get('VENETIAN_FITTING_PREVIEW')=='1':
 sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
 from venetian_fittings import panel_prototype
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 col=bpy.data.collections.new('Prototype');s.collection.children.link(col)
 def material(name,rgb):
  m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1);return m
 cream=material('Paint cream',(.77,.75,.61));green=material('Paint green',(.045,.28,.105));timber=material('Timber',(.29,.24,.19));globe=material('Globe',(.9,.89,.8));socket=material('Lamp socket',(.035,.045,.035))
 parts=panel_prototype()
 for key,m in parts.items():
  if key in ('rails','balusters'):m.vertices=[(x+.225,y,z)for x,y,z in m.vertices]
  ob=m.finish([green if key=='column' else cream],col)
  if key in ('column','balusters'):
   for face in ob.data.polygons:face.use_smooth=True
 from southport3d.geometry import Mesh
 floor=Mesh('Prototype deck');floor.box((1.6,0,-.12),(4,2,.24));floor.finish([timber],col)
 # One observed globe at the foreground standard; not a distribution pattern.
 mount=Mesh('Prototype lamp socket');mount.lathe((0,0),[(-.12,.085),(-.08,.085)],segments=24);mount.vertices=[(zz,yy,2.57+xx) for xx,yy,zz in mount.vertices];mount.finish([socket],col)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.17,location=(-.27,0,2.57));bpy.context.object.data.materials.append(globe)
 for face in bpy.context.object.data.polygons:face.use_smooth=True
 sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.45,-.3,-.7);s.collection.objects.link(sun)
 camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(camera);s.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=5.5;camera.location=(4,-5,3.2);camera.rotation_euler=(Vector((1.4,0,1.3))-camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(ROOT/'renders'/'venetian-fitting-prototype.png');bpy.ops.render.render(write_still=True)
