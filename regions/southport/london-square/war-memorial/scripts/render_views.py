"""Render the named cameras in the saved model without rebuilding geometry."""
import bpy
import sys
import json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import site_grade
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
scene=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
requested=[arg for arg in args if not arg.startswith('--')]
scene.cycles.samples=72 if '--final' in args else 32
site=json.loads((ROOT/'research/site_layout.json').read_text())
for code,name,z,scale in [('SW','Crossed torches detail',2.698,1.10),
                         ('SW','Remember plaque detail',2.125,2.55),
                         ('NE','They died plaque detail',2.125,2.55),
                         ('SW','Wreath trophy detail',3.75,2.05)]:
    if name not in bpy.data.objects:
        xy=site['colonnades'][code]['centre_site_xy_m']
        data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=scale
        cam=bpy.data.objects.new(name,data)
        bpy.data.collections['90 Lighting and cameras'].objects.link(cam)
        cam.location=(xy[0],xy[1]-18,z)
        cam.rotation_euler=Vector((0,1,0)).to_track_quat('-Z','Y').to_euler()
for name in ('NE end torches and text','SW end remember'):bpy.data.objects[name].data.ortho_scale=4.8
for code,name in [('NE','Victory close view'),('SW','Mourning close view')]:
    xy=site['colonnades'][code]['centre_site_xy_m'];cam=bpy.data.objects[name]
    cam.location=(xy[0],xy[1]+18,2.525)
    target=Vector((xy[0],xy[1]+12.3,2.125))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=3.95
ne=site['colonnades']['NE']['centre_site_xy_m']
# Move the orthographic elevations back along the same viewing ray. Their
# projection stays unchanged, while the bottom rays start above the floor.
sw=site['colonnades']['SW']['centre_site_xy_m']
for name,xy,dx,dy in [('NE inner façade',ne,-81,4.5),('SW inner façade',sw,81,-4.5),
                      ('NE outer façade',ne,84,0),('SW outer façade',sw,-84,0)]:
    cam=bpy.data.objects[name];cam.location=(xy[0]+dx,xy[1]+dy,7.2)
    cam.rotation_euler=(Vector((xy[0],xy[1],2.7))-cam.location).to_track_quat('-Z','Y').to_euler()
for name,position,target,scale in [
    ('Doric capital',(ne[0]-6,ne[1]+5.9,4.30),(ne[0]-1.90,ne[1]+4.90,4.0),1.7),
    ('Pelta trophy detail',(ne[0],ne[1]+18,3.75),(ne[0],ne[1]+12.25,3.75),2.05),
    ('Victory trophy detail',(ne[0]+9,ne[1]+9.85,3.75),(ne[0]+2.28,ne[1]+9.85,3.75),2.05),
    ('Arms ribbon detail',(0,-9,3.06),(0,-1.28,3.06),1.60),
    ('Single globe lamp detail',(ne[0]-8,ne[1]+4.76,2.35),(ne[0]-2.85,ne[1]+7.50,1.7),4.1),
    ('Clustered lamp detail',(24,-18,4.0),(18,-9,2.85),6.5),
    ('Clustered lamp head detail',(22,-15,5.5),(18,-9,4.68),2.65),
    ('Cornice mask pair detail',(ne[0]-6,ne[1]+7.50,5.10),(ne[0]-2.43,ne[1]+7.50,5.015),2.15),
    ('Frieze foliage detail',(ne[0]-7,ne[1]+7.50,4.66),(ne[0]-2.40,ne[1]+7.50,4.66),1.12),
    ('Architectural rosette detail',(ne[0]+.73,ne[1]-17,3.31),(ne[0]+.73,ne[1]-12.35,3.31),.32),
    ('Pedestal salute joints',(0,9,3.06),(0,1.28,3.06),2.85),
    ('Window lintel and rosettes',(ne[0]-8,ne[1]+9.85,3.21),(ne[0]-2.28,ne[1]+9.85,3.21),2.6),
    ('Window exterior surround',(ne[0]-8,ne[1]-9.85,2.0),(ne[0]-2.28,ne[1]-9.85,2.0),4.0),
    ('Salute wreath close view',(0,9,3.06),(0,1.28,3.06),1.55),
    ('Window oblique reveal',(ne[0]-8,ne[1]-12.9,2.5),(ne[0]-2.28,ne[1]-9.85,2.0),4.2),
    ('Obelisk SE pyramid opening',(-2,-5,19.9),(0,0,19.75),2.25),
    ('Obelisk NW pyramid opening',(-2,5,19.9),(0,0,19.75),2.25),
    ('Obelisk cornice light housings',(-4,-7,5.6),(-.25,-.55,4.61),4.0),
    ('Complete obelisk exterior',(-18,-36,14),(0,0,10.25),23.4),
    ('SE shaft masonry',(0,-8,12.3),(0,-.8,12.3),3.25),
    ('SW shaft masonry',(-8,0,6.4),(-.8,0,6.4),3.25),
    ('Complete obelisk northwest',(-18,36,14),(0,0,10.25),23.4),
    ('Obelisk WWII inscription',(-9,0,3.06),(-1.28,0,3.06),1.55)]:
    cam=bpy.data.objects.get(name)
    if cam is None:
        data=bpy.data.cameras.new(name);data.type='ORTHO'
        cam=bpy.data.objects.new(name,data)
        bpy.data.collections['90 Lighting and cameras'].objects.link(cam)
    cam.location=position;cam.data.ortho_scale=scale
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
floor=bpy.data.objects.get('Inspection studio floor')
if floor is None:
    bpy.ops.mesh.primitive_plane_add(size=1000,location=(0,0,-.003))
    floor=bpy.context.object;floor.name='Inspection studio floor'
    for collection in list(floor.users_collection):collection.objects.unlink(floor)
    bpy.data.collections['90 Lighting and cameras'].objects.link(floor)
    floor.data.materials.append(bpy.data.materials['Grey granite paving'])
    floor['purpose']='Inspection renders only; excluded from exported assets'
