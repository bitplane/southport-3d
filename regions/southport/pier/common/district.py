"""Fixed-budget section envelope, authored separately from the detailed mesh."""
import json
from blender_envelope import Surfaces
from shapes import create

def surfaces(asset):
    config=json.loads((asset/'research/section.json').read_text());s=Surfaces(['deck','structure','fittings'])
    for row in create(config,coarse=True).items:
        s.part=row['part'];v=row['vertices'];weight = 8 if row['name'].startswith('rail post') else 4 if row['name'].startswith('column ') else .025 if row['name'].startswith(('handrail','chord','deck fascia')) else row['weight']
        kw=dict(weight=weight,cage=row['cage_m'])
        if len(v)==4:s.quad(row['name'],v,**kw)
        else:
            for i in range(1,len(v)-1):s.triangle(row['name']+' cap '+str(i),[v[0],v[i],v[i+1]],**kw)
    return s.result
