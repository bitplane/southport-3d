#!/usr/bin/env python3
"""Compare published ground with EA terrain. Diagnostic only; never drape bridges.

Requires existing NumPy/Pillow and system PROJ cs2cs. Survey TIFFs and OSTN15
stay outside Git. Run with --reference-dir ../references/elevation.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from audit_published_coplanar import primitives

ROOT = Path(__file__).resolve().parents[1]
YAW = math.radians(43.5293)


class Raster:
    """North-up EA GeoTIFF, sampled at pixel centres, without extrapolation."""
    def __init__(self, path):
        self.path = Path(path)
        with Image.open(path) as im:
            self.values = np.asarray(im).copy()
            tags = dict(im.tag_v2)
        transform = tags.get(34264)
        if transform:
            if transform[1] or transform[4] or transform[0] <= 0 or transform[5] >= 0:
                raise ValueError('Expected north-up raster')
            self.x0, self.y0 = transform[3], transform[7]
            self.dx, self.dy = transform[0], -transform[5]
        else:
            scale, tie = tags[33550], tags[33922]
            self.dx, self.dy = scale[:2]
            self.x0, self.y0 = tie[3]-tie[0]*self.dx, tie[4]+tie[1]*self.dy
        self.values[~np.isfinite(self.values) | (self.values < -100)] = np.nan

    def sample(self, xy):
        xy = np.asarray(xy)
        col = (xy[..., 0]-self.x0)/self.dx-.5
        row = (self.y0-xy[..., 1])/self.dy-.5
        c, r = np.floor(col).astype(int), np.floor(row).astype(int)
        ok = (c >= 0) & (r >= 0) & (c+1 < self.values.shape[1]) & (r+1 < self.values.shape[0])
        cc, rr = np.clip(c, 0, self.values.shape[1]-2), np.clip(r, 0, self.values.shape[0]-2)
        u, v = col-c, row-r
        z = ((1-u)*(1-v)*self.values[rr, cc]+u*(1-v)*self.values[rr, cc+1]
             +(1-u)*v*self.values[rr+1, cc]+u*v*self.values[rr+1, cc+1])
        return np.where(ok, z, np.nan)


def geographic(origin, en):
    """Inverse local ENU on WGS84, matching the publisher's tangent frame."""
    lat, lon = np.radians(origin)
    a, e2 = 6378137., 6.6943799901413165e-3
    n = a/math.sqrt(1-e2*math.sin(lat)**2)
    base = np.array([n*math.cos(lat)*math.cos(lon), n*math.cos(lat)*math.sin(lon), n*(1-e2)*math.sin(lat)])
    east = np.array([-math.sin(lon), math.cos(lon), 0])
    north = np.array([-math.sin(lat)*math.cos(lon), -math.sin(lat)*math.sin(lon), math.cos(lat)])
    xyz = base+en[:, :1]*east+en[:, 1:]*north
    p = np.hypot(xyz[:, 0], xyz[:, 1])
    phi = np.arctan2(xyz[:, 2], p*(1-e2))
    for _ in range(8):
        n = a/np.sqrt(1-e2*np.sin(phi)**2)
        phi = np.arctan2(xyz[:, 2]+e2*n*np.sin(phi), p)
    return np.column_stack([np.degrees(phi), np.degrees(np.arctan2(xyz[:, 1], xyz[:, 0]))])


def grid_transform(origin, reference_dir):
    grid = reference_dir/'uk_os_OSTN15_NTv2_OSGBtoETRS.tif'
    if not grid.is_file():
        raise ValueError('OSTN15 grid required; do not silently use ballpark projection')
    en = np.array([(x, y) for x in [-2500, 0, 2500] for y in [-2500, 0, 2500]], dtype=float)
    geo = geographic(origin, en)
    env = dict(os.environ, PROJ_DATA=str(reference_dir)+':/usr/share/proj')
    proc = subprocess.run(['cs2cs', 'EPSG:4326', 'EPSG:27700', '-f', '%.6f'],
                          input=''.join(f'{lat} {lon}\n' for lat, lon in geo),
                          capture_output=True, text=True, check=True, env=env)
    bng = np.array([[float(v) for v in line.split()[:2]] for line in proc.stdout.splitlines()])
    design = np.column_stack([en, np.ones(len(en))])
    matrix = np.linalg.lstsq(design, bng, rcond=None)[0]
    residual = np.linalg.norm(design@matrix-bng, axis=1).max()
    if residual > .05:
        raise ValueError(f'Local projection fit error {residual} m')
    return matrix, float(residual)


def site_to_en(xy):
    c, s = math.cos(YAW), math.sin(YAW)
    return np.asarray(xy)@np.array([[c, s], [-s, c]])


def transform(en, matrix):
    en = np.asarray(en)
    return en@matrix[:2]+matrix[2]


