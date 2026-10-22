"""Apply the builder's paving support correction to the already baked scene.

One-off migration for checkpoint 0.5; normal rebuilds include it directly.
Must run after any renderer has finished saving the master scene.
"""
from pathlib import Path
import sys,json,bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from geometry import Mesh
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
name='Continuous paving beneath clustered lamps — provisional'
assert bpy.data.objects.get(name) is None,'Correction already applied'
m=Mesh(name)
for sx in (-1,1):
    for sy in (-1,1):m.box((sx*18,sy*9,-.04),(1.1,1.1,.06))
m.finish([bpy.data.materials['Grey granite paving']],bpy.data.collections['00 Site registration and approximate paving'])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
report_path=ROOT/'research/build_report.json'
report=json.loads(report_path.read_text());report['objects']+=1;report['mesh_vertices']+=len(m.vertices)
report['post_build_correction']='Four continuous paving supports; identical geometry is included by build_memorial.py'
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('CLUSTER_PAVEMENT_CONTACTS_CORRECTED',flush=True)
