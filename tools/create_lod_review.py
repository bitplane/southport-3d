"""Generate a local, disposable before/after LoD inspection page from checked GLBs."""
import argparse
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]


def create(asset,baseline):
    current=ROOT/'build'/asset/'package'
    dest=ROOT/'dist'/'reviews'/asset;dest.mkdir(parents=True,exist_ok=True)
    variants={}
    for label,folder,level in [('Detail',current,'detail'),('Walk',current,'walk'),('Previous District',baseline,'district'),('New District',current,'district')]:
        manifest=json.loads((folder/'manifest.json').read_text());files=[f for f in manifest['files'] if f['level']==level]
        prefix=label.lower().replace(' ','-');entries=[]
        for f in files:
            name=prefix+'-'+f['path'];shutil.copy2(folder/f['path'],dest/name);entries.append(name)
        variants[label]={'files':entries,**{key:sum(f[key] for f in files) for key in ('triangles','bytes','gpuBytesEstimate')}}
    (dest/'variants.json').write_text(json.dumps(variants))
    source=next(p for p in (ROOT/'regions').rglob('asset.json') if json.loads(p.read_text())['id']==asset)
    publication=json.loads((source.parent/'publication.json').read_text())
    (dest/'views.json').write_text(json.dumps(publication['views']))
    shutil.copy2(ROOT/'viewer/lod-review.html',dest/'index.html')
    print('http://127.0.0.1:8765/reviews/'+asset+'/index.html')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--asset',required=True);p.add_argument('--baseline',type=Path,required=True);a=p.parse_args();create(a.asset,a.baseline)
