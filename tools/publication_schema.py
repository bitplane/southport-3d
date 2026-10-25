"""Validate the version-one publication contract before launching Blender.

Reject unknown orchestration keys: otherwise a typo can silently disable ground
following or a reduction policy. Generator-specific settings remain opaque and
are validated by the asset's own generator/geometry checks.
"""
import math
from pathlib import Path
import re

LEVELS = ('detail', 'walk', 'district')


def fields(value, required, optional, where):
    if not isinstance(value, dict):
        raise ValueError(f'{where}: expected an object')
    unknown = value.keys() - required - optional
    missing = required - value.keys()
    if unknown or missing:
        raise ValueError(f'{where}: unknown fields {sorted(unknown)}; missing fields {sorted(missing)}')


def text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{where}: expected nonempty text')


def number(value, where):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{where}: expected a finite number')


def vector(value, where):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f'{where}: expected three coordinates')
    for coordinate in value:
        number(coordinate, where)


def rows(value, where):
    if not isinstance(value, list) or not value:
        raise ValueError(f'{where}: expected a nonempty list')
    return value


def unique_ids(values, where):
    seen = set()
    for value in values:
        key = value['id']
        if not isinstance(key, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key):
            raise ValueError(f'{where}: invalid ID {key!r}')
        if key in seen:
            raise ValueError(f'{where}: duplicate ID {key!r}')
        seen.add(key)


def action(value, where):
    fields(value, {'strategy', 'reason'}, {
        'bake', 'uv', 'cage_extrusion_m', 'max_sampled_error_m',
        'shape', 'profile', 'segments', 'generator', 'settings',
        'grid', 'source_npz', 'trim_empty', 'ratio',
    }, where)
    text(value['reason'], where + '.reason')
    strategy = value['strategy']
    if not isinstance(strategy, str) or strategy not in {'keep', 'omit', 'replace', 'generator', 'decimate'}:
        raise ValueError(f'{where}: unsupported strategy')
    if strategy in {'keep', 'omit'}:
        if set(value) != {'strategy', 'reason'}:
            raise ValueError(f'{where}: keep/omit do not accept reduction or bake settings')
        return
    if type(value.get('bake')) is not bool:
        raise ValueError(f'{where}: explicit boolean bake decision required')
    if value.get('uv') not in {'smart', 'planar-xy', 'lathe', 'box'}:
        raise ValueError(f'{where}: explicit supported UV layout required')
    if value['bake']:
        for key in ('cage_extrusion_m', 'max_sampled_error_m'):
            number(value.get(key), where + '.' + key)
            if value[key] <= 0:
                raise ValueError(f'{where}.{key}: must be positive')
    if strategy == 'decimate':
        number(value.get('ratio'), where + '.ratio')
        if not 0 < value['ratio'] < 1:
            raise ValueError(f'{where}: decimation ratio must be between zero and one')
    if strategy == 'replace':
        if value.get('shape') not in {'panel', 'box', 'lathe'}:
            raise ValueError(f'{where}: unsupported replacement shape')
        if value['shape'] == 'lathe':
            profile = rows(value.get('profile'), where + '.profile')
            if len(profile) < 2:
                raise ValueError(f'{where}: lathe requires at least two rings')
            for ring in profile:
                if not isinstance(ring, list) or len(ring) != 2:
                    raise ValueError(f'{where}: expected height/radius pairs')
                for coordinate in ring:
                    number(coordinate, where + '.profile')
                if ring[1] <= 0:
                    raise ValueError(f'{where}: radius must be positive')
            if any(a[0] >= b[0] for a, b in zip(profile, profile[1:])):
                raise ValueError(f'{where}: profile heights must increase')
            if type(value.get('segments')) is not int or not 8 <= value['segments'] <= 4096:
                raise ValueError(f'{where}: lathe requires 8..4096 segments')
    if strategy == 'generator':
        generator = value.get('generator')
        text(generator, where + '.generator')
        if generator == 'heightfield':
            grid = value.get('grid')
            if not isinstance(grid, list) or len(grid) != 2 or any(type(n) is not int or not 2 <= n <= 512 for n in grid):
                raise ValueError(f'{where}: heightfield requires two grid dimensions in 2..512')
            text(value.get('source_npz'), where + '.source_npz')
            if 'trim_empty' in value and type(value['trim_empty']) is not bool:
                raise ValueError(f'{where}: trim_empty must be boolean')
        elif not re.fullmatch(r'[a-z][a-z0-9_]*:[a-z][a-z0-9_]*', generator):
            raise ValueError(f'{where}: generator must name module:function')
        elif not isinstance(value.get('settings'), dict):
            raise ValueError(f'{where}: generator settings must be an object')


