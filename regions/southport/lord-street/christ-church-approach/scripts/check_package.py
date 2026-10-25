"""Fixed per-level ground/furniture budgets measured on the actual exports."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
repo=args.recipe.resolve().parents[4];sys.path.insert(0,str(repo/'tools'))
from publication import inspect_glb
layout=json.loads((args.recipe.parent/'research/layout.json').read_text());assembly=json.loads((args.package/'assembly.json').read_text());rows=[]
for level in ['detail','walk','district']:
    infos=[inspect_glb(args.package/f['path'])for f in assembly['files']if f['level']==level]
    totals={'max_triangles':sum(r['triangles']for r in infos),'max_download_bytes':sum(r['bytes']for r in infos),'max_gpu_bytes':sum(r['gpuBytesEstimate']for r in infos)}
    for key,value in totals.items():assert value<=layout['budgets'][level][key],(level,key,value,layout['budgets'][level][key])
    rows.append({'level':level,**totals})
(args.package/'approach-budget-check.json').write_text(json.dumps(rows,indent=2)+'\n');print('Approach fixed envelope budgets:',rows)
