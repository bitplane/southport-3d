#!/usr/bin/env python3
"""Source checks and isolated, sequential Blender builds."""
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
    digest = hashlib.sha256()
    for base in (source, ROOT / 'lib'):
        for path in sorted(base.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.name not in {'lod.json', 'lod.py', 'publication.json'}:
                digest.update(str(path.relative_to(ROOT)).encode())
                if path == source / 'asset.json':
                    metadata = json.loads(path.read_text())
                    metadata.pop('validation_checks', None)
                    digest.update((json.dumps(metadata, indent=2) + '\n').encode())
                else:
                    digest.update(path.read_bytes())
    return digest.hexdigest()


def build(args):
    source, spec = assets()[args.asset]
    runtime = ROOT / 'build' / args.asset
    signature = fingerprint(source)
    stamp = runtime / 'source.sha256'
    fresh = args.stage in ('build', 'all')
    if not fresh and (not stamp.exists() or stamp.read_text().strip() != signature):
        raise ValueError('Build missing or source changed: run --stage all first')
    runtime.mkdir(parents=True, exist_ok=True)
    if fresh:
        stamp.unlink(missing_ok=True)
        for name in ('scripts', 'research'):
            dest = runtime / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source / name, dest, ignore=shutil.ignore_patterns('__pycache__'))
        # Clear obsolete products when rebuilding changed source.
        for name in ('models', 'renders', 'textures'):
            dest = runtime / name
            if dest.exists():
                shutil.rmtree(dest)
            dest.mkdir()
        (runtime / 'research/progress_checkpoint.json').write_text(json.dumps({'checkpoint': 'Source build'}))
    logs = runtime / 'logs'
    logs.mkdir(exist_ok=True)
    env = dict(os.environ, SOUTHPORT_REPO_ROOT=str(ROOT))

    def run(script, blender=False, extra=()):
        command = ([args.blender, '-b', '--factory-startup', '--threads', str(args.threads), '--python-exit-code', '1', '--python'] if blender else [sys.executable])
        command += [str(runtime / 'scripts' / script)]
        if extra:
            command += ['--', *extra] if blender else list(extra)
        log = logs / (Path(script).stem + '.log')
        print(f'Running {script}; log: {log}', flush=True)
        with log.open('w') as output:
            subprocess.run(command, cwd=runtime, env=env, stdout=output, stderr=subprocess.STDOUT, check=True)

    if fresh:
        run(spec['build']['prepare'])
        run(spec['build']['geometry'], True, ('--no-render', '--no-export'))
        stamp.write_text(signature + '\n')
    if args.stage in ('all', 'export'):
        run(spec['build']['export'], True)
    if args.stage in ('all', 'validate'):
        run(spec['build']['validate'], True)
        for script in spec.get('validation_checks', []):
            run(script)
    if args.stage == 'render':
        run(spec['build']['render'], True, ('--final', *args.views))
        run('contact_sheet.py')
    print(f'Finished: {runtime}')


def lod(args):
    source, spec = assets()[args.asset]
    runtime = ROOT / 'build' / args.asset
    signature = fingerprint(source)
    stamp = runtime / 'source.sha256'
    if not stamp.exists() or stamp.read_text().strip() != signature:
        raise ValueError('Master missing or source changed: run build first')
    recipe_path = source / 'lod.json'
    recipe = load_recipe(recipe_path)
    blend = (runtime / recipe['source_blend']).resolve()
    if not blend.is_relative_to(runtime.resolve()) or not blend.is_file():
        raise ValueError('LOD source must be an existing blend inside the asset runtime')
    work = runtime / 'lod-work'
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    log = runtime / 'logs/lod.log'
    command = [args.blender, '-b', '--factory-startup', '--threads', str(args.threads),
               '--python-exit-code', '1', '--python', str(ROOT / 'tools/blender_lod.py'), '--',
               '--source', str(blend), '--recipe', str(recipe_path), '--output', str(work),
               '--source-fingerprint', signature]
    print(f'Baking LODs; log: {log}', flush=True)
    with log.open('w') as output:
        subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/check_lods.py'), str(work)], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/lod_contact_sheet.py'), str(work)], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/lod_contact_sheet.py'), str(work), '--oblique'], check=True)
    dest = runtime / 'lods'
    if dest.exists():
        shutil.rmtree(dest)
    work.rename(dest)
    print(f'Finished: {dest}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    sub.add_parser('check')
    builder = sub.add_parser('build')
    builder.add_argument('asset')
    builder.add_argument('--stage', choices=['all', 'build', 'export', 'validate', 'render'], default='all')
    builder.add_argument('--threads', type=int, default=12)
    builder.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    builder.add_argument('--views', nargs='*', default=[])
    lodder = sub.add_parser('lod', help='Bake and validate levels from the asset lod.json')
    lodder.add_argument('asset')
    lodder.add_argument('--threads', type=int, default=12)
    lodder.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    publisher = sub.add_parser('publish', help='Build all publication recipes and prepare the local viewer')
    publisher.add_argument('--rebuild', action='store_true')
    publisher.add_argument('--threads', type=int, default=12)
    publisher.add_argument('--blender', default=os.environ.get('BLENDER', 'blender'))
    args = parser.parse_args()
    if args.command == 'list':
        for key in assets():
            print(key)
    elif args.command == 'check':
        check()
    elif args.command == 'publish':
        from publish_viewer import publish
        publish(args, assets, fingerprint, build)
    elif args.command == 'lod':
        lod(args)
    else:
        build(args)


if __name__ == '__main__':
    main()
