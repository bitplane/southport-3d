"""Post contact with the existing named Nevill pavement grade; no new ground."""
import json,os
from pathlib import Path

def post_base(d,x):
 g=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/nevill-street/public-realm/research/layout.json').read_text())['grade']
 y=d['y']+d['shear_y']*x-2.40
 t=max(0,min(1,(y-g['start_y'])/(g['top_y']-g['start_y'])))
 return g['start_z']+t*(g['top_z']-g['start_z'])-d['base_z']
