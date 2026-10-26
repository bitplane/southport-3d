"""Measured common pavement; every placement must supply both coordinates."""
import os,sys
from pathlib import Path
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(REPO/'lib'))
from southport3d.elevation import Elevations
SURFACE=Elevations(REPO/'regions/southport/elevation/london-square.json').surface('london-square-pavement')
def grade(y,road=False,*,x):return SURFACE.height(x,y)-(.12 if road else 0)
