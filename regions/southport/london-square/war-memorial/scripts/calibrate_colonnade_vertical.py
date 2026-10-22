"""Recompute the explicitly conditional height diagnostic from native pixels."""
from pathlib import Path
import json
import statistics

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'research/colonnade_vertical_proportion_study.json'
report=json.loads(path.read_text())
bottom=report['anchors']['shaft_bottom_m'];top=report['anchors']['parapet_top_m']
for sample in report['sources']:
    p=sample['landmarks_y_px'];span=p['shaft_bottom']-p['parapet_top']
    assert span>0
    sample['upper_stack_to_fluted_shaft_ratio']=(p['shaft_top']-p['parapet_top'])/(p['shaft_bottom']-p['shaft_top'])
    sample['conditional_landmark_z_m']={k:bottom+(p['shaft_bottom']-v)/span*(top-bottom) for k,v in p.items()}
keys=set().union(*(s['conditional_landmark_z_m'] for s in report['sources']))
report['conditional_summary']={}
for key in sorted(keys):
    values=[s['conditional_landmark_z_m'][key] for s in report['sources'] if key in s['conditional_landmark_z_m']]
    report['conditional_summary'][key]={'mean_m':statistics.mean(values),'range_m':[min(values),max(values)],'sample_count':len(values)}
path.write_text(json.dumps(report,indent=2)+'\n')
print('CONDITIONAL_HEIGHT_DIAGNOSTIC',len(report['sources']),'column samples')
print('shaft_top',report['conditional_summary']['shaft_top'])
