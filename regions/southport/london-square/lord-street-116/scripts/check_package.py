"""Catch missed window bake rays which can evade valid-normal checks."""
import argparse,json
from pathlib import Path

def check(package,recipe):
    report=json.loads((package/'assembly.json').read_text())
    spec=json.loads(recipe.read_text());checked=0
    for row in report['prototypes']:
        if row['rule']!='windows':continue
        size=spec['levels'][row['level']]['texture_size']
        # Planar receivers fill 96% of each UV axis; dilation covers most of the
        # remaining border. Previously short cages covered only 82–89%.
        for channel in ['base-color','roughness']:
            coverage=row['bake_checks'][channel]['covered_pixels']/(size*size)
            if coverage<.95:
                raise ValueError(f"{row['source_object']} {channel}: {coverage:.1%} coverage; inspect projection cage")
        checked+=1
    if 'district_envelope' in spec:
        envelope=report.get('envelope')
        if not envelope or set(envelope['parts'])!=set(spec['district_envelope']['parts']):raise ValueError('Missing envelope coverage')
        for part,row in envelope['parts'].items():
            for channel,stats in row['bake_checks'].items():
                if stats['receiver_coverage']<.97:raise ValueError('Incomplete envelope projection: '+part+' '+channel)
        print('Envelope projection checks passed')
    elif not checked:raise ValueError('No window bake checks found')
    if checked:print(f'Window bake coverage passed for {checked} prototypes')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,required=True);parser.add_argument('--recipe',type=Path,required=True);args=parser.parse_args();check(args.package,args.recipe)
