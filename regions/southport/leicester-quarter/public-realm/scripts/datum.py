"""Shared measured terrain for the road canvas and building foundations."""
import os
import sys
from pathlib import Path
REPO = Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path.insert(0, str(REPO/'lib'))
from southport3d.elevation import Elevations
SURFACE = Elevations(REPO/'regions/southport/elevation/leicester-quarter.json').surface('leicester-quarter-pavement')
def grade(x,y):
    return SURFACE.height(x,y)
