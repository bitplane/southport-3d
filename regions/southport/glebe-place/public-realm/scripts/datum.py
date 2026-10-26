"""Shared measured lane surface and explicit raised-mouth offsets."""
import os,sys
from pathlib import Path
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path.insert(0,str(REPO/'lib'))
from southport3d.elevation import Elevations
E=Elevations(REPO/'regions/southport/elevation/glebe.json')
ROAD=E.surface('glebe-road')
MOUTH=E.surface('glebe-mouth')
