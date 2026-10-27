"""Scoped exterior/roof/window ownership and open-court regression."""
from pathlib import Path
import bpy,json,math,os,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from shapes import transform,bank_roof_height
from coplanar import check_blender,overlaps
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/building.blend'));s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];n=0
for ob in obs:
 ob.data.calc_loop_triangles();n+=len(ob.data.loop_triangles)
 for t in ob.data.loop_triangles:
  a,b,c=[ob.matrix_world@ob.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in [a,b,c]for v in p);assert (b-a).cross(c-a).length>1e-10,(ob.name,'degenerate')
checks={'shell':[o for o in obs if o.name.startswith('Shell')],'joinery':[o for o in obs if o.name.startswith('Joinery')],'canopy_skin':[o for o in obs if o.name.startswith('Canopy')and 'glass'in o.name.lower()]}
for name,oset in checks.items():
 assert oset,name;check_blender(oset)
# Full source guard supplements the semantic selections. Only the measured
# float32 shared-edge residue in sill/reveal and contiguous slate joins is allowed.
triangles=[];labels=[]
for ob in obs:
 for tri in ob.data.loop_triangles:
  triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co)for i in tri.vertices]);labels.append(ob.name)
residual=overlaps(triangles,labels)
print('FULL_SOURCE_RESIDUAL',residual)
for a,b,area in residual:
 shell_trim=(a.startswith('Shell')and b.startswith('Trim'))or(b.startswith('Shell')and a.startswith('Trim'))
 slate=a.startswith('Roof')and b.startswith('Roof')and'Grey slate'in a and'Grey slate'in b
 assert (shell_trim or slate)and area<1e-5,(a,b,area)
deps=bpy.context.evaluated_depsgraph_get()
for x,y in D['courts']:
 hit,*_=s.ray_cast(deps,Vector(transform(D,(x,y,4))),Vector((0,0,1)),distance=30);assert not hit,('obstructed court',x,y)
# Probe the open oculus, the solid wall above the oriel, pediment, return,
# both mansard slopes and the clipped glazing and stack feet independently.
def probe(name,start,end,expected,tolerance=.035):
 a,b,want=[Vector(transform(D,p))for p in (start,end,expected)];direction=(b-a).normalized()
 hit,location,normal,face,ob,matrix=s.ray_cast(deps,a,direction,distance=(b-a).length)
 assert hit,(name,'missing surface');assert abs((location-a).length-(want-a).length)<tolerance,(name,tuple(location),tuple(want),ob.name)
 return ob.name
t=D['tower'];cx=t['width']/2
probes={}
probes['wall above oriel']=probe('wall above oriel',(cx,-2,10.20),(cx,1,10.20),(cx,0,10.20))
probes['oculus glass']=probe('oculus glass',(cx+.11,-2,t['oculus_z']+.09),(cx+.11,1,t['oculus_z']+.09),(cx+.11,.205,t['oculus_z']+.09))
probes['pediment']=probe('pediment',(cx,-2,13.0),(cx,1,13.0),(cx,-t['pediment_depth'],13.0))
probes['return parapet']=probe('return parapet',(5,2,12.6),(3,2,12.6),(t['width']+t['return_thickness'],2,12.6))
probes['exposed party wedge']=probe('exposed party wedge',(-.4,.08,12.02),(.4,.08,12.02),(0,.08,12.02))
a,b=[Vector(transform(D,p))for p in [(-.4,.5,11.95),(.4,.5,11.95)]];hit,*_=s.ray_cast(deps,a,(b-a).normalized(),distance=(b-a).length);assert not hit,'bank duplicates the adjoining party wall'
probes['projecting return coping']=probe('projecting return coping',(5,2,12.86),(3,2,12.86),(t['width']+t['return_thickness']+t['return_coping_projection'],2,12.86))
z=t['top']+t['crown_rise']+.27;y=t['depth']/2
probes['crest rail']=probe('crest rail',(cx+.4,y,z),(cx-.4,y,z),(cx+.023,y,z))
for y in (.8,2.5):probes['mansard '+str(y)]=probe('mansard '+str(y),(8.2,y,20),(8.2,y,8),(8.2,y,bank_roof_height(D,y)))
y=.8;z=(bank_roof_height(D,y)+D['front_eaves']+(D['front_ridge']-D['front_eaves'])*y/D['ridge_y'])/2;w=D['front_width']
probes['end wall at pitch break']=probe('end wall at pitch break',(w+.5,y,z),(w-.5,y,z),(w,y,z))
v=D['front_rooflights'][0];x,y=v['x'],(v['y0']+v['y1'])/2
probes['rooflight glass']=probe('rooflight glass',(x,y,20),(x,y,8),(x,y,bank_roof_height(D,y)-.045))
v=D['front_roof_stacks'][0];x,y=v['x'],(v['y0']+v['y1'])/2
probes['roof stack']=probe('roof stack',(x,y,20),(x,y,8),(x,y,v['top']))
assert n<80000,n
report={'phase':D['phase'],'triangles':n,'objects':len(obs),'scoped_coplanarity':{k:len(v)for k,v in checks.items()},'court_probes':D['courts'],'tower_and_roof_probes':probes,'full_source_numeric_residuals':residual,'limits':'Tests grouped shell, repeated joinery and paired canopy skins. Full exported surface/trim/neighbour audit remains required; decorative buried contacts are not blanket exempt.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
