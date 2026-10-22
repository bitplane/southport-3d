"""Compare the delivered column/roof proportions with a conditional photo fit.

An isolated study, not a replacement for the master. Pixel observations are
recorded separately; affine ratios are not a camera-calibrated survey.
"""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/build_memorial.py'
ns={'__file__':str(source),'__name__':'vertical_proportion_study'}
baseline=ROOT/'checkpoints/exterior-0.10/scripts/build_memorial.py'
exec(compile(baseline.read_text().split('\nsite_context()\n')[0],str(baseline),'exec'),ns)
Mesh=ns['Mesh'];collection=ns['NE'];materials=ns['STONE']+[ns['STONE_DARK']]
fit=json.loads((ROOT/'research/colonnade_vertical_proportion_study.json').read_text())
candidate=fit['candidate_datums_m']


def revised_column(x):
    mesh=Mesh('Candidate Doric column with plain neck and lower annulus')
    mesh.lathe((0,0),[(.32,.365),(.34,.382),(.37,.388),(.405,.379),(.432,.349),(.47,.331)],80)
    shaft=[]
    for j in range(65):
        t=j/64
        shaft.append((.47+t*(candidate['shaft_top']-.47),.33*(1-t)+.275*t+.010*math.sin(math.pi*t)))
    mesh.lathe((0,0),shaft,160,0,20,.024)
    mesh.lathe((0,0),[(3.84,.282),(3.848,.292),(3.858,.298),(3.872,.293),(3.883,.280)],80)
    mesh.lathe((0,0),[(3.883,.280),(3.975,.280),(3.985,.285)],80)
    mesh.lathe((0,0),[(3.985,.285),(4.002,.301),(4.028,.342),(4.052,.391),(4.06,.397)],80)
    mesh.box((0,0,4.101),(.83,.83,.082))
    mesh.transform(Matrix.Diagonal((.48/.66,.48/.66,1,1)))
    ob=mesh.finish(materials,collection,.001,True)
    ob.location.x=x
    ob['status']='Candidate only; conditional 5.54 m top / 0.47 m shaft-base anchors'
    return ob


def band(name,x,z,width,depth,height,material=2):
    mesh=Mesh(name)
    mesh.box((x,0,z),(width,depth,height),material)
    return mesh.finish(materials,collection,.003)


for x in (-2.10-.35,-2.10+.35):
    ns['column']('Checkpoint 0.10 column',x,0,collection)
for x in (2.10-.35,2.10+.35):
    revised_column(x)
for x,name in [(-2.10,'Checkpoint 0.10'),(2.10,'Photographic candidate')]:
    band(name+' base',x,.22,3.1,1.4,.20)
    if x<0:
        layers=[(4.36,2.72,.64,.12,2),(4.47,2.80,.70,.10,2),
                (4.55,2.87,.78,.065,1),(4.605,2.86,.74,.045,2),
                (4.815,2.86,.80,.39,2),(5.045,2.92,.78,.07,1),
                (5.115,3.06,.87,.07,6),(5.18,3.10,.90,.065,6),
                ((5.215+5.54)/2,2.90,.78,5.54-5.215,2)]
    else:
        layers=[(4.175,2.72,.64,.10,2),(4.29,2.80,.70,.13,2),
                (4.37,2.87,.78,.06,1),(4.405,2.86,.74,.03,2),
                (4.66,2.86,.80,.48,2),(4.94,2.92,.78,.08,1),
                (5.015,3.06,.87,.07,6),(5.09,3.10,.90,.08,6),
                ((5.13+5.54)/2,2.90,.78,5.54-5.13,2)]
    for i,(z,w,d,h,mat) in enumerate(layers):
        band(name+' band '+str(i),x,z,w,d,h,mat)
    ns['text_object'](name,name,(x,-.55,5.82),(0,-1,0),.20,3.50,ns['FONT'],ns['BLACK_IRON'],collection=collection)

ns['setup_render']()
scene=bpy.context.scene;scene.cycles.samples=48
sun=bpy.data.objects['Soft afternoon sun']
sun.rotation_euler=Vector((.55,.65,-.52)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=2.8;sun.data.angle=.09
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
for name,position,target,scale,size in [
    ('whole',(0,-14,3.0),(0,0,3.0),8.2,(1800,1400)),
    ('capitals',(0,-14,4.05),(0,0,4.05),7.8,(2000,700))]:
    scene.camera=ns['camera']('Vertical proportion '+name,position,target,scale)
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(ROOT/f'renders/studies/vertical-proportions-{name}-0.11.png')
    bpy.ops.render.render(write_still=True)
    print('VERTICAL_STUDY_RENDERED',name,flush=True)
dest=ROOT/'models/studies';dest.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(dest/'colonnade-vertical-candidate.blend'))
print('VERTICAL_STUDY_COMPLETE',flush=True)
