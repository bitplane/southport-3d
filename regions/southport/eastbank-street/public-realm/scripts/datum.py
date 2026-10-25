"""Shared named elevation surface; all levels consume the same bounded profile."""
import os
from pathlib import Path
from southport3d.elevation import Elevations
SURFACES=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/eastbank.json')
PAVEMENT=SURFACES.surface('eastbank-pavement')
def grade(x,y):return PAVEMENT.height(x,y)
