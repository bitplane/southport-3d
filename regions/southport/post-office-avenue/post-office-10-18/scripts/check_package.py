"""Prevent small sign textures from making Walk more expensive than Detail."""
import argparse,json
from pathlib import Path


def check(package):
    files=json.loads((package/'manifest.json').read_text())['files']
    totals={level:{key:sum(f[key] for f in files if f['level']==level)
                   for key in ('triangles','bytes','gpuBytesEstimate')}
            for level in ('detail','walk','district')}
    for fine,coarse in [('detail','walk'),('walk','district')]:
        for key in totals[fine]:
            if totals[coarse][key]>=totals[fine][key]:
                raise ValueError(f'{coarse} {key} is not smaller than {fine}: {totals}')
    print('Monotone triangle/download/GPU budgets passed:',totals)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True)
    check(p.parse_args().package)
