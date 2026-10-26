"""Shared measured ground; water and bridge supports remain separate."""
import os
from pathlib import Path
from southport3d.elevation import Elevations
SURFACES=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/marine-lake-south.json')
PAVEMENT=SURFACES.surface('south-mainland')
BRIDGE=SURFACES.surface('south-venetian')
def grade(x,y):return PAVEMENT.height(x,y)
