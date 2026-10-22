"""Check the exported asset structurally and by importing it into Blender."""
import bpy
import json
import math
import struct
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
path=ROOT/'models/london-square-exterior.glb'
data=path.read_bytes()
magic,version,total=struct.unpack_from('<4sII',data,0)
assert magic==b'glTF' and version==2 and total==len(data),'Invalid GLB container'
length,kind=struct.unpack_from('<I4s',data,12)
assert kind==b'JSON'
gltf=json.loads(data[20:20+length])
assert not any('uri' in b for b in gltf.get('buffers',[])),'GLB must be self-contained'
assert all('bufferView' in image for image in gltf.get('images',[])),'Textures must be embedded'
assert gltf.get('images'),'Baked stone textures missing'
meshes=gltf['meshes'];triangles=0
for mesh in meshes:
    for prim in mesh['primitives']:
        if 'indices' in prim:triangles+=gltf['accessors'][prim['indices']]['count']//3
        assert 'POSITION' in prim['attributes']
        assert 'NORMAL' in prim['attributes']
        acc=gltf['accessors'][prim['attributes']['POSITION']]
        assert all(math.isfinite(v) for v in acc['min']+acc['max'])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(path))
scene=bpy.context.scene
columns=[o for o in scene.objects if 'fluted Doric column' in o.name]
assert len(columns)==32,f'Expected 32 columns, got {len(columns)}'
assert len(set(o.data.name for o in columns))==1,'Columns must retain their shared mesh'
# Probe actual exported shaft geometry instead of relying on metadata.
shaft_diameters={};sample=columns[0]
vertices=[sample.matrix_world@v.co for v in sample.data.vertices]
for label,z,expected in [('lower',.55,.48),('upper',3.74,.40)]:
    radial=[math.hypot(v.x-sample.matrix_world.translation.x,v.y-sample.matrix_world.translation.y)
            for v in vertices if abs(v.z-z)<.035]
    assert radial,'Column shaft probe found no vertices'
    diameter=2*max(radial);assert abs(diameter-expected)<.025,(label,diameter)
    shaft_diameters[label]=diameter
# The plain neck must be an actual cylindrical field, with a projecting lower
# annulus and a wider echinus; metadata alone cannot establish this correction.
capital_radii={}
inverse=sample.matrix_world.inverted()
axis=sample.matrix_world.translation
for z in (3.858,3.905,3.945,4.028):
    origin=Vector((axis.x+1,axis.y,z))
    ok,q,n,index=sample.ray_cast(inverse@origin,inverse.to_3x3()@Vector((-1,0,0)))
    assert ok,('Capital section absent',z)
    p=sample.matrix_world@q
    capital_radii[str(z)]=math.hypot(p.x-axis.x,p.y-axis.y)