floor.location.z=-.003
groups={k:bpy.data.collections[v] for k,v in {'site':'00 Site registration and approximate paving','obelisk':'01 Obelisk exterior','NE':'02 North-east colonnade exterior','SW':'03 South-west colonnade exterior','lamps':'04 Clustered lamp standards — placement provisional'}.items()}
views=[('01_ensemble_northwest','Ensemble from NW'),('02_ensemble_southeast','Ensemble from SE'),
       ('03_overhead','Site plan'),('04_ne_colonnade_inner','NE inner façade'),('05_sw_colonnade_inner','SW inner façade'),
       ('06_obelisk_salute','Obelisk salute'),('07_ne_victory_end','NE victory end'),('08_sw_mourning_end','SW mourning end'),
       ('09_ne_torches_text','NE end torches and text'),('10_sw_remember_text','SW end remember'),
       ('11_column_pair','Column pair detail'),('12_obelisk_arms','Obelisk coat of arms'),
       ('13_ne_outer','NE outer façade'),('14_sw_outer','SW outer façade'),('15_capital','Doric capital'),
       ('16_mourning_close','Mourning close view'),('17_victory_close','Victory close view'),
       ('18_crossed_torches','Crossed torches detail'),('19_remember_plaque','Remember plaque detail'),
       ('20_they_died_plaque','They died plaque detail'),('21_wreath_trophy','Wreath trophy detail'),
       ('22_pelta_trophy','Pelta trophy detail'),('23_victory_trophy','Victory trophy detail'),
       ('24_arms_ribbon','Arms ribbon detail'),('25_single_lamp','Single globe lamp detail'),
       ('26_clustered_lamp','Clustered lamp detail'),('27_clustered_lamp_head','Clustered lamp head detail'),
       ('28_cornice_masks','Cornice mask pair detail'),('29_frieze_foliage','Frieze foliage detail'),
       ('30_rosette','Architectural rosette detail'),('31_pedestal_salute_joints','Pedestal salute joints'),
       ('32_window_lintel','Window lintel and rosettes'),
       ('33_window_surround','Window exterior surround'),('34_salute_wreath','Salute wreath close view'),
       ('35_window_oblique','Window oblique reveal'),
       ('36_obelisk_tip_se','Obelisk SE pyramid opening'),
       ('37_obelisk_tip_nw','Obelisk NW pyramid opening'),
       ('38_obelisk_linear_lights','Obelisk cornice light housings'),
       ('39_obelisk_full','Complete obelisk exterior'),
       ('40_shaft_masonry_se','SE shaft masonry'),('41_shaft_masonry_sw','SW shaft masonry'),
       ('42_obelisk_northwest','Complete obelisk northwest'),
       ('43_obelisk_wwii','Obelisk WWII inscription')]
