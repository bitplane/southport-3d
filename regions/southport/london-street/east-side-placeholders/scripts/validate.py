"""Check finite architecture, facade registration and clear window openings."""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/east-side-placeholders.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for part,block in zip(['william-hill','kba','myers'],D['blocks']):
    obs=list(bpy.data.collections[part].objects)
    points=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    assert min(v.x for v in points)>6.6,(part,'projects into road')
    assert min(v.y for v in points)>block['y'][0]-.2,(part,'crosses south neighbour')
    assert max(v.y for v in points)<block['y'][1]+.2,(part,'crosses north neighbour')
    assert max(v.x for v in points)<29,(part,'blocks shared lane')
    assert min(v.z for v in points)<D['ground_z']+.01,(part,'floating base')
for o in meshes:
    if o.name.startswith('Roof ') and 'flat' not in o.name and 'felt' not in o.name:
        bm=bmesh.new();bm.from_mesh(o.data)
        assert all(e.is_manifold for e in bm.edges),(o.name,'open roof shell')
        bm.free()
    if o.name.startswith('Window ') and 'rooflight' not in o.name:
        pts=[v.co for v in o.data.vertices]
        x=(min(v.x for v in pts)+max(v.x for v in pts))/2+.04
        y=(min(v.y for v in pts)+max(v.y for v in pts))/2+.12
        origin=o.matrix_world@Vector((x,y,.35))
        direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
        hit,p,n,i,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
        assert hit and target==o,(o.name,'obscured by',target.name if target else None)
report={'meshes':len(meshes),'checks':'finite UV geometry; frontage and lane bounds; closed roof skins; visible recessed window samples'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)

# The visible corner return and main side plane previously coincided, flickering
# despite valid individual meshes. Audit these exterior wall skins together.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender([o for o in meshes if o.name in ['Envelope Myers brick frontage','Envelope Myers Anchor wall']])

# Myers owns the KBA/Myers party wall; KBA owns the William Hill/KBA wall.
assert bpy.data.objects.get('Envelope KBA main side.001') is None
assert bpy.data.objects.get('Envelope William Hill front side.001') is None
for name,depth,height in [('Envelope KBA main side',7.0,5.6),('Envelope Myers north party wall',8.5,5.95)]:
 ob=bpy.data.objects[name]
 for d in [.5,depth-.5]:
  for h in [.5,height-.1]:
   for side in [-1,1]:
    hit,p,n,i=ob.ray_cast(Vector((side,h,-d)),Vector((-side,0,0)),distance=2)
    assert hit and abs(abs(p.x)-.11)<1e-5,(name,'Shared-wall coverage',d,h,side)
print('Shared party sections have one continuous owner')
