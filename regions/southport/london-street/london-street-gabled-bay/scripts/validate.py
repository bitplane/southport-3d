"""Check roof partition, facade apertures, registration and closed roof shell."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from corner_plan import roof_faces,signed_area,frame,world
from coplanar import check_blender
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-gabled-bay.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in obs)
assert all(math.isfinite(c) for o in obs for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
area=sum(abs(signed_area([(x,y) for x,y,z in vs])) for _,vs in roof_faces(D));assert abs(area-abs(signed_area(D['corner_footprint'])))<1e-5
roof=bpy.data.objects['Shell roof'];bm=bmesh.new();bm.from_mesh(roof.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00015)
assert all(e.is_manifold for e in bm.edges),'Open roof shell'
assert all(e.is_contiguous for e in bm.edges),'Roof winding mismatch'
assert bm.calc_volume(signed=True)>0,'Inward roof';bm.free()
# Upper apertures must show joinery, not an overlapping placeholder/wall skin.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for f in D['facades']:
 a,u,n,w=frame(D['corner_footprint'],f['edge'])
 for t in f['windows']:
  q=(a[0]+u[0]*(t+.15)+n[0],a[1]+u[1]*(t+.15)+n[1],5.65)
  origin=Vector(world(D,q));end=Vector(world(D,(q[0]-n[0],q[1]-n[1],q[2])));direction=(end-origin).normalized()
  hit,at,normal,idx,found,M=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
  assert hit and found.name.startswith('Architecture'),(f['name'],t,found.name if found else None)
check_blender([o for o in obs if o.name.startswith('Shell')])
report={'objects':len(obs),'roof_plan_area_m2':area,'checks':'Finite packed UV meshes, complete nonoverlapping roof plan, closed outward roof slab, 15 unobscured upper openings, coplanar shell audit.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Mixed-level regression: the lower plain corner must stay owned by architecture
# when its shopfront is Detail and the rest of the building is District.
from district import surfaces
from mathutils.bvhtree import BVHTree
receivers=surfaces(ROOT);verts=[];polys=[]
for face in receivers['architecture']:
 start=len(verts);verts.extend(face['vertices']);polys.append(tuple(range(start,start+4)))
bvh=BVHTree.FromPolygons(verts,polys)
a,u,n,w=frame(D['corner_footprint'],2);q=(a[0]+u[0]*w/2+n[0],a[1]+u[1]*w/2+n[1],1.4)
origin=Vector(world(D,q));end=Vector(world(D,(q[0]-n[0],q[1]-n[1],q[2])));direction=(end-origin).normalized()
assert bvh.ray_cast(origin,direction,1.2)[0] is not None,'District loses lower corner wall'
placeholders=Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/station-quarter/frontage-placeholders'
plan=json.loads((placeholders/'research/layout.json').read_text())
assert next(b for b in plan['blocks'] if b['id']=='chapel-london-corner')['replace_with']=='southport.london-street.london-street-gabled-bay'
assert not any(p['id']=='chapel-london-corner' for p in json.loads((placeholders/'publication.json').read_text())['parts']),'Overlapping placeholder still published'
print('Mixed-level corner ownership and placeholder retirement verified')
