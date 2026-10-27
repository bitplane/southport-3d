"""Retained approach grade with a bounded Town Hall handover transition."""
import os
from pathlib import Path
from southport3d.elevation import Elevations

FIELD = Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT']) /
                   'regions/southport/elevation/london-square.json').surface('london-square-pavement')

def legacy_grade(x,y):
    return -.0075-.022*max(-36,min(36,y))

def grade(x,y):
    # The garden's adjoining rough plane owns the north edge and the three
    # sides of its handover polygon. A short linear transition reaches the
    # retained approach datum south of the Town Hall's white return.
    if y >= -35:
        return FIELD.height(x,y)
    if y <= -45:
        return legacy_grade(x,y)
    t = (-35-y)/10
    return (1-t)*FIELD.height(x,-35) + t*legacy_grade(x,-45)
