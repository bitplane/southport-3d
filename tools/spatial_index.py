"""Deterministic loose metric cells over immutable published part records."""
import copy
import hashlib
import json
import math
from pathlib import Path


def world_bounds(bounds, position, yaw):
    c,s=math.cos(yaw),math.sin(yaw)
    points=[(c*x+s*z+position[0],y+position[1],-s*x+c*z+position[2])
            for x in (bounds[0][0],bounds[1][0])
            for y in (bounds[0][1],bounds[1][1])
            for z in (bounds[0][2],bounds[1][2])]
    if not all(math.isfinite(v) for p in points for v in p):raise ValueError('Non-finite spatial bounds')
    return [[min(p[k] for p in points) for k in range(3)],
            [max(p[k] for p in points) for k in range(3)]]


def union(bounds):
    return [[min(b[0][k] for b in bounds) for k in range(3)],
            [max(b[1][k] for b in bounds) for k in range(3)]]


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()


def part_bounds(asset,part):
    local=union([r.get('bounds',part['bounds']) for r in part['levels'].values()])
    return world_bounds(local,asset['position'],asset['rotationY'])


def make_index(catalog, radius=250, margin=64, budget=256*1024*1024):
    groups={}
    for asset in sorted(catalog['assets'],key=lambda a:a['id']):
        revision=hashlib.sha256(encoded(asset)).hexdigest()
        for part in sorted(asset['parts'],key=lambda p:p['id']):
            bounds=part_bounds(asset,part)
            extent=max(bounds[1][k]-bounds[0][k] for k in (0,2))
            size=64
            while size<extent:size*=4
            i,j=[math.floor((bounds[0][k]+bounds[1][k])/2/size) for k in (0,2)]
            key=f'{size}/{i}/{j}'
            group=groups.setdefault(key,{'key':key,'size':size,'i':i,'j':j,'assets':{},'boxes':[]})
            row=group['assets'].setdefault(asset['id'],dict(copy.deepcopy(asset),parts=[],assetRevision=revision))
            row['parts'].append(dict(copy.deepcopy(part),worldBounds=bounds))
            group['boxes'].append(bounds)
    resources={};cells=[]
    for key,group in sorted(groups.items()):
        node={'schema_version':1,'key':key,'assets':list(group['assets'].values())}
        data=encoded(node);digest=hashlib.sha256(data).hexdigest();uri=f'cells/{digest}.json'
        resources[uri]=data
        cells.append({k:group[k] for k in ('key','size','i','j')} | {
            'bounds':union(group['boxes']),'uri':uri,'sha256':digest,'bytes':len(data)})
    scene={k:catalog[k] for k in ('worldOrigin','coordinateSystem','lodPolicy','viewerVersion')}
    scene.update(schema_version=2,catalogRevision=catalog['revision'],cells=cells,
                 streaming={'radius':radius,'margin':margin,'budget':budget,'stagingBudget':128*1024*1024},
                 assets=[{k:v for k,v in a.items() if k!='parts'}|{'parts':[]} for a in catalog['assets']])
    scene['revision']=hashlib.sha256(encoded(scene)).hexdigest()
    return scene,resources


def index_catalog(root):
    """Index last-good outputs, never rebuild or read unselected working drafts."""
    root=Path(root);dist=root/'dist';catalog=json.loads((dist/'catalog.json').read_text())
    from publication import inspect_glb
    # Old catalogs omitted lower-level bounds. Recover from matching checked
    # package metadata, falling back to actual published GLBs; no Detail-only guess.
    for asset in catalog['assets']:
        manifest=root/'build'/asset['id']/'package/manifest.json'
        old=json.loads(manifest.read_text()).get('files',[]) if manifest.exists() else []
        by_hash={f['sha256']:f['bounds'] for f in old}
        for part in asset['parts']:
            for level in part['levels'].values():
                if 'bounds' not in level:
                    level['bounds']=by_hash.get(level['sha256']) or inspect_glb(dist/level['uri'])['bounds']
    world=json.loads((root/'viewer/world.json').read_text())
    policy=world.get('streaming',{})
    scene,resources=make_index(catalog,policy.get('radius',250),policy.get('margin',64),policy.get('budget',256*1024*1024))
    for uri,data in resources.items():
        path=dist/uri;path.parent.mkdir(exist_ok=True)
        if not path.exists():
            tmp=path.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(path)
    tmp=dist/'scene.json.tmp';tmp.write_bytes(encoded(scene));tmp.replace(dist/'scene.json')
    return scene,set(resources)
