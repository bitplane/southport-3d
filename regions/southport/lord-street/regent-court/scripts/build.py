"""Regent Court massing study, site coordinates in metres."""
import os,sys,bpy,bmesh
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(REPO/'regions/southport/lord-street/corridor-placeholders/scripts')]
from southport3d.geometry import Mesh
from datum import grade
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'
cols={}
for n in ('tower','roof'):
 c=bpy.data.collections.new(n);s.collection.children.link(c);cols[n]=c
base=grade(494,-20)-.15
mat=bpy.data.materials.new('Neutral massing');mat.diffuse_color=(.56,.55,.51,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.56,.55,.51,1)
def box(name,center,size,part):
 m=Mesh(name);m.box((center[0],center[1],center[2]+base),size);o=m.finish([mat],cols[part]);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();uv=o.data.uv_layers.new(name='Metric')
 for p in o.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 return o
# Initial volumes only: dimensions are hypotheses pending matched comparisons.
box('Podium base',(494.4,-19.6,.12),(26,20,.24),'tower')
box('Podium first slab',(494.4,-19.6,3.35),(26,20,.35),'tower')
box('Podium top slab',(494.4,-19.6,6.35),(26,20,.30),'tower')

# Roof band frames a lower central deck; adjoining bands meet without overlap.
box('Roof band north',(494.2,-10.6,34.75),(27,2,.5),'roof')
box('Roof band south',(494.2,-28.6,34.75),(27,2,.5),'roof')
box('Roof band west',(481.7,-19.6,34.75),(2,16,.5),'roof')
box('Roof band east',(506.7,-19.6,34.75),(2,16,.5),'roof')
# Roof deck subdivides around two square roof openings visible in the 3D view.
for name,c,size in [('south',(494.2,-25.3,34.325),(23,4.6,.35)),('north',(494.2,-16.3,34.325),(23,9.4,.35)),('left',(483.35,-22,34.325),(1.3,2,.35)),('middle',(494.2,-22,34.325),(16.4,2,.35)),('right',(505.05,-22,34.325),(1.3,2,.35))]:
 box('Roof deck '+name,c,size,'roof')
box('Roof access',(489.8,-20.8,35.15),(4.0,2.4,1.3),'roof')
exec((ROOT/'scripts/facade_prototype.py').read_text())
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.5;sun.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
# Validate original object families, then join only objects with the same
# semantic prefix and material. Prove all checked triangles survive batching.
sys.path.insert(0,str(ROOT/'scripts'))
from source_checks import validate as validate_source
from batch import digest,batch
bpy.context.view_layer.update();validate_source()
source_digest,source_count=digest([o for c in cols.values() for o in c.objects if o.type=='MESH'])
for c in cols.values():batch(c)
bpy.context.view_layer.update()
export_digest,export_count=digest([o for c in cols.values() for o in c.objects if o.type=='MESH'])
assert (source_digest,source_count)==(export_digest,export_count),'Batching changed checked surfaces'
s['source_surface_digest']=source_digest;s['source_triangle_count']=source_count
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/regent-court.blend'))
