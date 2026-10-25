#!/usr/bin/env python3
"""Convert downloaded EA DTM into licensed, numeric, millimetre source tiles.

Acquisition is explicit; ordinary asset builds never require the network or
raw reference TIFFs. Uses the measured transform/datum from audit_elevation.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from audit_elevation import Raster, YAW
import math

ROOT = Path(__file__).resolve().parents[1]


def prepare(reference_dir, audit_path, destination):
    raster = Raster(reference_dir/'southport-dtm-1m.tif')
    audit = json.loads(audit_path.read_text())
    if raster.dx != 1 or raster.dy != 1:
        raise ValueError('Expected native one metre DTM')
    if hashlib.sha256(raster.path.read_bytes()).hexdigest() != audit['raster_sha256']:
        raise ValueError('Survey differs from audited raster')
    destination.mkdir(parents=True, exist_ok=True)
    c, s = math.cos(YAW), math.sin(YAW)
    matrix = np.array(audit['world_en_to_bng_affine'])
    matrix[:2] = np.array([[c, s], [-s, c]])@matrix[:2]
    tiles = {}
    # Includes all published geometry and the future pier. One-kilometre tiles
    # keep numerical inputs small and permit geographically scoped dependencies.
    for west in range(332000, 335000, 1000):
        for south in range(416000, 420000, 1000):
            col, row = int(west-raster.x0), int(raster.y0-south-1000)
            values = raster.values[row:row+1000, col:col+1000]
            valid = np.isfinite(values)
            if np.any(abs(values[valid]*1000) > 32767):
                raise ValueError('Terrain exceeds int16 millimetre range')
            z = np.rint(np.where(valid, values, 0)*1000).astype(np.int16)
            name = f'dtm-{west}-{south}.npz'
            np.savez_compressed(destination/name, odn_mm=z, valid=valid)
            tiles[f'{west}_{south}'] = {'path': name, 'sha256': hashlib.sha256((destination/name).read_bytes()).hexdigest()}
    index = json.loads((reference_dir/'dtm-survey-index.json').read_text())
    spec = {
        'schema_version': 1, 'crs': 'EPSG:27700', 'vertical_datum': 'Ordnance Datum Newlyn',
        'resolution_m': 1, 'tile_size_m': 1000,
        'site_xy_to_bng_affine': matrix.tolist(),
        'world_en_to_bng_affine': audit['world_en_to_bng_affine'],
        'local_zero_odn_m': audit['odn_at_local_zero_m'],
        'datum_status': audit['datum_status'],
        'datum_tie': {k: audit[k] for k in ['anchor_site_xy', 'anchor_model_z', 'anchor_odn', 'anchor_offset_spread_m']},
        'projection_fit_max_error_m': audit['projection_fit_max_error_m'],
        'quantisation_max_error_m': .0005,
        'source': {
            'url': 'https://www.data.gov.uk/dataset/01b3ee39-da3f-47b6-83da-dc98e73a461f/lidar-composite-dtm-2022-1m',
            'wcs': 'https://environment.data.gov.uk/spatialdata/lidar-composite-digital-terrain-model-dtm-1m/wcs',
            'coverage_id': '13787b9a-26a4-4775-8523-806d13af58fc__Lidar_Composite_Elevation_DTM_1m',
            'download_bbox_bng': [331000, 415000, 336000, 420000],
            'accessed': '2026-10-25', 'raw_sha256': audit['raster_sha256'],
            'attribution': '© Environment Agency copyright and/or database right 2022. All rights reserved.',
            'licence': 'Open Government Licence v3.0',
            'licence_url': 'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/',
            'survey_index_url': 'https://environment.data.gov.uk/spatialdata/survey-index-files/wfs',
            'survey_records_intersecting_download': [f['properties'] for f in index['features']],
            'source_survey_vertical_accuracy_rmse_m': .15,
        },
        'limitations': 'Bare-earth interpolation is not evidence for bridge decks, water level, stairs or retaining faces. Acquisition varies by survey polygon. Local datum tie is provisional. One metre sampling does not resolve individual stair risers. XY reconstruction error can exceed the raster resolution.',
        'tiles': tiles,
    }
    (destination/'terrain.json').write_text(json.dumps(spec, indent=2)+'\n')
    print('Wrote', len(tiles), 'tiles;', sum((destination/t['path']).stat().st_size for t in tiles.values()), 'bytes')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference-dir', type=Path, default=ROOT.parent/'references/elevation')
    p.add_argument('--audit', type=Path, default=ROOT.parent/'output/elevation/audit.json')
    p.add_argument('--destination', type=Path, default=ROOT/'regions/southport/elevation/survey')
    a = p.parse_args()
    prepare(a.reference_dir, a.audit, a.destination)
