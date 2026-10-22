"""Record or verify a completed local checkpoint without changing model assets.

Run after export, validation, rendering, visual review and progress updates.
Use --verify before resuming work to detect any changed or missing inputs.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'research/checkpoint_manifest.json'

def record(path):
    data=path.read_bytes()
    return {'path':str(path.relative_to(ROOT)),'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest()}

if '--verify' in sys.argv:
    manifest=json.loads(DEST.read_text())
    for item in manifest['files']+manifest['reproducibility_files']:
        actual=record(ROOT/item['path'])
        assert actual==item,('Checkpoint file changed',item['path'])
    print('CHECKPOINT_FILES_VERIFIED',len(manifest['files']),len(manifest['reproducibility_files']))
else:
    progress=json.loads((ROOT/'research/progress_checkpoint.json').read_text())
    validation=json.loads((ROOT/'research/validation_report.json').read_text())
    assert progress['checkpoint_artifacts_ready'] and not progress['in_progress']
    assert isinstance(progress['goal_complete'],bool)
    if progress['goal_complete']:
        assert progress['goal_status']=='complete','Completion must be recorded through the goal workflow'
    assert validation['glb_reimport_success']
    assert validation['file_bytes']==(ROOT/'models/london-square-exterior.glb').stat().st_size
    artifacts=[ROOT/'models/london-square-exterior.blend']
    artifacts+=sorted((ROOT/'models').glob('*.glb'))
    artifacts+=sorted((ROOT/'renders').glob('[0-9][0-9]_*.png'))
    artifacts+=[ROOT/'renders/contact-sheet.png']
    support={ROOT/'README.txt'}
    for key in ('build_log','export_log','validation_log','render_log'):
        if key in progress:
            log=ROOT/progress[key]
            assert log.is_file(),('Missing checkpoint log',key)
            support.add(log)
    for name in progress.get('study_artifacts',[]):
        path=ROOT/name
        assert path.is_file(),('Missing reviewed study artifact',name)
        support.add(path)
    support.update((ROOT/'scripts').glob('*.py'))
    support.update(p for p in (ROOT/'research').rglob('*.json') if p!=DEST)
    support.update((ROOT/'research/relief-data').glob('*.npz'))
    support.update((ROOT/'textures').glob('*.png'))
    catalog=json.loads((ROOT/'research/reference_catalog.json').read_text())
    for item in catalog['images']+catalog.get('documents',[]):
        for key in ('local_file','local_page'):
            if key in item:
                p=ROOT/item[key]
                if p.exists():support.add(p)
    for name in ('iwm-1228.html','wmo-140024.html','historic-england-1379604.html','osm-london-square.xml'):
        p=ROOT/'references/pages'/name
        if p.exists():support.add(p)
    manifest={'checkpoint':progress['checkpoint'],'date':datetime.now(timezone.utc).isoformat(),
              'goal_complete':progress['goal_complete'],'files':[record(p) for p in artifacts],
              'reproducibility_files':[record(p) for p in sorted(support)],
              'validation':'research/validation_report.json',
              'review':progress['visual_review'],
              'scope':'Research checkpoint; geometry confidence and outstanding work remain in modelling_spec and progress_checkpoint.'}
    DEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print('CHECKPOINT_MANIFEST_WRITTEN',len(artifacts),len(support))