sun=bpy.data.objects['Soft afternoon sun']
default_sun=(sun.rotation_euler.copy(),sun.data.angle,sun.data.energy)
default_world=scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value
for filename,name in views:
    if requested and filename not in requested:continue
    scene.camera=bpy.data.objects[name]
    sun.rotation_euler=default_sun[0];sun.data.angle=default_sun[1];sun.data.energy=default_sun[2]
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=default_world
    if filename[:2] in ('16','17','22','31','34','37','42'):
        # Raking inspection light makes the exterior carving readable over SSH.
        sun.rotation_euler=Vector((.55,-.65,-.52)).to_track_quat('-Z','Y').to_euler()
        sun.data.angle=.09;sun.data.energy=2.8
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
    if filename[:2] in ('12','18','19','20','21','24','30','36','38','39','40','41','43'):
        sun.rotation_euler=Vector((.55,.65,-.52)).to_track_quat('-Z','Y').to_euler()
        sun.data.angle=.09;sun.data.energy=2.8
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
    if filename[:2]=='23':
        sun.rotation_euler=Vector((-.65,.55,-.52)).to_track_quat('-Z','Y').to_euler()
        sun.data.angle=.09;sun.data.energy=2.8
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
    if filename[:2] in ('25','26','27','28','29','32','33','35'):
        sun.rotation_euler=Vector((.55,.65,-.75)).to_track_quat('-Z','Y').to_euler()
        sun.data.angle=.12;sun.data.energy=2.8
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.48
    bpy.data.collections['99 Survey guides — hidden in renders'].hide_render=filename!='03_overhead'
    overview=filename[:2] in ('01','02','03')
    focus='NE' if filename[:2] in ('04','07','09','11','13','15','17','20','22','23','25','28','29','30','32','33','35') else 'SW' if filename[:2] in ('05','08','10','14','16','18','19','21') else 'lamps' if filename[:2] in ('26','27') else 'obelisk'
    site_grade.inspection_floor(floor,focus)
    for key,group in groups.items():group.hide_render=not overview and key!=focus
    floor.hide_render=overview
    scene.render.resolution_x=1600;scene.render.resolution_y=1000
    if filename=='03_overhead':scene.render.resolution_x=1800
    if filename[:2] in ('04','05','13','14'):scene.render.resolution_x=2400;scene.render.resolution_y=800
    if filename[:2] in ('18','19','20','24','25','26','27','30','33','34','35','36','37','43'):scene.render.resolution_x=1600;scene.render.resolution_y=1600
    if filename[:2] in ('21','22','23'):scene.render.resolution_x=1800;scene.render.resolution_y=700
    if filename[:2]=='28':scene.render.resolution_x=1800;scene.render.resolution_y=900
    if filename[:2] in ('29','32'):scene.render.resolution_x=1800;scene.render.resolution_y=800
    if filename[:2]=='31':scene.render.resolution_x=1800;scene.render.resolution_y=1400
    if filename[:2]=='38':scene.render.resolution_x=1800;scene.render.resolution_y=1000
    if filename[:2] in ('39','42'):scene.render.resolution_x=1200;scene.render.resolution_y=2200
    if filename[:2] in ('40','41'):scene.render.resolution_x=1200;scene.render.resolution_y=1600
    scene.render.filepath=str(ROOT/'renders'/(filename+'.png'))
    bpy.ops.render.render(write_still=True)
    print('RENDERED',filename,flush=True)
for group in groups.values():group.hide_render=False
bpy.data.collections['99 Survey guides — hidden in renders'].hide_render=True
floor.hide_render=True
scene.camera=bpy.data.objects['Ensemble from NW']
sun.rotation_euler=default_sun[0];sun.data.angle=default_sun[1];sun.data.energy=default_sun[2]
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=default_world
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
