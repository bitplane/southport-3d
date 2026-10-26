"""Whole-architecture coplanar regression and actual exported source integrity."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/jacksons.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];count=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(v) for p in o.data.vertices for v in p.co)
 o.data.calc_loop_triangles();count+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert(b-a).cross(c-a).length>1e-10,(o.name,'degenerate')
 if o.get('closed_shell'):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),(o.name,'open roof');assert bm.calc_volume(signed=True)>0,(o.name,'inward roof');bm.free()
check_blender([o for o in obs if not o.name.startswith('Fine ')])
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':count,'checks':['all architectural meshes coplanar regression','finite nondegenerate geometry','packed textures'],'limits':['Scoped coplanar check covers all authored architecture; it does not audit neighbouring assets or depth artifacts. Roofs are single-sided skins, not closed solids.']},indent=2)+'\n')
