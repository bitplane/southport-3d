"""Assemble complete streaming parts from explicit per-feature policies."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from southport3d.lod import sha256
from blender_lod import evaluated_copy, reduce, bake, sample_error, triangles, validate_materials, select


def export(path,objects):
    select(*objects)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
                             export_apply=True,export_tangents=True,export_cameras=False,
                             export_lights=False,export_extras=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--asset',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);asset_dir=Path(args.asset);dest=Path(args.output);dest.mkdir(exist_ok=True,parents=True)
    spec=json.loads((asset_dir/'publication.json').read_text());rules=[(r,re.compile(r['match'])) for r in spec['rules']]
    report={'source_sha256':sha256(args.source),'coverage':{},'prototypes':[],'files':[]}
    for level in ('detail','walk','district'):
        bpy.ops.wm.open_mainfile(filepath=args.source)
        memberships={}
        for part in spec['parts']:
            for obj in bpy.data.collections[part['collection']].all_objects:
                if obj.type=='MESH' and len(obj.data.polygons):
                    if obj in memberships:raise ValueError('Mesh appears in multiple parts: '+obj.name)
                    memberships[obj]=part['id']
        excluded={o for c in spec.get('excluded_collections',[]) for o in bpy.data.collections[c['name']].all_objects}
        for obj in bpy.context.scene.objects:
            if obj.type=='MESH' and len(obj.data.polygons) and obj not in memberships and obj not in excluded:
                raise ValueError('Mesh outside declared publication parts: '+obj.name)
        if set(memberships)&excluded:raise ValueError('Published and excluded collections overlap')
        by_part={p['id']:[o for o in bpy.data.collections[p['collection']].all_objects if o.type=='MESH' and len(o.data.polygons)] for p in spec['parts'] if not p.get('fixed_level') or p['fixed_level']==level}
        included={o for objects in by_part.values() for o in objects}
        # Every exportable mesh needs exactly one deliberate classification.
        classes={}
        for obj in included:
            matches=[r for r,pattern in rules if pattern.search(obj.name)]
            if len(matches)!=1:raise ValueError(f'{obj.name}: expected one publication rule, found {len(matches)}')
            classes[obj]=matches[0]
        report['coverage'][level]={'objects':len(included),'classified':len(classes)}
        omitted=set()
        if level!='detail':
            groups={}
            for obj in included:
                rule=classes[obj];action=rule[level]
                if action['strategy']=='omit':omitted.add(obj);continue
                if action['strategy']=='keep':continue
                scale=tuple(round(obj.matrix_world.to_3x3().col[i].length,6) for i in range(3))
                key=(obj.data.name,rule['id'],scale,tuple(s.material.name if s.material else '' for s in obj.material_slots))
                groups.setdefault(key,[]).append(obj)
            for key,instances in sorted(groups.items(),key=lambda item:item[0]):
                source=instances[0];rule=classes[source];action=rule[level]
                token=hashlib.sha256(repr(key).encode()).hexdigest()[:10];out=dest/'maps'/level/(rule['id']+'-'+token);out.mkdir(parents=True)
                high=evaluated_copy(source,'HIGH '+rule['id']);high.hide_render=False
                low=reduce(high,rule['id']+'-'+level,action,{'id':level,'texture_size':spec['levels'][level]['texture_size']},asset_dir)
                row={'rule':rule['id'],'level':level,'instances':len(instances),'source_object':source.name,'source_triangles':triangles(high),'triangles':triangles(low),'reason':action['reason']}
                if action['bake']:
                    validate_materials(high)
                    error=sample_error(high,low);row['sampled_error']=error
                    if error['max_m']>action['max_sampled_error_m']:raise ValueError(f"{rule['id']} {level}: error {error['max_m']} exceeds {action['max_sampled_error_m']}")
                    _,stats=bake(high,low,action,{'texture_size':spec['levels'][level]['texture_size']},out);row['bake_checks']=stats
                else:
                    for mat in high.data.materials:low.data.materials.append(mat)
                if triangles(low)>=triangles(high):raise ValueError('Generator failed to reduce '+source.name)
                for obj in instances:
                    obj.data=low.data;obj.modifiers.clear()
                bpy.data.objects.remove(high,do_unlink=True);bpy.data.objects.remove(low,do_unlink=True)
                report['prototypes'].append(row);print('PROTOTYPE',rule['id'],level,row['triangles'],'instances',len(instances),flush=True)
        for part,objects in by_part.items():
            objects=[o for o in objects if o not in omitted]
            if not objects:raise ValueError('Cannot publish an empty part: '+part)
            path=dest/(part+'-'+level+'.glb');export(path,objects)
            report['files'].append({'part':part,'level':level,'path':path.name})
        print('LEVEL_COMPLETE',level,flush=True)
    if sha256(args.source)!=report['source_sha256']:raise ValueError('Master changed during packaging')
    (dest/'assembly.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
