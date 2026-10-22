from pathlib import Path
import bpy,json,math
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];layout=json.loads((ROOT/'research/layout.json').read_text())
assert len([o for o in meshes if o.name.startswith('Furniture ') and ' extension ' not in o.name])==len(layout['furniture'])
assert len([o for o in meshes if o.name.startswith('Chain ')])==2
assert all(math.isfinite(v) for o in meshes for p in o.data.vertices for v in p.co)
assert all(o.data.polygons for o in meshes)
assert all(o.data.uv_layers for o in meshes if o.name.startswith(('Surface ','Pattern ')))
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
(ROOT/'research/validation.json').write_text(json.dumps({'mesh_objects':len(meshes),'furniture_placements':len(layout['furniture']),'checks':'finite geometry, complete placement count, packed maps, ground UVs'},indent=2))
print('Public realm geometry validated')
# Validate the shared generator levers independently of published instance totals.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.street import furniture
for kind in {f['kind'] for f in layout['furniture']}:
 counts=[]
 for level in ['detail','walk','district']:
  m=furniture(kind,level);counts.append(sum(len(f)-2 for f in m.faces))
  assert all(math.isfinite(c) for v in m.vertices for c in v)
 assert counts[0]>counts[1]>counts[2],(kind,counts)
print('Furniture generator reductions validated')

# Every base is on its assigned pavement, including the narrowing island ends.
for f in layout['furniture']:
 x,y=f['xy']
 if f['part']=='island-furniture':
  radius=layout['island']['width']/2;cap=max(0,abs(y)-(layout['island']['length']/2-radius))
  assert x*x+cap*cap<radius*radius,(f,'off island')
 else:
  poly=layout['courts']['ne' if f['part']=='ne-furniture' else 'sw'];crosses=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):crosses.append((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))
  assert min(crosses)>=-1e-5 or max(crosses)<=1e-5,(f,'off forecourt')
  if f['kind']=='bollard':assert not (abs(x)<14 and 11<y<13),'Bollard obstructs crossing'
print('Furniture pavement containment and crossing clearance validated')

# Extension coverage, open seams, and bounded longitudinal grade.
sys.path.insert(0,str(ROOT/'scripts'))
from extensions import PARTS
assert all(bpy.data.collections.get(n) and len(bpy.data.collections[n].objects) for n in PARTS)
from southport3d.landscape import tree
counts=[sum(len(f)-2 for f in tree(level).faces) for level in ['detail','walk','district']]
assert counts[0]>counts[1]>counts[2],counts
assert len([o for o in meshes if o.name.startswith('Tree ')])==sum(len(v) for v in json.loads((ROOT/'research/streets.json').read_text())['trees'].values())
for name in ['london-1-ground','london-2-ground','london-3-ground']:
 vertices=[v.co.z for o in bpy.data.collections[name].objects for v in o.data.vertices]
 assert max(vertices)-min(vertices)<.3,(name,'Unbounded grade or furniture in ground')
print('Extended areas, tree LODs and bounded road grades validated')

# The photographed garden row extends, rather than duplicates, the core row.
front=json.loads((ROOT/'research/streets.json').read_text())['sw_frontage_2024']
posts=[o for o in meshes if o.name.startswith('Furniture bollard ')]
positions=[tuple(round(c,3) for c in o.location[:2]) for o in posts]
assert len(set(positions))==len(positions),'Duplicated bollard placements'
for x in front['garden_bollards_x']:
 assert (x,front['garden_bollards_y']) in positions
 assert x>-66,'Post blocks SW garden service-road opening'
for x in front['shop_bollards_x']:
 assert (x,front['shop_bollards_y']) in positions
 assert -23.6<front['shop_bollards_y']< -21.1,'Post off frontage footway'
assert len([o for o in meshes if o.name.startswith('Garden globe lamp')])==2
from garden_front import globe_lamp,balustrade
for factory in [globe_lamp,balustrade]:
 counts=[sum(len(f)-2 for f in factory(level).faces) for level in ['detail','walk','district']]
 assert counts[0]>counts[1]>counts[2],(factory.__name__,counts)
print('Photographed garden furniture placement and LOD reductions validated')
