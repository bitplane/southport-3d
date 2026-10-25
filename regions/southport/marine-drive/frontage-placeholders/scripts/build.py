"""Neutral block-plan volumes. Flat tops are bounds, not reconstructed roofs."""
import json, math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.9
 return m
mats=[material('Provisional warm grey massing',(.38,.36,.32)),material('Provisional roof height bound',(.23,.25,.26))]
sys.path.insert(0,str(ROOT/'scripts'))
from datum import grade,PAVEMENT
for block in D['blocks']:
 if block['replace_with']:continue
 c=bpy.data.collections.new(block['id']);s.collection.children.link(c)
 p=block['footprint']
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))<0:p=list(reversed(p))
 footing=min(point[2]for a,b in zip(p,p[1:]+p[:1])for point in PAVEMENT.edge_points(a,b))-.05
 n=len(p);base=[(x,y,footing)for x,y in p];z=grade(sum(x for x,y in p)/n,sum(y for x,y in p)/n)+block['height_m']
 top=[(x,y,z) for x,y in p];m=Mesh('Massing '+block['id'])
 m.add(base+top,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
 vectors=[Vector((x,y,0)) for x,y in p]
 for tri in tessellate_polygon([vectors]):
  ids=[k if isinstance(k,int) else vectors.index(k) for k in tri]
  m.add([top[k] for k in ids],[(0,1,2)],1)
  m.add([base[k] for k in ids],[(2,1,0)],0)
 ob=m.finish(mats,c)
 # Merge cap-edge vertices so the closed-volume checks inspect true topology.
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric placeholder UV')
 for poly in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(poly.normal[i]))[:2])
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 ob['footprint_id']=block['id'];ob['status']='placeholder, not finished architecture'
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
light=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));light.data.energy=2.5;light.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(light)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/frontage-placeholders.blend'))
