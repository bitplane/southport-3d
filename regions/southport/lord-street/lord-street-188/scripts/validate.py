"""Recheck the exported master against the pre-batching authoring digest."""
from pathlib import Path
import bpy,os,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from source_checks import validate
from batch import digest
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/building.blend'));s=bpy.context.scene
validate();actual=digest([o for o in s.objects if o.type=='MESH'])
assert actual==(s['source_surface_digest'],s['source_triangle_count']),('surface digest changed',actual)
print('BATCHED_MASTER',len([o for o in s.objects if o.type=='MESH']),actual,flush=True)
