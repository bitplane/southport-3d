"""Check fixed canopy LoD budgets and retain translucent glass in each export."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args();repo=a.recipe.resolve().parents[4];sys.path.insert(0,str(repo/'tools'))
from publication import inspect_glb
from check_lods import read_glb
assembly=json.loads((a.package/'assembly.json').read_text());results=[]
for level,limit in [('detail',12000),('walk',12000),('district',1500)]:
 files=[a.package/r['path']for r in assembly['files']if r['level']==level];assert len(files)==1
 info=inspect_glb(files[0]);assert info['triangles']<=limit and info['bytes']<2000000 and info['gpuBytesEstimate']<2000000,(level,info)
 doc,_=read_glb(files[0]);assert any(m.get('alphaMode')=='BLEND' and m.get('doubleSided') for m in doc.get('materials',[])),(level,'missing translucent glass')
 results.append({'level':level,'triangles':info['triangles'],'bytes':info['bytes'],'gpu':info['gpuBytesEstimate']})
(a.package/'canopy-budget-check.json').write_text(json.dumps(results,indent=2)+'\n');print('Canopy budgets',results)
