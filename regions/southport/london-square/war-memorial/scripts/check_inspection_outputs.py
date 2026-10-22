"""Decode the completed views and exercise their Chafa SSH commands.

python3 scripts/check_inspection_outputs.py --render-log research/render-0.7.log
Run only after render_views.py and contact_sheet.py have finished.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--render-log',required=True)
parser.add_argument('--inherit-manifest',help='Previous checkpoint manifest for unchanged, isolated views')
parser.add_argument('--inherit-reason',help='Why the inherited cameras cannot show the edited geometry')
args=parser.parse_args()
tree=ast.parse((ROOT/'scripts/render_views.py').read_text())
views=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign)
           and any(isinstance(t,ast.Name) and t.id=='views' for t in node.targets))
expected={row[0] for row in views}
log=(ROOT/args.render_log).read_text()
assert '\0' not in log,'Render log still contains holes from overlapping writers'
assert not any(s in log for s in ('Traceback (most recent call last)','Error: Python:'))
recorded=re.findall(r'^RENDERED (\S+)',log,re.M)
rendered=set(recorded)
assert rendered<=expected,('Unexpected completed render markers',rendered-expected)
assert recorded==[name for name,_ in views if name in rendered],'Repeated or out-of-order render completion markers'
if rendered==expected:
    mtimes=[(ROOT/'renders'/(name+'.png')).stat().st_mtime_ns for name,_ in views]
    assert all(a<b for a,b in zip(mtimes,mtimes[1:])),'Final PNG timestamps do not follow the completed render pass'
inherited=[]
if expected!=rendered:
    assert args.inherit_manifest and args.inherit_reason,('Missing completed render markers',expected-rendered)
    previous=json.loads((ROOT/args.inherit_manifest).read_text())
    old={item['path']:item for item in previous['files']}
    for name in sorted(expected-rendered):
        relative='renders/'+name+'.png'
        assert relative in old,('Missing inherited view',relative)
        raw=(ROOT/relative).read_bytes()
        assert len(raw)==old[relative]['bytes'] and hashlib.sha256(raw).hexdigest()==old[relative]['sha256'],('Inherited view changed',relative)
        inherited.append({'file':relative,'sha256':old[relative]['sha256'],'checkpoint':previous['checkpoint']})
assert 'Saved as "london-square-exterior.blend"' in log,'Final scene save not confirmed'
report={'checkpoint':json.loads((ROOT/'research/progress_checkpoint.json').read_text())['checkpoint'],
        'ordered_unique_render_markers':True,'png_timestamps_in_render_order':True if rendered==expected else None,
        'render_log':args.render_log,'completed_render_markers':len(rendered),
        'all_final_pngs_decoded':[],'chafa_checks':[],
        'inherited_unchanged_views':inherited,'inheritance_manifest':args.inherit_manifest,
        'inheritance_reason':args.inherit_reason,
        'scope':'PNG decoding and terminal output checks; visual comparison recorded separately'}
for name in sorted(expected)+['contact-sheet']:
    path=ROOT/'renders'/(name+'.png')
    with Image.open(path) as im:
        im.load();size=im.size
    report['all_final_pngs_decoded'].append({'file':str(path.relative_to(ROOT)),
                                            'pixels':size,'decoded':True})
for name,size in [('04_ne_colonnade_inner','140x50'),('15_capital','100x70'),
                  ('16_mourning_close','100x70'),('21_wreath_trophy','120x50'),
                  ('32_window_lintel','120x50'),('33_window_surround','100x70'),
                  ('43_obelisk_wwii','100x70'),('contact-sheet','120x80')]:
    command=['chafa','-f','symbols','--size',size,'renders/'+name+'.png']
    run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=45)
    assert run.returncode==0 and len(run.stdout)>500,(command,run.stderr)
    report['chafa_checks'].append({'command':command,'exit_code':run.returncode,'stdout_bytes':len(run.stdout)})
(ROOT/'research/chafa_check.json').write_text(json.dumps(report,indent=2)+'\n')
print('INSPECTION_OUTPUTS_CHECKED',len(expected),'renders',len(report['chafa_checks']),'Chafa commands')
