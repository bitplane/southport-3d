"""Small incremental recipe stages with snapshotted inputs and runtime depfiles.

Recipes remain ordinary Python. Master owns models/textures. Leaf stages may not
mutate its outputs. State is committed only after success, under the asset lock.
"""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

VERSION = 1


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    temporary.replace(path)


def files(base):
    return sorted(p for p in Path(base).rglob('*') if p.is_file() and '__pycache__' not in p.parts)


def record(paths):
    return {str(p): sha(p) if p.is_file() else None for p in sorted(set(map(Path, paths)))}


@lru_cache(maxsize=8)
def tool_identity(blender):
    executable = shutil.which(blender)
    if not executable:
        raise ValueError('Blender executable not found: ' + blender)
    executable = Path(executable).resolve()
    stat = executable.stat()
    import numpy
    import PIL
    return {'blender': str(executable), 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns,
            'version': subprocess.check_output([str(executable), '--version'], text=True).splitlines()[0],
            'python': sys.version, 'numpy': numpy.__version__, 'pillow': PIL.__version__}


class Stages:
    def __init__(self, root, source, spec, runtime, blender='blender', threads=12):
        self.root, self.source, self.runtime = map(Path, (root, source, runtime))
        self.spec, self.blender, self.threads = spec, blender, threads
        self.render_views=[]
        self.path = self.runtime / 'build-state.json'
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {}
        if self.state.get('version') != VERSION:
            self.state = {'version': VERSION, 'nodes': {}}
        self.identity = tool_identity(blender)
        self.snapshot = self.runtime / 'inputs'
        self.runtime.mkdir(parents=True, exist_ok=True)
        (self.runtime / 'logs').mkdir(exist_ok=True)

    def static_inputs(self, stage):
        paths = [self.root / 'tools' / name for name in ('build_state.py', 'trace_run.py')]
        # Directory membership guards against new modules shadowing prior imports.
        membership = [str(p.relative_to(self.root)) for folder in ('lib', 'tools')
                      for p in files(self.root / folder) if p.suffix == '.py']
        membership += [str(p.relative_to(self.source)) for p in files(self.source / 'scripts')]
        if stage == 'master':
            paths += files(self.source / 'research')
            paths += [p for p in self.source.iterdir() if p.is_file() and p.name not in ('asset.json', 'publication.json', 'lod.json')]
            scripts = [self.spec['build'][s] for s in ('prepare', 'geometry')]
        elif stage == 'validate':
            scripts = [self.spec['build']['validate'], *self.spec.get('validation_checks', [])]
        elif stage == 'render':
            scripts = [self.spec['build']['render'], 'contact_sheet.py']
        elif stage == 'export':
            scripts = [self.spec['build']['export']]
        elif stage == 'package':
            scripts = []
            paths += [self.source / 'publication.json']
            # JSON-named generators are recorded by the runtime tracer. Research
            # remains conservative for C-side image/numeric data loading.
            paths += files(self.source / 'research')
            paths += [self.root / 'tools' / name for name in
                      ('blender_package.py', 'blender_lod.py', 'publish_viewer.py',
                       'publication.py', 'publication_schema.py', 'check_lods.py')]
        else:
            raise ValueError('Unknown stage: ' + stage)
        paths += [self.source / 'scripts' / name for name in scripts]
        for name in self.spec.get('build_inputs', {}).get(stage, []):
            path = (self.root / name).resolve()
            if not path.is_relative_to(self.root.resolve()) or not path.is_file():
                raise ValueError('Invalid declared build input: ' + name)
            paths.append(path)
        meta = {k:v for k,v in self.spec.items() if k not in ('build', 'validation_checks', 'publication_checks', 'build_inputs')}
        return paths, {'identity': self.identity, 'membership': sorted(membership),
                       'metadata': meta if stage == 'master' else {}, 'scripts': scripts}

    def inputs(self, stage, dependency_paths=None):
        paths, parameters = self.static_inputs(stage)
        if dependency_paths is None:
            dependency_paths = self.state['nodes'].get(stage, {}).get('dependencies', [])
        paths += [Path(p) for p in dependency_paths]
        parameters['files'] = record(paths)
        if stage == 'render':parameters['views']=self.render_views
        if stage == 'validate':
            parameters['export'] = self.state['nodes'].get('export', {}).get('key')
        if stage != 'master':
            parameters['master'] = self.state['nodes'].get('master', {}).get('key')
        return parameters

    def reason(self, stage):
        node = self.state['nodes'].get(stage)
        if not node:
            return 'no successful stage record'
        now = self.inputs(stage)
        if now != node['inputs']:
            for path, value in now['files'].items():
                if node['inputs']['files'].get(path) != value:
                    return 'input changed: ' + path
            return 'dependencies, recipe or tool identity changed'
        for path, digest in node['outputs'].items():
            if not Path(path).is_file() or sha(path) != digest:
                return 'output missing or changed: ' + path
        return None

    def package_reason(self):
        if self.reason('master'):return 'upstream master needs rebuilding'
        manifest=self.runtime/'package/manifest.json'
        if not manifest.exists():return 'no successful package record'
        previous=json.loads(manifest.read_text())
        current=self.inputs('package',previous.get('dependencies',[]))
        current['host_tools']={name:sha(self.root/'tools'/name) for name in
            ('publish_viewer.py','publication.py','publication_schema.py','check_lods.py')}
        if previous.get('inputs')!=current:return 'package inputs or recipe changed'
        for item in previous['files']:
            path=self.runtime/'package'/item['path']
            if not path.is_file() or sha(path)!=item['sha256']:
                return 'package output missing or changed: '+str(path)
        return 'up to date'

    def save(self):
        atomic_json(self.path, self.state)

    def snapshot_inputs(self):
        # Legacy recipes generate material/geometry manifests under research/.
        # Preserve only verified outputs of successful stages, never arbitrary
        # leftovers from failed runs. A new master clears all node records first.
        generated={}
        for node in self.state.get('nodes',{}).values():
            for name,digest in node.get('outputs',{}).items():
                path=Path(name)
                if path.is_relative_to(self.runtime/'research'):
                    if not path.is_file() or sha(path)!=digest:
                        raise ValueError('Generated stage input missing or changed: '+name)
                    generated[path]=path.read_bytes()
        if self.snapshot.exists():
            shutil.rmtree(self.snapshot)
        self.snapshot.mkdir()
        for name in ('lib', 'tools', 'regions'):
            shutil.copytree(self.root / name, self.snapshot / name,
                            ignore=shutil.ignore_patterns('__pycache__', 'node_modules', 'output', 'profile'))
        shutil.copytree(self.snapshot / self.source.relative_to(self.root), self.snapshot / 'asset',
                        ignore=shutil.ignore_patterns('__pycache__'))
        for declarations in self.spec.get('build_inputs', {}).values():
            for name in declarations:
                original=(self.root / name).resolve()
                if not original.is_relative_to(self.root.resolve()) or not original.is_file():
                    raise ValueError('Invalid declared build input: '+name)
                target=self.snapshot / original.relative_to(self.root)
                if not target.exists():
                    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
        # Snapshot first, then hash. A mixed concurrent source edit is detected by
        # comparing the complete source copy against live input bytes below.
        self.snapshot_hashes = record(files(self.snapshot))
        if json.loads((self.snapshot / 'asset/asset.json').read_text()) != self.spec:
            raise ValueError('Asset manifest changed while snapshotting')
        for name in ('scripts', 'research'):
            dest = self.runtime / name
            if dest.exists(): shutil.rmtree(dest)
            shutil.copytree(self.snapshot / 'asset' / name, dest)
        for path,data in generated.items():
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)

    def live_path(self, path):
        path = Path(path)
        if path.is_relative_to(self.snapshot / 'asset'):
            return self.source / path.relative_to(self.snapshot / 'asset')
        if path.is_relative_to(self.snapshot):
            return self.root / path.relative_to(self.snapshot)
        for name in ('scripts', 'research'):
            if path.is_relative_to(self.runtime / name):
                if name=='research':
                    original=self.snapshot/'asset'/path.relative_to(self.runtime)
                    if not original.is_file() or (path.is_file() and sha(path)!=sha(original)):
                        return None  # Generated stage output, not a live source input.
                return self.source / path.relative_to(self.runtime)
        if path.is_relative_to(self.root) and not path.is_relative_to(self.root / 'build'):
            return path
        return None

    def snapshot_digest(self, live):
        if live.is_relative_to(self.source):
            path = self.snapshot / 'asset' / live.relative_to(self.source)
        elif live.is_relative_to(self.root):
            path = self.snapshot / live.relative_to(self.root)
        else:
            return sha(live)
        return self.snapshot_hashes.get(str(path))

    def run_script(self, script, blender=False, extra=()):
        script = Path(script)
        if not script.is_absolute(): script = self.runtime / 'scripts' / script
        dep = self.runtime / 'logs' / (script.stem + '.deps.json')
        dep.unlink(missing_ok=True)
        wrapper = self.snapshot / 'tools/trace_run.py'
        command = ([self.blender, '-b', '--factory-startup', '--threads', str(self.threads),
                    '--python-exit-code', '1', '--python', str(wrapper), '--'] if blender
                   else [sys.executable, str(wrapper)])
        command += [str(script), str(dep), *extra]
        env = dict(os.environ, SOUTHPORT_REPO_ROOT=str(self.snapshot), PYTHONDONTWRITEBYTECODE='1', SOUTHPORT_TRACE_BLENDER='1' if blender else '0')
        log = self.runtime / 'logs' / (script.stem + '.log')
        print(f'Running {script.name}; log: {log}', flush=True)
        with log.open('w') as output:
            subprocess.run(command, cwd=self.runtime, env=env, stdout=output, stderr=subprocess.STDOUT, check=True)
        self.deps.update(p for name in json.loads(dep.read_text()) if (p := self.live_path(Path(name))) is not None and p.is_file())

    def execute(self, stage, force=False, views=()):
        if stage == 'render':self.render_views=list(views)
        why = self.reason(stage)
        if not force and why is None:
            print('Reusing checked stage:', stage, flush=True)
            return False
        if stage != 'master' and self.reason('master'):
            raise ValueError('Master is stale: run build first')
        print(f'{stage}: {why or "forced"}', flush=True)
        self.state['nodes'].pop(stage, None)
        if stage == 'master':
            self.state['nodes'].clear()
            (self.runtime / 'source.sha256').unlink(missing_ok=True)
        self.save()
        self.snapshot_inputs()
        self.deps = set()
        before = self.inputs(stage, [])
        master_outputs = dict(self.state['nodes'].get('master', {}).get('outputs', {}))
        research_before=record(files(self.runtime/'research'))
        if stage == 'master':
            for name in ('models', 'textures', 'renders'):
                dest = self.runtime / name
                if dest.exists(): shutil.rmtree(dest)
                dest.mkdir()
            (self.runtime / 'research/progress_checkpoint.json').write_text('{"checkpoint":"Source build"}')
            self.run_script(self.spec['build']['prepare'])
            self.run_script(self.spec['build']['geometry'], True, ('--no-render', '--no-export'))
            outputs = files(self.runtime / 'models') + files(self.runtime / 'textures')
        elif stage == 'export':
            self.run_script(self.spec['build']['export'], True)
            outputs = [p for p in files(self.runtime / 'models') if p.suffix != '.blend']
        elif stage == 'validate':
            self.run_script(self.spec['build']['validate'], True)
            for script in self.spec.get('validation_checks', []): self.run_script(script)
            outputs = []
        elif stage == 'render':
            self.run_script(self.spec['build']['render'], True, ('--final', *views))
            self.run_script('contact_sheet.py')
            outputs = files(self.runtime / 'renders')
        else:
            raise ValueError('Use package runner for ' + stage)
        outputs += [p for p in files(self.runtime/'research') if research_before.get(str(p))!=sha(p)]
        if stage == 'master' and not any(p.suffix == '.blend' for p in outputs):
            raise ValueError('Master stage produced no Blender file')
        for path, digest in master_outputs.items():
            if not Path(path).is_file() or sha(path) != digest:
                raise ValueError(f'{stage} mutated master output: {path}')
        after = self.inputs(stage, sorted(map(str, self.deps)))
        if before != self.inputs(stage, []):
            raise ValueError('Inputs changed during ' + stage)
        for path in set(self.deps) | set(map(Path, after['files'])):
            if not path.is_file() or sha(path) != self.snapshot_digest(path):
                raise ValueError('Dependency changed during ' + stage + ': ' + str(path))
        key = hashlib.sha256(json.dumps(after, sort_keys=True).encode()).hexdigest()
        self.state['nodes'][stage] = {'key': key, 'inputs': after,
                                     'dependencies': sorted(map(str, self.deps)), 'outputs': record(outputs)}
        self.save()
        return True
