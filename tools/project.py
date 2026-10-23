#!/usr/bin/env python3
"""Source checks and isolated, sequential Blender builds."""
from build_lock import asset_lock

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from southport3d.lod import load_recipe

ROOT = Path(__file__).resolve().parents[1]


def assets():
    found = {}
    for path in sorted((ROOT / 'regions').rglob('asset.json')):
        spec = json.loads(path.read_text())
        key = spec['id']
        if not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', key) or key in found:
            raise ValueError(f'Invalid or duplicate asset ID: {key}')
        if spec['units'] != 'metres':
            raise ValueError(f'Expected metric asset: {key}')
        for script in [*spec['build'].values(), *spec.get('validation_checks', [])]:
            if Path(script).name != script or not (path.parent / 'scripts' / script).is_file():
                raise ValueError(f'Invalid build script: {script}')
        found[key] = (path.parent, spec)
    return found


def check():
    import numpy as np
    entries = assets()
    if not entries:
        raise ValueError('No assets found')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    forbidden = {'references', 'models', 'renders', 'textures', 'profile', 'node_modules', 'checkpoints', 'build', 'dist'}
    for name in filter(None, tracked):
        path = ROOT / name
        if forbidden.intersection(Path(name).parts) or path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.blend', '.glb', '.gltf', '.gif'}:
            raise ValueError(f'Private reference or build output tracked: {name}')
        if path.stat().st_size > 10_000_000:
            raise ValueError(f'Oversized source: {name}')
        if path.suffix == '.py':
            ast.parse(path.read_text(), filename=name)
        if path.suffix == '.json':
            json.loads(path.read_text())
        if path.suffix == '.npz':
            with np.load(path, allow_pickle=False) as data:
                if not {'z', 'width', 'height'} <= set(data.files) <= {'z', 'width', 'height', 'origin_y'}:
                    raise ValueError(f'Unexpected relief payload: {name}')
                if data['z'].ndim != 2 or any(not np.isfinite(data[k]).all() for k in data.files):
                    raise ValueError(f'Invalid relief data: {name}')
                if float(data['width']) <= 0 or float(data['height']) <= 0:
                    raise ValueError(f'Invalid relief dimensions: {name}')
    for source, spec in entries.values():
        recipe_path = source / 'lod.json'
        if recipe_path.exists():
            load_recipe(recipe_path)
        if (source / 'publication.json').exists():
            from publication import load_publication
            load_publication(source / 'publication.json')
    print(f'Checked {len(entries)} asset(s) and {len(list(filter(None, tracked)))} tracked files.')


def fingerprint(source):
    """Expected master input key; output hashes are integrity checks, not keys."""
    from build_state import Stages
    spec = json.loads((source / 'asset.json').read_text())
    stages = Stages(ROOT, source, spec, ROOT / 'build' / spec['id'])
    return hashlib.sha256(json.dumps(stages.inputs('master'), sort_keys=True).encode()).hexdigest()


def build(args):
    with asset_lock(ROOT, args.asset):
        return _build(args)


def _build(args):
    from build_state import Stages
    source, spec = assets()[args.asset]
    runtime = ROOT / 'build' / args.asset
    stages = Stages(ROOT, source, spec, runtime, args.blender, args.threads)
    force = getattr(args, 'force', False)
    if args.stage in ('build', 'all'):
        stages.execute('master', force)
    elif stages.reason('master'):
        raise ValueError('Build missing or source changed: run --stage all first')
    try:
        if args.stage in ('all', 'export'):
            stages.execute('export', force)
        if args.stage in ('all', 'validate'):
            stages.execute('validate', force)
        if args.stage == 'render':
            stages.execute('render', force or bool(args.views), args.views)
    except Exception:
        (runtime / 'source.sha256').unlink(missing_ok=True)
        raise
    if not stages.reason('validate'):
        (runtime / 'source.sha256').write_text(stages.state['nodes']['master']['key'] + '\n')
    print(f'Finished: {runtime}')


def explain(args):
    from build_state import Stages
    source, spec = assets()[args.asset]
    stages = Stages(ROOT, source, spec, ROOT / 'build' / args.asset, args.blender)
    for stage in ('master', 'export', 'validate', 'render'):
        reason = stages.reason(stage)
        if stage != 'master' and stages.reason('master'):
            reason = 'upstream master needs rebuilding'
        print(f'{stage}: {reason or "up to date"}')
    print('package: '+stages.package_reason())


