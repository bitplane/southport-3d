"""Shared bounded profiles, including exact West/Nevill legacy handovers."""
import os
from pathlib import Path
from southport3d.elevation import Elevations
SURFACES=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/marine-lake-south.json')
PAVEMENT=SURFACES.surface('south-mainland')
BRIDGE=SURFACES.surface('south-venetian')
RETURN=SURFACES.surface('south-nevill-return')
BLEND=SURFACES.surface('south-west-blend')
import json
D=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/marine-lake-south/public-realm/research/layout.json').read_text())
def in_polygon(x,y,points):
 inside=False
 for a,b in zip(points,points[1:]+points[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def grade(x,y):
 if in_polygon(x,y,D['esplanade_inland_polygon']):return SURFACES.surface('south-esplanade').height(x,y)
 return (RETURN if x>=-81.84 else BLEND if x>=-97.84 else PAVEMENT).height(x,y)