def validate_publication(spec):
    fields(spec, {'schema_version', 'source_blend', 'coordinates', 'area_name',
                  'status', 'levels', 'parts', 'views', 'walk_spawn', 'rules'},
           {'excluded_collections', 'district_envelope'}, 'publication')
    if type(spec['schema_version']) is not int or spec['schema_version'] != 1:
        raise ValueError('publication: expected schema_version 1')
    for key in ('source_blend', 'area_name', 'status'):
        text(spec[key], key)
    source = Path(spec['source_blend'])
    if source.is_absolute() or '..' in source.parts or source.suffix != '.blend':
        raise ValueError('source_blend: expected an asset-relative .blend path')

    coordinates = spec['coordinates']
    fields(coordinates, {'frame', 'yaw_from_east_degrees', 'elevation_m'}, set(), 'coordinates')
    if coordinates['frame'] not in {'site', 'east-north'}:
        raise ValueError('coordinates: declare site or east-north frame')
    for key in ('yaw_from_east_degrees', 'elevation_m'):
        number(coordinates[key], 'coordinates.' + key)

    fields(spec['levels'], set(LEVELS), set(), 'levels')
    previous = 8192
    for level in LEVELS:
        fields(spec['levels'][level], {'texture_size'}, set(), 'levels.' + level)
        size = spec['levels'][level]['texture_size']
        # Null retains original maps; reduced levels must declare finite caps.
        if level == 'detail' and size is None:
            continue
        if type(size) is not int or not 64 <= size <= previous or size & (size - 1):
            raise ValueError('levels: texture caps must be non-increasing powers of two, 64..8192')
        previous = size

    parts = rows(spec['parts'], 'parts')
    for i, part in enumerate(parts):
        where = f'parts[{i}]'
        fields(part, {'id', 'name', 'collection'}, {'ground', 'fixed_level', 'support_surface'}, where)
        for key in ('name', 'collection'):
            text(part[key], where + '.' + key)
        if 'ground' in part and type(part['ground']) is not bool:
            raise ValueError(f'{where}.ground: expected boolean')
        if 'support_surface' in part:
            text(part['support_surface'], where + '.support_surface')
            if not part.get('ground'):
                raise ValueError(f'{where}: support_surface requires ground:true')
        if 'fixed_level' in part and part['fixed_level'] not in LEVELS:
            raise ValueError(f'{where}.fixed_level: unknown level')
    unique_ids(parts, 'parts')
    if len({part['collection'] for part in parts}) != len(parts):
        raise ValueError('parts: each collection must belong to exactly one part')

    for i, view in enumerate(rows(spec['views'], 'views')):
        fields(view, {'name', 'position', 'target'}, set(), f'views[{i}]')
        text(view['name'], 'view.name')
        vector(view['position'], 'view.position')
        vector(view['target'], 'view.target')
    fields(spec['walk_spawn'], {'position', 'target'}, set(), 'walk_spawn')
    vector(spec['walk_spawn']['position'], 'walk_spawn.position')
    vector(spec['walk_spawn']['target'], 'walk_spawn.target')

    rules = rows(spec['rules'], 'rules')
    for i, rule in enumerate(rules):
        where = f'rules[{i}]'
        fields(rule, {'id', 'match', 'walk', 'district'}, set(), where)
        text(rule['match'], where + '.match')
        try:
            re.compile(rule['match'])
        except re.error as error:
            raise ValueError(f'{where}.match: invalid regular expression') from error
        for level in ('walk', 'district'):
            action(rule[level], where + '.' + level)
    unique_ids(rules, 'rules')
    if 'district_envelope' in spec:
        envelope=spec['district_envelope']
        fields(envelope, {'generator','reason','parts','max_bytes','max_gpu_bytes'}, {'source_omissions'}, 'district_envelope')
        text(envelope['reason'],'district_envelope.reason')
        for omission in envelope.get('source_omissions',[]):
            fields(omission,{'match','reason'},set(),'district_envelope.source_omissions')
            text(omission['reason'],'source omission reason')
            text(omission['match'],'source omission match')
            try:re.compile(omission['match'])
            except re.error as error:raise ValueError('Invalid source omission regex') from error

        if not isinstance(envelope['generator'],str) or not re.fullmatch(r'[a-z][a-z0-9_]*:[a-z][a-z0-9_]*',envelope['generator']):
            raise ValueError('district_envelope: expected module:function')
        for name in ('max_bytes','max_gpu_bytes'):
            if type(envelope[name]) is not int or envelope[name]<=0:raise ValueError('district_envelope: positive budgets required')
        fields(envelope['parts'], {p['id'] for p in parts}, set(), 'district_envelope.parts')
        for name,part in envelope['parts'].items():
            fields(part, {'atlas','max_triangles','cage_m'}, {'source_parts'}, 'district_envelope.'+name)
            if type(part['max_triangles']) is not int or part['max_triangles']<=0:raise ValueError('Invalid envelope triangle budget')
            if 'source_parts' in part:
                if not isinstance(part['source_parts'],list) or not part['source_parts'] or any(v not in envelope['parts'] for v in part['source_parts']):raise ValueError('Invalid envelope source parts')
            number(part['cage_m'],'envelope cage')
            if part['cage_m']<=0:raise ValueError('Invalid envelope cage')
            if not isinstance(part['atlas'],list) or len(part['atlas'])!=2 or any(type(v) is not int or v<64 or v>spec['levels']['district']['texture_size'] or v&(v-1) for v in part['atlas']):
                raise ValueError('Invalid envelope atlas dimensions')
        texture_floor=sum(part['atlas'][0]*part['atlas'][1]*16 for part in envelope['parts'].values())
        if envelope['max_gpu_bytes']<=texture_floor:
            raise ValueError(f'district_envelope: GPU budget must exceed the atlas memory floor ({texture_floor} bytes), leaving space for mesh buffers')
    excluded = spec.get('excluded_collections', [])
    if not isinstance(excluded, list):
        raise ValueError('excluded_collections: expected a list')
    for item in excluded:
        fields(item, {'name', 'reason'}, set(), 'excluded_collections')
        text(item['name'], 'excluded_collections.name')
        text(item['reason'], 'excluded_collections.reason')