def lod(args):
    with asset_lock(ROOT, args.asset):
        return _lod(args)


def _lod(args):
    from build_state import Stages, record
    source, spec = assets()[args.asset]
    runtime = ROOT / 'build' / args.asset
    stages = Stages(ROOT, source, spec, runtime, args.blender, args.threads)
    if stages.reason('master'):
        raise ValueError('Master missing or source changed: run build first')
    stages.snapshot_inputs();stages.deps=set()
    recipe_path = stages.snapshot / 'asset/lod.json'
    recipe = load_recipe(recipe_path)
    blend = (runtime / recipe['source_blend']).resolve()
    if not blend.is_relative_to(runtime.resolve()) or not blend.is_file():
        raise ValueError('LOD source must be an existing blend inside the asset runtime')
    master_hash = record([blend])
    work = runtime / 'lod-work'
    if work.exists():shutil.rmtree(work)
    work.mkdir()
    stages.run_script(stages.snapshot/'tools/blender_lod.py', True,
        ('--source',str(blend),'--recipe',str(recipe_path),'--output',str(work),
         '--source-fingerprint',stages.state['nodes']['master']['key']))
    for script, extra in [('check_lods.py',()),('lod_contact_sheet.py',()),('lod_contact_sheet.py',('--oblique',))]:
        stages.run_script(stages.snapshot/'tools'/script, False, (str(work),*extra))
    if record([blend])!=master_hash:raise ValueError('LOD pilot mutated master')
    for path in stages.deps:
        if not path.is_file() or stages.snapshot_digest(path)!=sha_file(path):
            raise ValueError('LOD dependency changed during run: '+str(path))
    dest = runtime / 'lods'
    if dest.exists():shutil.rmtree(dest)
    work.rename(dest)
    print(f'Finished: {dest}')


def sha_file(path):
    from build_state import sha
    return sha(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    sub.add_parser('check')
    indexer=sub.add_parser('index', help='Index the last-good published catalog without building assets')
    indexer.add_argument('--viewer', action='store_true', help='Also publish current viewer code without rebuilding assets')
    builder = sub.add_parser('build')
    builder.add_argument('asset')
    builder.add_argument('--stage', choices=['all', 'build', 'export', 'validate', 'render'], default='all')
    builder.add_argument('--threads', type=int, default=12)
    builder.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    builder.add_argument('--views', nargs='*', default=[])
    builder.add_argument('--force', action='store_true')
    planner = sub.add_parser('explain', aliases=['plan'], help='Explain stale incremental stages')
    planner.add_argument('asset')
    planner.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    lodder = sub.add_parser('lod', help='Bake and validate levels from the asset lod.json')
    lodder.add_argument('asset')
    lodder.add_argument('--threads', type=int, default=12)
    lodder.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    publisher = sub.add_parser('publish', help='Build all publication recipes and prepare the local viewer')
    publisher.add_argument('--rebuild', action='store_true')
    publisher.add_argument('--asset', action='append', default=[], help='Publish only this asset (repeatable), retaining other assets at their last published versions')
    publisher.add_argument('--threads', type=int, default=12)
    publisher.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    args = parser.parse_args()
    if args.command == 'list':
        for key in assets():
            print(key)
    elif args.command == 'check':
        check()
    elif args.command == 'index':
        from spatial_index import index_catalog
        with asset_lock(ROOT, 'catalog'):
            if args.viewer:
                from publish_viewer import install_viewer
                path=ROOT/'dist/catalog.json'
                catalog=json.loads(path.read_text())
                catalog['viewerVersion']=install_viewer(ROOT/'dist')
                catalog.pop('revision',None)
                catalog['revision']=hashlib.sha256(json.dumps(catalog,sort_keys=True).encode()).hexdigest()
                temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(catalog,indent=2)+'\n');temporary.replace(path)
            scene, _ = index_catalog(ROOT)
        print(f"Indexed {len(scene['cells'])} spatial cells: {scene['revision']}")
    elif args.command == 'publish':
        from publish_viewer import publish
        # Publication owns all asset locks before invoking the unlocked builder.
        publish(args, assets, fingerprint, _build)
    elif args.command in ('explain', 'plan'):
        explain(args)
    elif args.command == 'lod':
        lod(args)
    else:
        build(args)


if __name__ == '__main__':
    main()
