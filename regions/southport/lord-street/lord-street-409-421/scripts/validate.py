"""Scoped exterior/roof/window ownership and open-court regression."""
from pathlib import Path
import bpy,json,math,os,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from shapes import transform
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
assert n<80000,n
report={'phase':D['phase'],'triangles':n,'objects':len(obs),'scoped_coplanarity':{k:len(v)for k,v in checks.items()},'court_probes':D['courts'],'full_source_numeric_residuals':residual,'limits':'Tests grouped shell, repeated joinery and paired canopy skins. Full exported surface/trim/neighbour audit remains required; decorative buried contacts are not blanket exempt.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