assert abs(capital_radii['3.905']-capital_radii['3.945'])<.0003,'Plain capital neck replaced by rings/taper'
assert .010<capital_radii['3.858']-capital_radii['3.905']<.017,'Lower annulus missing'
assert capital_radii['4.028']-capital_radii['3.945']>.035,'Echinus flare missing'
lion_masks=[o for o in scene.objects if 'mask_id' in o]
expected_masks={f'{code}_{face}_{i:02}' for code in ('NE','SW') for face in ('NE','SW') for i in range(1,13)}
assert {o['mask_id'] for o in lion_masks}==expected_masks,'Missing cornice masks / end-bay pairs'
assert len(set(o.data.name for o in lion_masks))==1,'Cornice masks must share one mesh'
for ob in lion_masks:
    face=ob['mask_id'].split('_')[1]
    outward=(ob.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    assert outward.dot(Vector((1 if face=='NE' else -1,0,0)))>.999,ob.name
single_lamps=[o for o in scene.objects if o.get('lamp_type')=='single']
cluster_lamps=[o for o in scene.objects if o.get('lamp_type')=='cluster']
assert len(single_lamps)==8 and len(cluster_lamps)==4,'Lamp counts differ from exterior sources'
for group in (single_lamps,cluster_lamps):assert len(set(o.data.name for o in group))==1
support=next(o for o in scene.objects if o.name.startswith('Continuous paving beneath clustered lamps'))
for ob in cluster_lamps:
    bottom=min((ob.matrix_world@Vector(v)).z for v in ob.bound_box)
    inv=support.matrix_world.inverted()
    for dx,dy in [(0,0)]+[(x,y) for x in (-.39,.39) for y in (-.39,.39)]:
        origin=Vector((ob.matrix_world.translation.x+dx,ob.matrix_world.translation.y+dy,bottom+1))
        ok,location,normal,index=support.ray_cast(inv@origin,inv.to_3x3()@Vector((0,0,-1)))
        assert ok and abs((support.matrix_world@location).z-bottom)<.001,(ob.name,'Pedestal lacks paving contact')
globe_checks={}
for kind,ob,centres,radius in [
    ('single',single_lamps[0],[(0,0,2.942)],.218),
    ('cluster',cluster_lamps[0],[(0,0,5.465)]+[(.66*math.cos(i*math.pi/2),.66*math.sin(i*math.pi/2),4.075) for i in range(4)],.283)]:
    slots=[i for i,slot in enumerate(ob.material_slots) if slot.material and slot.material.name.startswith('Opaque ivory lamp globes')]
    globe_vertex_ids={i for p in ob.data.polygons if p.material_index in slots for i in p.vertices}
    assert globe_vertex_ids,'Opaque globe geometry missing'
    counts=[0]*len(centres)
    for index in globe_vertex_ids:
        p=ob.matrix_world@ob.data.vertices[index].co-ob.matrix_world.translation
        distances=[(p-Vector(c)).length for c in centres]
        nearest=min(range(len(centres)),key=lambda k:distances[k])
        assert distances[nearest]<radius+.003,(kind,'Globe outside expected geometric envelope')
        counts[nearest]+=1
    assert min(counts)>200,(kind,counts,'Each physical globe needs a complete surface')
    assert ob.get('globe_count')==len(centres)
    globe_checks[kind]={'sphere_count':len(centres),'vertices_per_globe':counts}
lamp_plinths=[o for o in scene.objects if o.name.startswith('Bromsgrove lamp stone plinth')]
assert len(lamp_plinths)==8
for obj in lamp_plinths:
    bottom=min((obj.matrix_world@Vector(v)).z for v in obj.bound_box)
    top=max((obj.matrix_world@Vector(v)).z for v in obj.bound_box)
    centre=obj.matrix_world@Vector((sum(v[0] for v in obj.bound_box)/8,sum(v[1] for v in obj.bound_box)/8,0))
    pavement=-.0075-.022*centre.y
    assert bottom<pavement<top,(obj.name,'Plinth must extend through local sloped pavement')
    assert abs(top-.35)<.001,(obj.name,'Lamp cap height differs from revised base')
    candidates=sorted(single_lamps,key=lambda o:(o.matrix_world.translation.xy-centre.xy).length)
    lamp_bottom=min((candidates[0].matrix_world@Vector(v)).z for v in candidates[0].bound_box)
    assert abs(lamp_bottom-top)<.012,(obj.name,'Iron feet must rest on cap',lamp_bottom,top)
# Check actual terrain and column-floor contact after GLB conversion.
ground=next(o for o in scene.objects if o.name.startswith('Working site ground'))
levels=[]
for y in (-10,10):
    inv=ground.matrix_world.inverted()
    ok,q,n,index=ground.ray_cast(inv@Vector((45,y,2)),inv.to_3x3()@Vector((0,0,-1)))
    assert ok
    levels.append((ground.matrix_world@q).z)
assert abs((levels[1]-levels[0])/20+.022)<.00001,'NW pavement fall lost in export'
end_feet=[o for o in scene.objects if o.name.startswith('End elevation pilasters and panel frame')]
assert len(end_feet)==4
for ob in end_feet:
    sx=1 if sum(v.co.x for v in ob.data.vertices)>0 else -1
    ok,q,n,index=ob.ray_cast(Vector((sx*13,0,.66)),Vector((-sx,0,0)))
    assert ok,(ob.name,'Base moulding missing above chamber plinth')
    ok,q,n,index=ob.ray_cast(Vector((sx*13,0,.40)),Vector((-sx,0,0)))
    assert not ok,(ob.name,'Old low moulding protrudes across chamber plinth')
base_contacts=0
for col in columns:
    steps=next(o for o in scene.objects if o.name.startswith(col.name[:2]+' central entrance steps'))
    inv=steps.matrix_world.inverted();axis=col.matrix_world.translation
    # Off the deliberate tread joints, beneath the actual column axis.
    ok,q,n,index=steps.ray_cast(inv@Vector((axis.x,axis.y,.4)),inv.to_3x3()@Vector((0,0,-1)))
    assert ok,(col.name,'Missing stone floor below column')
    top=(steps.matrix_world@q).z
    foot=min((col.matrix_world@v.co).z for v in col.data.vertices)
    assert abs(top-foot)<.001,(col.name,'Column floats or sinks into floor',top,foot)
    base_contacts+=1
points=[o.matrix_world@Vector(v) for o in scene.objects if o.type=='MESH' for v in o.bound_box]
minimum=[min(p[i] for p in points) for i in range(3)]
maximum=[max(p[i] for p in points) for i in range(3)]
assert abs(maximum[2]-20.574)<.015,maximum
assert 115.9<maximum[0]-minimum[0]<116.1,'Site width or units changed in export'
colonnade_plan_checks={}
for code in ('NE','SW'):
    part=[o for o in columns if o.name.startswith(code)]
    assert len(part)==16
    assert abs(max((o.matrix_world@Vector(v)).z for o in part for v in o.bound_box)-4.142)<.02
    roof=next(o for o in scene.objects if o.name.startswith(code+' stepped architrave'))
    inv=roof.matrix_world.inverted()
    for col in part:
        axis=col.matrix_world.translation
        origin=Vector((axis.x,axis.y,4.13))
        ok,q,n,index=roof.ray_cast(inv@origin,inv.to_3x3()@Vector((0,0,1)))
        assert ok and abs((roof.matrix_world@q).z-4.142)<.0005,(col.name,'Column and entablature do not meet')
    axes=[inv@o.matrix_world.translation for o in part]
    expected_x=[a+d for a in (-4.5,-1.5,1.5,4.5) for d in (-.4,.4)]
    assert sorted(round(p.x,3) for p in axes)==sorted(expected_x*2),(code,'Exported bay/pair spacing changed')
    assert sorted(round(p.y,3) for p in axes)==[-1.9]*8+[1.9]*8
    frieze=next(o for o in scene.objects if o.name.startswith(code+' stepped entablature'))
    setbacks=[]
    for sx in (-1,1):
        for sy in (-1,1):
            depths=[]
            for x in (8.05,8.25):
                ok,q,n,index=frieze.ray_cast(Vector((sx*x,sy*3,4.875)),Vector((0,-sy,0)))
                assert ok,(code,'Roof return missing',sx,sy,x)
                depths.append(q.y*sy)
            setbacks.append(depths[0]-depths[1])
            assert abs(setbacks[-1]-.12)<.0002,(code,'Central roof projection absent',setbacks[-1])
    cornice=next(o for o in scene.objects if o.name.startswith(code+' stepped cornice'))
    dims=[max(v.co[i] for v in cornice.data.vertices)-min(v.co[i] for v in cornice.data.vertices) for i in (0,1)]
    assert abs(dims[0]-24.6)<.002 and abs(dims[1]-4.9)<.002,(code,'Cornice outside published envelope',dims)
    parapet=next(o for o in scene.objects if o.name.startswith(code+' stepped parapet ashlar'))
    assert abs(max((parapet.matrix_world@v.co).z for v in parapet.data.vertices)-5.54)<.002
    colonnade_plan_checks[code]={'column_axes_checked':len(axes),'roof_returns_m':setbacks,
                                'maximum_cornice_length_depth_m':dims,'top_m':5.54}
inscriptions=json.loads((ROOT/'research/inscriptions_built.json').read_text())
full_spec=json.loads((ROOT/'research/modelling_spec.json').read_text())
spec=full_spec['exterior_inscriptions']
built=[v['text'] for v in inscriptions]
expected=[]
for key in ('NE_inner_SW','NE_outer_NE','SW_inner_NE','SW_outer_SW','NE_NW_date','SW_NW_date','obelisk_NW_date'):
    expected.append(spec[key])
for key in ('NE_SE_panel','SW_SE_panel','obelisk_NW','obelisk_SW'):expected.extend(spec[key])
expected.append('—')  # Short rule beneath CHRIST CHURCH in the SW photograph.
assert sorted(built)==sorted(expected),'Inscription content differs from reviewed exterior specification'
import wwii_roundel
wwii_check=wwii_roundel.validate(scene)
panels={o['panel_id']:o for o in scene.objects if 'panel_id' in o}
assert set(panels)==set(full_spec['trophy_panel_map']),'Trophy identities missing from exported scene'
for key,obj in panels.items():
    code,end,face=key.split('_')
    outward=(obj.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    expected_normal=Vector((0,1 if end=='NW' else -1,0)) if face=='end' else Vector((1 if face=='NE' else -1,0,0))
    assert outward.dot(expected_normal)>.999,(key,tuple(outward))
assert 'victory' in panels['NE_NW_NE'].data.name.lower(),'Garden-facing NW window has incorrect trophy'
walls=[o for o in scene.objects if o.type=='MESH' and 'chamber ashlar' in o.name]
from colonnade_envelope import pier_end_surface_count
pier_end_surfaces=[]
for wall in walls:
    sign=1 if wall['window_chamber_centre_x']>0 else -1
    for sy in (-1,1):
        count=pier_end_surface_count(wall.data,sign,sy)
        assert count==1,(wall.name,sy,'Coincident exposed pier surfaces',count)
        pier_end_surfaces.append({'wall':wall.name,'side':sy,'surfaces':count})
def hit_wall(point,outward):
    origin=point+outward*.5;hits=[]
    for wall in walls:
        inverse=wall.matrix_world.inverted()
        ok,local,normal,index=wall.ray_cast(inverse@origin,(inverse.to_3x3()@(-outward)).normalized())
        if ok:
            world=wall.matrix_world@local
            distance=(origin-world).dot(outward)
            if distance>=0:hits.append((distance,world))
    assert hits,'No ashlar behind trophy probe'
    return min(hits,key=lambda v:v[0])[1]
recess_depths={}
for key,obj in panels.items():
    n=(obj.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    inside=obj.matrix_world@Vector((.98,.285,0))
    outside=obj.matrix_world@Vector((1.30,.285,0))
    inner=(hit_wall(inside,n)-inside).dot(n)
    outer=(hit_wall(outside,n)-outside).dot(n)
    depth=outer-inner
    assert .050<depth<.080,(key,depth,'Trophy field must be cut into ashlar')
    recess_depths[key]=depth
figures=[o for o in scene.objects if 'traced continuous surface' in o.name and
         (o.name.startswith('Mourning figure') or o.name.startswith('Victory Britannia'))]
assert len(figures)==2,'Both refined exterior figures must survive GLB export'
assert any(o.get('inscription')=='PATRIA' for o in figures),'PATRIA carving metadata lost'
torches=[o for o in scene.objects if o.name.startswith('Crossed inverted torches — traced continuous surface')]
assert len(torches)==2,'Both exterior traced torch reliefs must survive export'
assert len(set(o.data.name for o in torches))==1,'Repeated torch design should share one mesh'
wreaths=[o for o in scene.objects if o.name.startswith('Classical trophy wreath — traced continuous surface')]
assert len(wreaths)==6,'Six SW wreath trophies required'
assert len(set(o.data.name for o in wreaths))==1,'Repeated wreath design should share one mesh'
trophy_counts={}
for motif in ('pelta','victory','wreath'):
    expected_count=sum(p['motif']==motif for p in full_spec['trophy_panel_map'].values())
    traced=[o for o in panels.values() if o.name.startswith('Classical trophy '+motif+' — traced continuous surface')]
    assert len(traced)==expected_count,(motif,len(traced),expected_count)
    assert len(set(o.data.name for o in traced))==1,(motif,'Repeated trophy mesh must be shared')
    trophy_counts[motif]=len(traced)
arms=[o for o in scene.objects if o.name.startswith('Southport arms — traced continuous surface')]
assert len(arms)==1 and arms[0].get('inscription')=='SALVS POPVLI','Traced heraldry / motto missing'
assert not any(o.name.startswith('Arms motto ') for o in scene.objects),'Old floating motto glyphs survived'
arms_trace=json.loads((ROOT/'research/relief-data/southport-arms-traces.json').read_text())
assert ''.join(g['letter'] for g in arms_trace['glyphs'])=='SALVSPOPVLI'
assert min(g['seated_on_ribbon_fraction'] for g in arms_trace['glyphs'])>.99

# Verify the physical settings of the newly traced small floral carvings.
flora={kind:[o for o in scene.objects if o.get('floral_kind')==kind]
       for kind in ('frieze-foliage','architectural-rosette')}
assert len(flora['frieze-foliage'])==8 and len(flora['architectural-rosette'])==24
floral_recess_depths=[];rosette_support_offsets=[]
def support_offset(ob,u,v):
    support=bpy.data.objects[ob['support_object']]
    point=ob.matrix_world@Vector((u,v,0))
    n=(ob.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    inv=support.matrix_world.inverted()
    ok,local,normal,index=support.ray_cast(inv@(point+n*.2),inv.to_3x3()@(-n))
    assert ok,(ob.name,'Missing support stone')
    return (support.matrix_world@local-point).dot(n)
for kind,objects in flora.items():
    assert len(set(o.data.name for o in objects))==1,(kind,'Repeated mesh not shared')
    for ob in objects:
        if kind=='frieze-foliage':
            depth=support_offset(ob,.45,.10)-support_offset(ob,.38,.10)
            assert abs(depth-.018)<.0002,(ob.name,depth)
            floral_recess_depths.append(depth)
        else:
            assert ob.get('petals')==12
            offset=support_offset(ob,0,0)
            assert abs(offset-.002)<.0002,(ob.name,'Floating rosette',offset)
            rosette_support_offsets.append(offset)
            assert max(math.hypot(v.co.x,v.co.y) for v in ob.data.vertices)<.0871,'Empty background sliver survived'

# Mortar beds must remain actual cuts after GLB triangulation and import.
from pedestal_joints import COURSES,CENTRE_Z,face_segments
from geometry import face_matrix
body=bpy.data.objects['Square obelisk pedestal'];joint_depths=[]
assert body.get('masonry_channel_count')==26
body_inv=body.matrix_world.inverted()
for face,normal in [('NW',(0,1,0)),('SE',(0,-1,0)),('NE',(1,0,0)),('SW',(-1,0,0))]:
    n=Vector(normal);mat=face_matrix(n*1.275+Vector((0,0,CENTRE_Z)),n)
    for a,b in face_segments(face):
        u,v=((1.02,a[1]) if abs(a[1]-b[1])<1e-7 else (a[0],(a[1]+b[1])/2))
        point=mat@Vector((u,v,0))
        ok,local,hit_n,index=body.ray_cast(body_inv@(point+n*.1),body_inv.to_3x3()@(-n))
        assert ok,(face,'No mortar channel floor')
        depth=(point-body.matrix_world@local).dot(n)
        assert abs(depth-.003)<.0002,(face,u,v,depth)
        joint_depths.append(depth)
border_crossings=0
for face in ('NW','SE','SW'):
    border=bpy.data.objects['Obelisk '+face+' roundel border']
    for z in COURSES[:2]:
        v=z-CENTRE_Z
        for sign in (-1,1):
            u=sign*math.sqrt(.647**2-v*v)
            ok,*_=border.ray_cast(Vector((u,v,.1)),Vector((0,0,-1)))
            assert not ok,(face,'Mortar gap closed across circular moulding')
            vn=v+.009;un=sign*math.sqrt(.647**2-vn*vn)
            ok,*_=border.ray_cast(Vector((un,vn,.1)),Vector((0,0,-1)))
            assert ok,(face,'Adjacent moulding was damaged')
            border_crossings+=1
arm_joint_heights=[]
for z in COURSES[:2]:
    v=z-CENTRE_Z
    ok,local,normal,index=arms[0].ray_cast(Vector((0,v,.1)),Vector((0,0,-1)))
    assert ok and local.z<.003,(z,'Masonry seam did not cross heraldry',local)
    arm_joint_heights.append(local.z)
    adjacent=[]
    for dv in (-.010,.010):
        ok,q,normal,index=arms[0].ray_cast(Vector((0,v+dv,.1)),Vector((0,0,-1)))
        if ok:adjacent.append(q.z)
    assert max(adjacent)>.010,'Carving next to mortar seam was lost'
underline=next(i for i in inscriptions if i['name']=='Obelisk salute 5')
assert underline['text']=='—' and abs(underline['height_m']-.006)<1e-7
ux,uy,uz=underline['origin_local']
ok,q,normal,index=body.ray_cast(body_inv@Vector((ux,1.38,uz)),body_inv.to_3x3()@Vector((0,-1,0)))
assert ok and 1.267<q.y<1.271,('Salute underline cut missing',q)
for z in (uz-.012,uz+.012):
    ok,q,normal,index=body.ray_cast(body_inv@Vector((ux,1.38,z)),body_inv.to_3x3()@Vector((0,-1,0)))
    assert ok and abs(q.y-1.275)<.0002,('Oversized underline remains',q)

# Check the actual opening, including the formerly obstructed window head.
depsgraph=bpy.context.evaluated_depsgraph_get();window_rays=0
chambers=[o for o in scene.objects if 'window_chamber_centre_x' in o]
assert len(chambers)==4
for wall in chambers:
    x=wall['window_chamber_centre_x'];mat=wall.matrix_world
    for sign in (-1,1):
        direction=mat.to_3x3()@Vector((0,-sign,0))
        for u in (-.48,0,.48):
            for z in (1.26,2.20,3.00,3.086):
                point=mat@Vector((x+u,sign*2.8,z))
                ok,*_=scene.ray_cast(depsgraph,point,direction,distance=.95)
                assert not ok,(wall.name,sign,u,z,'Exterior window aperture obstructed')
                window_rays+=1
        for u in (-.71,.71):
            point=mat@Vector((x+u,sign*2.8,3.061))
            ok,hit,n,index,obj,matrix=scene.ray_cast(depsgraph,point,direction,distance=.95)
            assert ok and obj.get('window_part')=='individual capital',(wall.name,sign,u,'Separate capital missing')
capitals=[o for o in scene.objects if o.get('window_part')=='individual capital']
assert len(capitals)==16
aprons=[o for o in scene.objects if o.name.startswith('Window apron with recessed blank field')]
assert len(aprons)==8
apron_depths=[]
for ob in aprons:
    corners=[Vector(v) for v in ob.bound_box]
    x=(min(v.x for v in corners)+max(v.x for v in corners))/2
    y=(min(v.y for v in corners)+max(v.y for v in corners))/2
    sign=1 if y>0 else -1;heights=[]
    for u in (0,.49):
        ok,q,n,index=ob.ray_cast(Vector((x+u,y+sign*.2,.725)),Vector((0,-sign,0)))
        assert ok,(ob.name,'Apron field missing')
        heights.append(q.y*sign)
    depth=heights[1]-heights[0]
    assert abs(depth-.005)<.0002,(ob.name,'Blank apron recess incorrect',depth)
    apron_depths.append(depth)
salute=[o for o in scene.objects if o.name.startswith('Salute laurel wreath — traced continuous surface')]
assert len(salute)==1 and salute[0].get('leaf_count')==63
wreath_trace=json.loads((ROOT/'research/relief-data/salute-wreath-traces.json').read_text())
reg=wreath_trace['source_to_panel'];leaf_probes=0
import numpy as np
for leaf in wreath_trace['leaves_source_pixels']:
    a,b=leaf['base_px'],leaf['tip_px'];px=(a[0]+b[0])/2;py=(a[1]+b[1])/2
    u=(px-reg['x_centre_px'])*reg['x_scale_m_per_px']
    v=float(np.interp(py,reg['source_y_px'],reg['panel_up_m']))
    # A mortar bed can cross a leaf; sample away from the bed in that case.
    if min(abs(v-(z-CENTRE_Z)) for z in COURSES)<.006:continue
    ok,q,n,index=salute[0].ray_cast(Vector((u,v,.1)),Vector((0,0,-1)))
    assert ok and q.z>.008,(leaf['group'],leaf['tip_px'],'Laurel leaf surface lost')
    leaf_probes+=1
assert leaf_probes>50
salute_gaps=0
for z in COURSES[:2]:
    v=z-CENTRE_Z
    for u in np.linspace(-.59,.59,71):
        ok,q,n,index=salute[0].ray_cast(Vector((float(u),v,.1)),Vector((0,0,-1)))
        assert not ok or q.z<.004,(z,u,'Mortar bed closed by laurel relief')
        salute_gaps+=1
plaque_spec=full_spec['dimensions']['exterior_end_plaque']
plaques=[o for o in scene.objects if 'carved panel' in o.name and o.name[:2] in ('NE','SW')]
assert len(plaques)==4,'Four exterior plaques required'
for obj in plaques:
    bounds=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    width=max(v.x for v in bounds)-min(v.x for v in bounds)
    height=max(v.z for v in bounds)-min(v.z for v in bounds)
    assert abs(width-plaque_spec['width_m'])<.002 and abs(height-plaque_spec['height_m'])<.002,obj.name
from obelisk_fixtures import validate_fixtures
obelisk_fixture_checks=validate_fixtures(scene)
from shaft_masonry import validate_shaft
shaft_masonry_checks=validate_shaft(scene)
from obelisk_surfaces import validate_assignments
obelisk_surface_checks=validate_assignments(scene)
report={
 'wwii_roundel':wwii_check,
 'glb_header_valid':True,'glb_reimport_success':True,'embedded_images':len(gltf.get('images',[])),
 'materials':len(gltf.get('materials',[])),'unique_meshes':len(meshes),'unique_mesh_triangle_count':triangles,
 'column_count':len(columns),'column_meshes':len(set(o.data.name for o in columns)),
 'exported_shaft_diameters_m':shaft_diameters,'cornice_masks_with_verified_orientation':len(lion_masks),
 'revised_capital_section_radii_m':capital_radii,'column_entablature_contacts':32,
 'colonnade_plan_and_roof_checks':colonnade_plan_checks,
 'pier_exposed_end_cap_surface_counts':pier_end_surfaces,
 'single_lamps':len(single_lamps),'clustered_lamps':len(cluster_lamps),
 'clustered_lamp_paving_contacts_checked_by_ray':len(cluster_lamps),
 'single_lamp_shared_meshes':len(set(o.data.name for o in single_lamps)),
 'clustered_lamp_shared_meshes':len(set(o.data.name for o in cluster_lamps)),
 'physical_globe_geometry_checks':globe_checks,
 'grounded_lamp_plinths':len(lamp_plinths),
 'estimated_ground_gradient_dz_dy':(levels[1]-levels[0])/20,
 'column_floor_contacts':base_contacts,
 'raised_end_frame_feet':len(end_feet),
 'obelisk_fixture_geometry_checks':obelisk_fixture_checks,
 'shaft_masonry_geometry_checks':shaft_masonry_checks,
 'obelisk_surface_assignment_checks':obelisk_surface_checks,
 'world_bounds_m':{'min':minimum,'max':maximum},'verified_inscription_lines':len(built),
 'trophy_panels_with_checked_orientation':len(panels),'traced_figure_surfaces':len(figures),
 'traced_torch_reliefs':len(torches),'shared_torch_meshes':len(set(o.data.name for o in torches)),
 'traced_wreath_trophies':len(wreaths),'shared_wreath_meshes':len(set(o.data.name for o in wreaths)),
 'traced_trophy_counts':trophy_counts,'traced_arms_with_incised_motto':len(arms),
 'motto_glyphs_checked_on_ribbon':len(arms_trace['glyphs']),
 'frieze_foliage_reliefs':len(flora['frieze-foliage']),
 'architectural_rosettes':len(flora['architectural-rosette']),
 'floral_recess_depths_verified_by_ray_m':floral_recess_depths,
 'rosette_support_offsets_verified_by_ray_m':rosette_support_offsets,
 'pedestal_joint_depths_verified_by_ray_m':joint_depths,
 'roundel_moulding_mortar_crossings_checked':border_crossings,
 'heraldry_surface_height_at_mortar_beds_m':arm_joint_heights,
 'salute_underline_geometry_checked':True,
 'window_clear_aperture_rays':window_rays,'separate_window_jamb_capitals':len(capitals),
 'window_apron_recess_depths_m':apron_depths,
 'salute_wreath_leaf_midpoints_checked':leaf_probes,'salute_wreath_mortar_samples':salute_gaps,
 'end_plaques_matching_photographic_estimate':len(plaques),
 'trophy_recess_depths_verified_by_rays_m':recess_depths,
 'file_bytes':len(data),'scope':'Structural and content validation, not a claim of survey accuracy',
 'still_requires':'Better evidence for measured dimensions, fine carving depth, screened relief-panel identities and exact site edges; see browser_survey_2026-10-21.json'
}
(ROOT/'research/validation_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('ASSET_VALIDATION_OK',json.dumps(report),flush=True)
