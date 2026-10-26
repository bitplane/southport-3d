"""Named bounded geographic surfaces, shared by ground and foundations."""
import os
from pathlib import Path
from southport3d.elevation import Elevations
SURFACES=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/marine-drive.json')
PAVEMENT=SURFACES.surface('marine-mainland')
BRIDGE=SURFACES.surface('marine-bridge-measured-reference')
def grade(x,y):return PAVEMENT.height(x,y)

LOWER=SURFACES.surface('marine-lower-promenade')
