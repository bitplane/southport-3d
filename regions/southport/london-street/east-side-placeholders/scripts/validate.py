"""Check placeholder footprints stay separate, behind the frontage and off NatWest."""
from pathlib import Path
import json
import math
import os
import bpy

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/east-side-placeholders.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==len(D['blocks'])
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
boxes=[]
for o in meshes:
    points=[o.matrix_world@v.co for v in o.data.vertices]
    box=[(min(p[k] for p in points),max(p[k] for p in points)) for k in range(3)]
    assert box[0][0]>D['frontage_x']-1e-4,(o.name,'in front of the London Street frontage')
    assert box[2][0]<D['ground_z']<box[2][1]
    boxes.append((o.name,box))
# NatWest's corrected return ends at y=-42.66; placeholders must not intrude.
repo=Path(os.environ['SOUTHPORT_REPO_ROOT'])
natwest=json.loads((repo/'regions/southport/london-square/natwest/research/layout.json').read_text())
for name,box in boxes:
    assert box[1][1]<=natwest['rear_y']-.01,(name,'overlaps NatWest')
for i,(name,a) in enumerate(boxes):
    for other,b in boxes[i+1:]:
        overlap=[min(a[k][1],b[k][1])-max(a[k][0],b[k][0]) for k in range(2)]
        assert min(overlap)<1e-4,('Overlapping placeholders',name,other)
report={'placeholders':len(meshes),'checks':'Finite UV boxes on the shared frontage, buried bases, no mutual or NatWest overlap'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
