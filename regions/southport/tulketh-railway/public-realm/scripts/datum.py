"""Bounded shared heights; ground and railway remain separate."""
import os
from pathlib import Path
from southport3d.elevation import Elevations
SURFACES=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/tulketh-railway.json')
PAVEMENT=SURFACES.surface('tulketh-pavement')
def grade(x,y):return PAVEMENT.height(x,y)
