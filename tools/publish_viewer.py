"""Build asset packages and a local, content-addressed viewer catalog."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

from publication import load_publication, inspect_glb, resize_glb_textures, east_north_offset

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.lod import sha256


def publish(args, assets, fingerprint, build):
    """Freeze writers while packaging; build must be the unlocked callback."""
    from contextlib import ExitStack
    from build_lock import asset_lock

    inventory = assets()
    selected = set(getattr(args, 'asset', []) or [])
    if selected:
        unknown = selected - inventory.keys()
        if unknown:raise ValueError('Unknown publication assets: '+', '.join(sorted(unknown)))
        inventory = {key:value for key,value in inventory.items() if key in selected}
        if any(not (source/'publication.json').is_file() for source,_ in inventory.values()):
            raise ValueError('Selected asset has no publication recipe')
    with ExitStack() as locks:
        locks.enter_context(asset_lock(ROOT, "catalog"))
        for key in sorted(inventory):
            locks.enter_context(asset_lock(ROOT, key))
        retained=[]
        catalog=ROOT/'dist/catalog.json'
        if selected and catalog.exists():
            retained=[entry for entry in json.loads(catalog.read_text())['assets'] if entry['id'] not in selected]
        return _publish(args, lambda: inventory, fingerprint, build, retained)


def _publish(args, assets, fingerprint, build, retained=()):
    world=json.loads((ROOT/'viewer/world.json').read_text())
    entries=list(retained)
    for key,(source,asset) in assets().items():
        config=source/'publication.json'
        if not config.exists():
            print('No publication recipe; skipping',key);continue
        spec=load_publication(config);runtime=ROOT/'build'/key
        # Always ask the stage runner: unchanged stages are cheap verified hits,
        # and validation-only changes must not bypass publication validation.
        build(SimpleNamespace(asset=key,stage='all',threads=args.threads,blender=args.blender,
                              views=[],force=args.rebuild))
        from build_state import Stages
        stages=Stages(ROOT,source,asset,runtime,args.blender,args.threads)
        signature=stages.state['nodes']['master']['key']
        source_blend=(runtime/spec['source_blend']).resolve()
        if not source_blend.is_relative_to(runtime.resolve()) or not source_blend.is_file():raise ValueError('Invalid source blend')
        if stages.reason('master'):raise ValueError('Master changed before packaging')
        package=runtime/'package';manifest_path=package/'manifest.json'
        previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        dependencies=previous.get('dependencies',[])
        package_inputs=stages.inputs('package',dependencies)
        # Host-side inspection/repacking is part of the package recipe too.
        package_inputs['host_tools']={name:sha256(ROOT/'tools'/name) for name in
            ('publish_viewer.py','publication.py','publication_schema.py','check_lods.py')}
        reuse=(not args.rebuild and previous.get('inputs')==package_inputs and
               all((package/f['path']).is_file() and sha256(package/f['path'])==f['sha256']
                   for f in previous.get('files',[])) and bool(previous.get('files')))
        if not reuse:
            work=runtime/'package-work'
            if work.exists():shutil.rmtree(work)
            work.mkdir();log=runtime/'logs/package.log'
            stages.snapshot_inputs();stages.deps=set()
            before=stages.inputs('package',[])
            stages.run_script(stages.snapshot/'tools/blender_package.py',True,
                ('--source',str(source_blend),'--asset',str(stages.snapshot/'asset'),'--output',str(work)))
            if stages.reason('master'):raise ValueError('Master changed during packaging')
            if before!=stages.inputs('package',[]):raise ValueError('Package inputs changed during baking')
            for path in set(stages.deps)|set(map(Path,before['files'])):
                if not path.is_file() or sha256(path)!=stages.snapshot_digest(path):
                    raise ValueError('Package dependency changed during baking: '+str(path))
            dependencies=sorted(map(str,stages.deps))
            package_inputs=stages.inputs('package',dependencies)
            package_inputs['host_tools']={name:sha256(ROOT/'tools'/name) for name in
                ('publish_viewer.py','publication.py','publication_schema.py','check_lods.py')}
            package_signature=hashlib.sha256(json.dumps(package_inputs,sort_keys=True).encode()).hexdigest()
            assembly=json.loads((work/'assembly.json').read_text());files=[]
            for item in assembly['files']:
                path=work/item['path'];limit=spec['levels'][item['level']]['texture_size']
                if limit:resize_glb_textures(path,limit)
                info=inspect_glb(path)
                if limit and any(max(size)>limit for size in info['textureDimensions']):raise ValueError('Exported texture exceeds its level budget')
                files.append(dict(item,**info,sha256=sha256(path)))
            for part in spec['parts']:
                levels={f['level']:f for f in files if f['part']==part['id']}
                for a,b in [('detail','walk'),('walk','district')]:
                    if a in levels and b in levels and levels[b]['triangles']>levels[a]['triangles']:raise ValueError('Placed triangles increased in a lower level')
            metadata={'schema_version':1,'asset':key,'inputs':package_inputs,'dependencies':dependencies,'build_signature':package_signature,'source_fingerprint':signature,'source_blend_sha256':assembly['source_sha256'],'files':files,'coverage':assembly['coverage']}
            (work/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
            if package.exists():shutil.rmtree(package)
            work.rename(package)
        else:
            print('Reusing checked package:',key,flush=True)
        metadata=json.loads((package/'manifest.json').read_text())
        # Asset-specific appearance checks run on new AND reused packages before
        # the catalog is replaced. A valid GLB alone does not prove a sound bake.
        for script in asset.get('publication_checks', []):
            check=(runtime/'scripts'/script).resolve()
            if not check.is_relative_to((runtime/'scripts').resolve()) or not check.is_file():
                raise ValueError('Invalid publication check: '+script)
            print('Checking published asset:',key,script,flush=True)
            subprocess.run([sys.executable,str(check),'--package',str(package),'--recipe',str(config)],
                           cwd=runtime,check=True)

        east,north=east_north_offset(world['origin_wgs84_lat_lon'],asset['origin_wgs84_lat_lon'])
        coordinates=spec['coordinates']
        entry={'id':key,'name':asset['name'],'areaName':spec['area_name'],'status':spec['status'],
               'position':[east,coordinates['elevation_m'],-north],
               'rotationY':math.radians(coordinates['yaw_from_east_degrees']) if coordinates['frame']=='site' else 0,
               'views':spec['views'],'walkSpawn':spec['walk_spawn'],'parts':[]}
        for part in spec['parts']:
            files=[f for f in metadata['files'] if f['part']==part['id']]
            # Prefer detailed bounds for stable switching at every level.
            baseline=next((f for f in files if f['level']=='detail'),files[0])
            result={'id':part['id'],'name':part['name'],'bounds':baseline['bounds'],'ground':part.get('ground',False),'levels':{}}
            if part.get('fixed_level'):result['fixedLevel']=part['fixed_level']
            for item in files:
                result['levels'][item['level']]={k:item[k] for k in ('bytes','sha256','triangles','uniqueTriangles','gpuBytesEstimate','bounds')}
                result['levels'][item['level']]['uri']=f"assets/{key}/{item['part']}-{item['level']}-{item['sha256'][:16]}.glb"
                result['levels'][item['level']]['source_path']=str(package/item['path'])
            entry['parts'].append(result)
        entries.append(entry)
    if not entries:raise ValueError('No publishable assets were found')
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    old_catalog=json.loads((dist/'catalog.json').read_text()) if (dist/'catalog.json').exists() else {'assets':[]}
    def uris(catalog):return {f['uri'] for a in catalog['assets'] for p in a['parts'] for f in p['levels'].values()}
    for entry in entries:
        for part in entry['parts']:
            for record in part['levels'].values():
                if 'source_path' not in record:
                    if not (dist/record['uri']).is_file():raise ValueError('Missing retained published asset: '+record['uri'])
                    continue
                source=Path(record.pop('source_path'));destination=dist/record['uri'];destination.parent.mkdir(parents=True,exist_ok=True)
                if not destination.exists():
                    try:os.link(source,destination)
                    except OSError:shutil.copy2(source,destination)
    viewer_version=install_viewer(dist)
    catalog={'schema_version':1,'worldOrigin':world['origin_wgs84_lat_lon'],'coordinateSystem':'East, up, south (metres)','lodPolicy':world['lodPolicy'],'assets':sorted(entries,key=lambda entry:entry['id'])}
    catalog['viewerVersion']=viewer_version
    catalog['revision']=hashlib.sha256(json.dumps(catalog,sort_keys=True).encode()).hexdigest()
    temporary=dist/'catalog.json.tmp';temporary.write_text(json.dumps(catalog,indent=2)+'\n');temporary.replace(dist/'catalog.json')
    from spatial_index import index_catalog
    _, cells = index_catalog(ROOT)
    retire_resources(dist,uris(catalog) | cells)
    print('Viewer package ready:',dist,flush=True)
    print('Serve with: python3 tools/serve.py   →   http://127.0.0.1:8765',flush=True)


def install_viewer(dist):
    """Install one coherent snapshot of viewer sources, returning its identity."""
    names=('index.html','style.css','app.js','lod.js','streamer.js','snags.js','view-state.js',
           'live.js','spatial.js','spatial-streamer.js')
    snapshot={name:(ROOT/'viewer'/name).read_bytes() for name in names}
    if any((ROOT/'viewer'/name).read_bytes()!=data for name,data in snapshot.items()):
        raise ValueError('Viewer sources changed during snapshot')
    version=hashlib.sha256()
    for name,data in snapshot.items():
        version.update(name.encode());version.update(data)
        target=dist/(name+'.tmp');target.write_bytes(data);target.replace(dist/name)
    return version.hexdigest()


def retire_resources(dist, current, now=None):
    """Retain obsolete resources for 24 hours after retirement, even across builds."""
    now=time.time() if now is None else now
    retired_path=dist/'retired-resources.json'
    retired=json.loads(retired_path.read_text()) if retired_path.exists() else {}
    published={p.relative_to(dist).as_posix() for p in (dist/'assets').rglob('*.glb')}
    published.update(p.relative_to(dist).as_posix() for p in (dist/'cells').glob('*.json'))
    for uri in published-current:retired.setdefault(uri,now)
    for uri in list(retired):
        if uri in current or uri not in published:del retired[uri]
        elif now-retired[uri]>86400:
            path=(dist/uri).resolve()
            if any(path.is_relative_to((dist/folder).resolve()) for folder in ('assets','cells')):path.unlink(missing_ok=True)
            del retired[uri]
    tmp=dist/'retired-resources.json.tmp';tmp.write_text(json.dumps(retired));tmp.replace(retired_path)
