"""Finite geometry, aperture visibility, reserved passage, and surface ownership."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lakeland-leather.blend'));bpy.context.view_layer.update()
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')];from ground_contact import post_base
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];deps=bpy.context.evaluated_depsgraph_get();triangles=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate export')
frame=Matrix(bpy.data.objects['Glazing great']['face_frame']);direction=(frame.to_3x3()@Vector((0,0,-1))).normalized()
probes=[(3.63,9.1),(2.1,8.8),(4.8,8.8),(1.67,12.5),(5.37,12.5),(3.63,5.5),(2.07,5.5)]
for x,z in probes:
 hit,p,n,index,target,m=bpy.context.scene.ray_cast(deps,frame@Vector((x,z,3)),direction,distance=4)
 assert hit and target.name.startswith(('Glazing','Frames','Fine oriel')),(x,z,target.name if target else None)
# No building point may intrude into the reserved passage east of x=7.
inv=frame.inverted()
for o in obs:
 for v in o.data.vertices:
  p=inv@(o.matrix_world@v.co)
  assert p.x<7.25,(o.name,'passage intrusion',tuple(p))
# Top/bottom bay slabs must face outward; signed normal bakes preserve that.
for name,sign in [('Oriel horizontal balcony floor',1),('Oriel horizontal base',-1)]:
 assert all(p.normal.z*sign>.99 for p in bpy.data.objects[name].data.polygons),(name,'inward normal')
for k,x in enumerate((.12,1.9,5.1,6.88)):
 o=bpy.data.objects['Verandah column '+str(k)]
 assert abs(min(v.co.z for v in o.data.vertices)-(D['base_z']+post_base(D,x)))<1e-5,(o.name,'ground contact')
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'));from coplanar import check_blender
check_blender(obs)
report={'triangles':triangles,'glazing_probes':len(probes),'post_ground_probes':4,'bay_normal_checks':2,'phase':D['phase'],'scope':'All master mesh families: wall/roof skins, curved oriel, arch surrounds, joinery, relief and verandah. Same-facing coplanarity only; no claim to detect all depth-buffer artefacts.','limitations':'Rear roof dimensions estimated; court and concealed openings deferred.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
