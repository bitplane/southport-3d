"""Canopy feet use the same rough paving controls as the street."""
import os
from pathlib import Path
from functools import lru_cache
from southport3d.terrain import GroundControls
@lru_cache(maxsize=1)
def ground():
 return GroundControls(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/ground-controls.json')
def post_base(d,x):
 y=-2.40
 return ground().height(d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x)+.12-d['base_z']