def quantiles(values, weights):
    idx = np.argsort(values)
    total = np.cumsum(weights[idx]); total /= total[-1]
    return np.interp([.05, .5, .95], total, values[idx]).tolist()


def run(reference_dir, output):
    output.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((ROOT/'dist/catalog.json').read_text())
    dtm = Raster(reference_dir/'southport-dtm-1m.tif')
    matrix, residual = grid_transform(catalog['worldOrigin'], reference_dir)
    # Explicit provisional datum tie: road beside memorial, away from steps.
    # Road surface at y=0 is -0.1275 in the existing memorial model.
    anchors = np.array([(x, y) for x in [-10.5, 10.5] for y in [-4, 0, 4]])
    anchor_z = -.1275-.022*anchors[:, 1]
    anchor_odn = dtm.sample(transform(site_to_en(anchors), matrix))
    offsets = anchor_odn-anchor_z
    datum = float(np.median(offsets))
    rows, clouds = [], []
    for asset in catalog['assets']:
        for part in asset['parts']:
            if not part.get('ground'):
                continue
            entries = []
            for tri, source in primitives(ROOT/'dist'/part['levels']['detail']['uri'], asset):
                normal = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
                area = abs(normal[:, 1])/2
                valid = (area > .02) & (abs(normal[:, 1]) > .7*np.linalg.norm(normal, axis=1))
                # Centroids are diagnostics weighted by horizontal area; no claim
                # that tiny kerbs or each individual stair tread are measured.
                centre = tri[valid].mean(axis=1)
                if not len(centre):
                    continue
                en = centre[:, [0, 2]]*np.array([1, -1])
                survey = dtm.sample(transform(en, matrix))-datum
                good = np.isfinite(survey)
                entries.append(np.column_stack([en[good], centre[good, 1], survey[good], area[valid][good]]))
            if not entries:
                continue
            points = np.concatenate(entries)
            delta = points[:, 2]-points[:, 3]
            separate = any(k in (part['id']+' '+str(part.get('supportSurface', ''))).lower() for k in ['bridge', 'venetian', 'water'])
            rows.append({'asset': asset['id'], 'part': part['id'], 'support_surface': part.get('supportSurface'),
                         'separate_structure_review': separate, 'samples': len(points),
                         'area_m2': float(points[:, 4].sum()),
                         'model_minus_terrain_p05_median_p95_m': quantiles(delta, points[:, 4]),
                         'area_fraction_over_0_5m': float(points[abs(delta) > .5, 4].sum()/points[:, 4].sum())})
            if not separate:
                clouds.append(points)
        print('Audited', asset['id'], flush=True)
    report = {'catalog_revision': catalog['revision'], 'datum_status': 'provisional road tie; requires anchor review',
              'odn_at_local_zero_m': datum, 'anchor_site_xy': anchors.tolist(),
              'anchor_model_z': anchor_z.tolist(), 'anchor_odn': anchor_odn.tolist(),
              'anchor_offset_spread_m': float(np.ptp(offsets)), 'world_en_to_bng_affine': matrix.tolist(),
              'projection_fit_max_error_m': residual, 'parts': rows,
              'raster_sha256': hashlib.sha256(dtm.path.read_bytes()).hexdigest(),
              'limitations': 'DTM may interpolate removed structures. Water, bridges, stairs and retaining edges need separate evidence. Centroid statistics are horizontal-area weighted, not an acceptance test.'}
    (output/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    cloud = np.concatenate(clouds)
    np.savez_compressed(output/'ground-samples.npz', samples=cloud)
    lo, hi = cloud[:, :2].min(axis=0), cloud[:, :2].max(axis=0)
    scale = 1400/max(hi-lo)
    size = tuple((np.ceil((hi-lo)*scale)+80).astype(int))
    im = Image.new('RGB', size, '#eeeeea'); draw = ImageDraw.Draw(im)
    for e, n, model, survey, _ in cloud[np.argsort(cloud[:, 4])[::-1]]:
        x, y = 40+(e-lo[0])*scale, size[1]-40-(n-lo[1])*scale
        d = max(-3, min(3, model-survey))/3
        colour = (int(100+155*max(d, 0)), int(155*(1-abs(d))), int(100+155*max(-d, 0)))
        draw.ellipse((x-1.3, y-1.3, x+1.3, y+1.3), fill=colour)
    draw.text((12, 10), 'Elevation audit: red=model too high, blue=too low; saturation at 3 m', fill='black')
    im.save(output/'ground-errors.png')
    print(json.dumps({k: report[k] for k in ['odn_at_local_zero_m', 'anchor_offset_spread_m', 'projection_fit_max_error_m']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-dir', type=Path, default=ROOT.parent/'references/elevation')
    parser.add_argument('--output', type=Path, default=ROOT.parent/'output/elevation')
    args = parser.parse_args()
    run(args.reference_dir.resolve(), args.output.resolve())
