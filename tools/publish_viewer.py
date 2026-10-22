"""Build asset packages and a local, content-addressed viewer catalog."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

from publication import load_publication, inspect_glb, resize_glb_textures, east_north_offset

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.lod import sha256


def publish(args, assets, fingerprint, build):
    world=json.loads((ROOT/'viewer/world.json').read_text())
    entries=[]
    for key,(source,asset) in assets().items():
        config=source/'publication.json'
        if not config.exists():
            print('No publication recipe; skipping',key);continue
        spec=load_publication(config);runtime=ROOT/'build'/key
        signature=fingerprint(source);stamp=runtime/'source.sha256'
        if not stamp.exists() or stamp.read_text().strip()!=signature or args.rebuild:
            build(SimpleNamespace(asset=key,stage='all',threads=args.threads,blender=args.blender,views=[]))
        source_blend=(runtime/spec['source_blend']).resolve()
        if not source_blend.is_relative_to(runtime.resolve()) or not source_blend.is_file():raise ValueError('Invalid source blend')
        digest=hashlib.sha256()
        for value in [signature,sha256(source_blend),config.read_text()]:digest.update(value.encode())
        for name in ['blender_package.py','blender_lod.py','publication.py']:
            digest.update((ROOT/'tools'/name).read_bytes())
        package_signature=digest.hexdigest();package=runtime/'package';manifest_path=package/'manifest.json'
        reuse=False
        if manifest_path.exists() and not args.rebuild:
            previous=json.loads(manifest_path.read_text())
            reuse=previous.get('build_signature')==package_signature and all((package/f['path']).is_file() and sha256(package/f['path'])==f['sha256'] for f in previous['files'])
        if not reuse:
            work=runtime/'package-work'
            if work.exists():shutil.rmtree(work)
            work.mkdir();log=runtime/'logs/package.log'
            command=[args.blender,'-b','--factory-startup','--threads',str(args.threads),'--python-exit-code','1','--python',str(ROOT/'tools/blender_package.py'),'--','--source',str(source_blend),'--asset',str(source),'--output',str(work)]
            print(f'Building viewer levels for {key}; log: {log}',flush=True)
            with log.open('w') as output:subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True)
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
            metadata={'schema_version':1,'asset':key,'build_signature':package_signature,'source_fingerprint':signature,'source_blend_sha256':assembly['source_sha256'],'files':files,'coverage':assembly['coverage']}
            (work/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
            if package.exists():shutil.rmtree(package)
            work.rename(package)
        else:
            print('Reusing checked package:',key,flush=True)
        metadata=json.loads((package/'manifest.json').read_text())
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
                result['levels'][item['level']]={k:item[k] for k in ('bytes','sha256','triangles','uniqueTriangles','gpuBytesEstimate')}
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
                source=Path(record.pop('source_path'));destination=dist/record['uri'];destination.parent.mkdir(parents=True,exist_ok=True)
                if not destination.exists():
                    try:os.link(source,destination)
                    except OSError:shutil.copy2(source,destination)
    for name in ('index.html','style.css','app.js','lod.js','streamer.js'):
        target=dist/(name+'.tmp');shutil.copy2(ROOT/'viewer'/name,target);target.replace(dist/name)
    catalog={'schema_version':1,'worldOrigin':world['origin_wgs84_lat_lon'],'coordinateSystem':'East, up, south (metres)','lodPolicy':world['lodPolicy'],'assets':entries}
    temporary=dist/'catalog.json.tmp';temporary.write_text(json.dumps(catalog,indent=2)+'\n');temporary.replace(dist/'catalog.json')
    # Keep one previous catalog's resources for open browser tabs; bound disk growth.
    history=dist/'previous-catalog.json'
    previous=json.loads(history.read_text()) if history.exists() else {'assets':[]}
    keep=uris(catalog)|uris(old_catalog)
    for uri in uris(previous)-keep:
        path=(dist/uri).resolve()
        if path.is_relative_to((dist/'assets').resolve()):path.unlink(missing_ok=True)
    history.write_text(json.dumps(old_catalog,indent=2)+'\n')
    print('Viewer package ready:',dist,flush=True)
    print('Serve with: python3 tools/serve.py   →   http://127.0.0.1:8765',flush=True)
