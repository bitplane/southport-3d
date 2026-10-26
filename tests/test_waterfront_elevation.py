"""Deck references retain survey humps and exclude returns from tall structures."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.elevation import Elevations
DATA=ROOT/'regions/southport/elevation'


def test_marine_reference_ignores_pylon_returns():
    evidence=json.loads((DATA/'survey/waterfront-decks.json').read_text())['marine_way']
    field=Elevations(DATA/'marine-drive.json').surface('marine-bridge-measured-reference')
    for sample in evidence['probes']:
        height=field.height(*sample['xy'])-.12
        if sample['s']in evidence['excluded_stations_m']:
            assert 3.7<height<4.8
            if sample['s']==100:assert max(sample['dsm'])>40
        else:
            assert height==pytest.approx(float(np.median(sample['dsm'])),abs=.000501)


def test_venetian_keeps_central_hump_above_approaches():
    evidence=json.loads((DATA/'survey/waterfront-decks.json').read_text())['venetian']
    field=Elevations(DATA/'marine-lake-south.json').surface('south-venetian')
    heights=[]
    for sample in evidence['probes']:
        z=field.height(*sample['xy']);heights.append(z)
        if sample['s']:
            assert z==pytest.approx(float(np.median(sample['dsm'])),abs=.000501)
        else:
            assert abs(z-float(np.median(sample['dsm'])))<.15
    assert max(heights)-max(heights[0],heights[-1])>1.5
    assert heights[0]<.5 and heights[-1]<1


def test_water_remains_independent_and_explicitly_provisional():
    plan=Elevations(DATA/'marine-lake-south.json')
    control=plan.controls['marine-lake']
    assert control['status']=='provisional-water-level-not-surveyed'
    water=plan.surface('south-water')
    assert water.height(-400,400)==water.height(-100,500)
    bridge=plan.surface('south-venetian')
    assert bridge.height(-290,405)>water.height(-290,405)+2
