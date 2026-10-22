"""Portable LOD recipe validation and publication metadata helpers (no bpy)."""
import hashlib
import json
import math
from pathlib import Path
import re


def safe_id(value):
    return isinstance(value, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) is not None


def load_recipe(path):
    recipe = json.loads(Path(path).read_text())
    if recipe.get('schema_version') != 1 or recipe.get('scope') not in {'component-pilot', 'asset'}:
        raise ValueError('LOD recipe requires schema_version 1 and an explicit scope')
    for field in ('levels', 'targets'):
        rows = recipe.get(field, [])
        if not rows or any(not safe_id(row.get('id')) for row in rows):
            raise ValueError(f'{field} needs nonempty, path-safe IDs')
        if len({row['id'] for row in rows}) != len(rows):
            raise ValueError(f'Duplicate {field} ID')
    last_texture = 8192
    for level in recipe['levels']:
        size = level['texture_size']
        if type(size) is not int or size < 64 or size > last_texture or size & (size - 1):
            raise ValueError('Texture sizes must be non-increasing powers of two, 64..8192')
        last_texture = size
    names = []
    level_ids = {level['id'] for level in recipe['levels']}
    for target in recipe['targets']:
        if not isinstance(target.get('object'), str) or not target['object']:
            raise ValueError('Each target must name an exact source object')
        names.append(target['object'])
        if set(target.get('actions', {})) != level_ids:
            raise ValueError('Every component needs an explicit decision at every level')
        direction = target.get('view_direction', [])
        if len(direction) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in direction) or not any(direction):
            raise ValueError('Target needs a finite nonzero view_direction')
        for action in target['actions'].values():
            if action.get('strategy') not in {'omit', 'replace', 'generator', 'decimate'} or not action.get('reason', '').strip():
                raise ValueError('Each action requires a supported strategy and a reason')
            if action['strategy'] == 'omit':
                continue
            for key in ('cage_extrusion_m', 'max_sampled_error_m'):
                value = action.get(key, target.get(key))
                if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                    raise ValueError(f'{key} must be positive and finite')
            if action.get('uv') not in {'smart', 'planar-xy', 'lathe', 'box'}:
                raise ValueError('Explicit supported UV layout required')
            if action['strategy'] == 'decimate' and not 0 < action.get('ratio', 0) < 1:
                raise ValueError('Decimation needs a ratio between zero and one')
            if action['strategy'] == 'replace':
                if action.get('shape') not in {'panel', 'box', 'lathe'}:
                    raise ValueError('Unsupported replacement shape')
                if action['shape'] == 'panel' and action['uv'] != 'planar-xy':
                    raise ValueError('Panel replacement requires planar UVs')
                if action['shape'] == 'box' and action['uv'] != 'box':
                    raise ValueError('Box replacement requires the six-face atlas')
                if action['shape'] == 'lathe':
                    profile = action.get('profile', [])
                    if len(profile) < 2 or any(len(r) != 2 or not all(math.isfinite(v) for v in r) or r[1] <= 0 for r in profile):
                        raise ValueError('Lathe requires finite (z, positive radius) rings')
                    if any(a[0] >= b[0] for a, b in zip(profile, profile[1:])):
                        raise ValueError('Lathe profile heights must increase')
                    if type(action.get('segments')) is not int or not 8 <= action['segments'] <= 4096 or action['uv'] != 'lathe':
                        raise ValueError('Lathe requires 8..4096 segments and a lathe atlas')
            if action['strategy'] == 'generator':
                generator = action.get('generator', '')
                if generator == 'heightfield':
                    grid = action.get('grid', [])
                    if len(grid) != 2 or any(type(n) is not int or not 2 <= n <= 512 for n in grid):
                        raise ValueError('Heightfield needs two grid dimensions between 2 and 512')
                    source = (Path(path).parent / action['source_npz']).resolve()
                    if not source.is_relative_to(Path(path).parent.resolve()) or source.suffix != '.npz' or not source.is_file():
                        raise ValueError('Heightfield source must be an asset-local NPZ')
                    if action['uv'] != 'planar-xy':
                        raise ValueError('Heightfields require planar UVs')
                elif not re.fullmatch(r'[a-z][a-z0-9_]*:[a-z][a-z0-9_]*', generator):
                    raise ValueError('Generator must name an asset module:function')
    if len(names) != len(set(names)):
        raise ValueError('Source objects must not be duplicated in the recipe')
    return recipe


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def file_record(path, root):
    path = Path(path)
    return {'uri': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha256(path)}
