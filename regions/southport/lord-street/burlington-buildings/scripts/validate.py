"""Scoped shell, window joinery and canopy-skin regressions plus clear courts."""
from pathlib import Path
import bpy,json,math,os,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from shapes import transform
from coplanar import check_blender,overlaps
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/burlington-buildings.blend'));s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];triangles=0
for o in obs:
 assert o.data.uv_layers or o.name.startswith(('Fine Burlington','Shop lettering')),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for v in o.data.vertices:assert all(math.isfinite(n) for n in v.co)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate triangle')
selections={'structural_shell':[o for o in obs if o.name.startswith('Shell')],'roof_slopes':[o for o in obs if o.name.startswith(('Roof continuous','Roof works','Roof middle','Roof cafe'))],'all_repeated_window_joinery':[o for o in obs if o.name.startswith('Joinery')],'canopy_top_and_underside':[o for o in obs if o.name.startswith('Canopy glass')]}
selections['window_prototypes_and_shell_interfaces']=[o for o in obs if o.name=='Shell front main' or o.name.startswith(('Joinery','Door return','Trim south ','Trim middle first','Trim middle second','Trim name first','Trim name second','Trim cafe first','Trim cafe second','Trim upper head','Trim moulded head'))]
for name,selected in selections.items():
 assert selected,name
 if name!='window_prototypes_and_shell_interfaces':check_blender(selected)
 else:
  ts=[];ls=[]
  for ob in selected:
   ob.data.calc_loop_triangles()
   for tri in ob.data.loop_triangles:
    ts.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in tri.vertices]);ls.append(ob.name)
  residual=overlaps(ts,ls)
  # Independently triangulated float32 sill/reveal shared edges have <0.00001m²
  # projection residue. Only these exact interface classes may use this bound.
  for a,b,area in residual:
   names={a,b};trim=next((v for v in names if v.startswith('Trim ')), '')
   assert 'Shell front main' in names and trim.endswith((' sill',' lintel')) and area<1e-5,(a,b,area)

# Every open upper courtyard stays open. Low additions remain separate footprints.
deps=bpy.context.evaluated_depsgraph_get()
for x,y in [(10,18),(16.5,18),(16.5,25),(10,26)]:
 hit,*_=s.ray_cast(deps,Vector(transform(D,(x,y,.5))),Vector((0,0,1)),distance=30)
 assert not hit,('filled court',x,y)
assert triangles<150000,triangles
report={'phase':D['phase'],'triangles':triangles,'objects':len(obs),'coplanar_selections':{k:len(v) for k,v in selections.items()},'clear_court_probes':4,'coverage_limit':'Selections test shell, all repeated window joinery, roof valley ownership and canopy skins; all exported surfaces and neighbour seams receive a separate publication audit, not a blanket overlap-free claim.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
