"""Build and inspect a separate complete colonnade plan/roof candidate.

Does not overwrite the delivered master, GLBs or numbered inspection images.
The proposed bay pitch is conditional on chamber dimensions, not a survey.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import bpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/build_memorial.py'
ns={'__file__':str(source),'__name__':'colonnade_plan_study'}
exec(compile(source.read_text().split('\nsite_context()\n')[0],str(source),'exec'),ns)
import colonnade_envelope as envelope

plan=json.loads((ROOT/'research/colonnade_plan_projection_study.json').read_text())['selected_candidate_m']
Mesh=ns['Mesh']; c=ns['NE']; code='NE'; spec=ns['SPEC']
finish=ns['finish'];block=ns['block'];masonry=ns['masonry'];engrave=ns['engrave']
wall_top=ns['COL']['abacus_top']
tw,th,tz=(ns['TROPHY'][k] for k in ('width_m','height_m','centre_z_m'))
b=plan['central_roof_break_x'];setback=plan['central_to_chamber_setback']
structural=[]


def build_candidate():
    import colonnade_assembly
    structural.extend(colonnade_assembly.build(ns,code,c,plan))


def inspect_geometry():
    bpy.context.view_layer.update()
    report={'candidate_only':True,'columns':0,'column_contacts':0,'clear_window_rays':0,
            'roof_mesh_topology':{},'published_max_roof_envelope_m':[24.6,4.9,5.54]}
    depsgraph=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
    report['pier_end_surfaces']=[]
    for wall in (o for o in c.objects if 'window_chamber_centre_x' in o):
        sign=1 if wall['window_chamber_centre_x']>0 else -1
        evaluated=wall.evaluated_get(depsgraph);mesh=evaluated.to_mesh()
        for sy in (-1,1):
            count=envelope.pier_end_surface_count(mesh,sign,sy)
            assert count==1,(wall.name,sy,'Coincident pier end caps',count)
            report['pier_end_surfaces'].append({'wall':wall.name,'side':sy,'surfaces':count})
        evaluated.to_mesh_clear()
    for ob in c.objects:
        if 'fluted Doric column' not in ob.name:continue
        report['columns']+=1
        origin=ob.location+Vector((0,0,4.13))
        arch=next(o for o in structural if 'architrave' in o.name)
        ok,hit,normal,face=arch.evaluated_get(depsgraph).ray_cast(origin,Vector((0,0,1)),distance=.15)
        assert ok and abs(hit.z-4.142)<.0002,(ob.name,'missing underside contact')
        report['column_contacts']+=1
    for x in plan['window_centres']:
        for sy in (-1,1):
            for dx in (-.35,0,.35):
                for z in (1.32,1.9,2.7,3.06):
                    origin=Vector((x+dx,sy*2.65,z))
                    ok,*_=scene.ray_cast(depsgraph,origin,Vector((0,-sy,0)),distance=1.0)
                    assert not ok,('window obstructed',tuple(origin))
                    report['clear_window_rays']+=1
    for ob in structural:
        counts=Counter(tuple(sorted((a,b))) for p in ob.data.polygons
                       for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]]))
        boundary=sum(v==1 for v in counts.values());nonmanifold=sum(v!=2 for v in counts.values())
        assert not nonmanifold,(ob.name,'nonmanifold edges',nonmanifold)
        report['roof_mesh_topology'][ob.name]={'faces':len(ob.data.polygons),
                                              'boundary_edges':boundary,'nonmanifold_edges':nonmanifold}
    assert report['columns']==16 and report['column_contacts']==16 and report['clear_window_rays']==48
    report['structural_square_chamber_external_size_m']=[4.40,4.40]
    return report


build_candidate()
report=inspect_geometry()
ns['setup_render']();scene=bpy.context.scene;scene.cycles.samples=48
block('Study ground',(0,0,-.053),(2000,2000,.1),ns['CONTEXT'],ns['PAVER'],0)
sun=bpy.data.objects['Soft afternoon sun']
sun.rotation_euler=Vector((-.55,-.65,-.75)).to_track_quat('-Z','Y').to_euler()
sun.data.angle=.12;sun.data.energy=2.8
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.48

# Import a preserved baseline for a camera-identical elevation comparison.
baseline_path=ROOT/'checkpoints/exterior-0.11/models/london-square-exterior.blend'
with bpy.data.libraries.load(str(baseline_path),link=False) as (src,dst):
    dst.collections=['02 North-east colonnade exterior']
baseline=dst.collections[0];scene.collection.children.link(baseline)
bpy.context.view_layer.update()  # Appended matrix_world values are initially identity.
centre=ns['SITE']['colonnades']['NE']['centre_site_xy_m']
undo=(Matrix.Translation(Vector((*centre,0))) @ Matrix.Rotation(math.pi/2,4,'Z')).inverted()
for ob in baseline.objects:ob.matrix_world=undo @ ob.matrix_world
bpy.context.view_layer.update()
base_platform=next(o for o in baseline.objects if 'continuous stepped platform' in o.name)
points=[base_platform.matrix_world@Vector(v) for v in base_platform.bound_box]
assert abs(max(p.x for p in points)-min(p.x for p in points)-24.9)<.02
assert abs(max(p.y for p in points)-min(p.y for p in points)-5.7)<.02
baseline.hide_render=True
views=[
    ('front',(0,80,5.7),(0,0,2.7),27.4,(2400,800)),
    ('corner',(26,30,13),(2,0,2.8),28,(2000,1100)),
    ('roof-step',(11,10,7.6),(8.1,1.9,4.9),5.5,(1500,1100)),
    ('plan',(0,0,36),(0,0,0),27.4,(2400,900)),
]
renders=[]
for name,position,target,scale,size in views:
    scene.camera=ns['camera']('Plan study '+name,position,target,scale)
    scene.render.resolution_x,scene.render.resolution_y=size
    for version in (['baseline','candidate'] if name=='front' else ['candidate']):
        baseline.hide_render=version!='baseline';c.hide_render=version!='candidate'
        path=ROOT/f'renders/studies/plan-{name}-{version}-0.12.png'
        scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        renders.append(str(path.relative_to(ROOT)))
        print('PLAN_STUDY_RENDERED',path.name,flush=True)
baseline.hide_render=True;baseline.hide_viewport=True;c.hide_render=False
scene.camera=bpy.data.objects['Plan study corner']
dest=ROOT/'models/studies/colonnade-plan-candidate.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report['candidate_blend']=str(dest.relative_to(ROOT));report['renders']=renders
report['artifacts']=[{'path':p,'bytes':(ROOT/p).stat().st_size,
                      'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
                     for p in [str(dest.relative_to(ROOT))]+renders]
report['limits']='Plan and roof details are photographic estimates. This isolated scene compares against checkpoint 0.11; adoption is recorded in the progress checkpoint. No interiors added.'
(ROOT/'research/colonnade_plan_candidate_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PLAN_STUDY_COMPLETE',json.dumps(report),flush=True)
