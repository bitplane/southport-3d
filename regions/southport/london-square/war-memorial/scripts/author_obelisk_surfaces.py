"""Author metric stone PBR maps from bounded numeric surface recipes.

No photograph pixels are read here. Visible block classes and tip markings
follow the cited photographs; albedo, pit depths and fine shapes are estimates.
Run with system Python (NumPy / Pillow) before build_memorial.py.
"""
from pathlib import Path
import json
import math
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SIZE = 1024
CLASSES = {
    'pale': dict(seed=1923, albedo=[.62, .60, .535], roughness=.79,
                 pits=160, pit_depth_m=.00035, grain_m=.000018),
    'aged': dict(seed=1924, albedo=[.385, .390, .355], roughness=.89,
                 pits=700, pit_depth_m=.0012, grain_m=.000055),
    'pitted': dict(seed=1925, albedo=[.445, .435, .380], roughness=.94,
                   pits=2400, pit_depth_m=.004, grain_m=.00009),
}


def field(rng, width, height, length_x, length_y=None):
    """Periodic, band-limited field with correlation lengths in metres."""
    length_y = length_x if length_y is None else length_y
    kx = np.fft.rfftfreq(SIZE, d=width/SIZE)[None, :]
    ky = np.fft.fftfreq(SIZE, d=height/SIZE)[:, None]
    spectrum = np.fft.rfft2(rng.normal(size=(SIZE, SIZE)))
    spectrum *= np.exp(-2*math.pi**2*((kx*length_x)**2+(ky*length_y)**2))
    a = np.fft.irfft2(spectrum, s=(SIZE, SIZE))
    return np.clip(a/(3*a.std()), -1, 1)


def surface(recipe, width=1., height=1.):
    rng = np.random.default_rng(recipe['seed'])
    broad = field(rng, width, height, .12)
    mottling = field(rng, width, height, .028, .11)
    fine = field(rng, width, height, .0014)
    relief = fine*recipe['grain_m']
    density = field(rng, width, height, .07)
    for _ in range(round(recipe['pits']*width*height)):
        x, y = rng.uniform(0, width), rng.uniform(0, height)
        ix, iy = int(x/width*SIZE), int(y/height*SIZE)
        if rng.random() > np.clip(.58+.85*density[iy, ix], .05, 1):
            continue
        rx, ry = rng.uniform(.0025, .009, 2)
        angle, phase = rng.uniform(0, 2*math.pi, 2)
        radius = max(rx, ry)*1.35
        xs = np.arange(math.floor((x-radius)/width*SIZE), math.ceil((x+radius)/width*SIZE)+1)
        ys = np.arange(math.floor((y-radius)/height*SIZE), math.ceil((y+radius)/height*SIZE)+1)
        dx, dy = xs[None, :]*width/SIZE-x, ys[:, None]*height/SIZE-y
        xx = (dx*math.cos(angle)+dy*math.sin(angle))/rx
        yy = (-dx*math.sin(angle)+dy*math.cos(angle))/ry
        theta = np.arctan2(yy, xx)
        q = (xx**2+yy**2)*(1+.18*np.sin(3*theta+phase)+.09*np.cos(5*theta-phase))
        bowl = np.maximum(1-q, 0)**1.5
        patch = np.ix_(ys % SIZE, xs % SIZE)
        depth = recipe['pit_depth_m']*rng.uniform(.25, 1)
        relief[patch] = np.minimum(relief[patch], -depth*bowl+fine[patch]*recipe['grain_m'])
    relief = np.clip(relief, -recipe['pit_depth_m'], recipe['grain_m'])
    color = np.asarray(recipe['albedo'])[None, None, :]*(1+.23*broad+.12*mottling+.018*fine)[..., None]
    roughness = np.clip(recipe['roughness']+.035*broad+.015*fine, .70, .99)
    return color, roughness, relief, broad, mottling


def save_maps(name, color, roughness, relief, width=1., height=1.):
    dest = ROOT/'textures'
    dest.mkdir(exist_ok=True)
    # Central differences are in metres. +Y is the glTF tangent-space up axis.
    du = (np.roll(relief, -1, axis=1)-np.roll(relief, 1, axis=1))/(2*width/SIZE)
    dv = (np.roll(relief, -1, axis=0)-np.roll(relief, 1, axis=0))/(2*height/SIZE)
    normals = np.stack((-du, -dv, np.ones_like(du)), axis=2)
    normals /= np.linalg.norm(normals, axis=2)[..., None]
    linear = np.clip(color, 0, 1)
    srgb = np.where(linear <= .0031308, 12.92*linear, 1.055*linear**(1/2.4)-.055)
    maps = {'base': srgb, 'normal': normals*.5+.5,
            'roughness': np.repeat(roughness[..., None], 3, axis=2)}
    for kind, pixels in maps.items():
        # Arrays use increasing v upward; PNG scanlines run downward.
        Image.fromarray(np.uint8(np.rint(np.flipud(pixels)*255))).save(dest/f'{name}-{kind}.png')
    return {'name': name, 'resolution': [SIZE, SIZE], 'physical_span_m': [width, height],
            'height_range_m': [float(relief.min()), float(relief.max())],
            'normal_tilt_rms_degrees': float(np.sqrt(np.mean(np.degrees(np.arccos(normals[..., 2]))**2))),
            'roughness_range': [float(roughness.min()), float(roughness.max())],
            'maps': {k: f'textures/{name}-{k}.png' for k in maps}}


def main():
    reports = []
    for key, recipe in CLASSES.items():
        color, roughness, relief, _, _ = surface(recipe)
        reports.append(save_maps('obelisk-'+key, color, roughness, relief))
    p = json.loads((ROOT/'research/obelisk_fixture_calibration.json').read_text())['pyramid']
    width = p['base_width_m']
    height = math.hypot(p['tip_z_m']-p['base_z_m'], width/2)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]/SIZE
    u = (xx-.5)*width
    for face, seed in [('SE', 1940), ('SW', 1941), ('NW', 1942), ('NE', 1943)]:
        recipe = dict(CLASSES['aged'], seed=seed, albedo=[.53, .515, .455], pits=480)
        color, roughness, relief, broad, mottling = surface(recipe, width, height)
        if face in ('SE', 'SW', 'NW'):
            # Face-specific central streaks read in the original photographs.
            # The less visible NE face gets no invented prominent stain.
            rng = np.random.default_rng(seed+100)
            fragments = field(rng, width, height, .007)
            clouds = field(rng, width, height, .025)
            runs = field(rng, width, height, .007, .17)
            centre = -.035*(1-yy)+.025*np.sin(yy*13)*(.3+yy)
            halfwidth = (.018+.075*yy**.8) if face == 'SW' else (.080+.012*(1-yy))
            width_variation = np.clip(1+.50*mottling+.20*broad, .45, 1.55)
            edge = 1-np.abs(u-centre)/(halfwidth*width_variation)
            coverage = np.clip(edge*3+fragments*.8+clouds*.4, 0, 1)
            coverage *= np.clip((yy-.15+clouds*.09)*14, 0, 1)
            coverage *= np.clip((1-yy)*35, 0, 1)
            coverage *= np.clip(.85+.20*clouds+.23*fragments+.16*runs, .25, 1)
            stain = np.array([.36, .285, .055] if face in ('SE', 'SW') else [.25, .27, .215])
            tint = stain[None, None, :]*(1+.18*clouds[..., None])
            color = color*(1-coverage[..., None])+tint*coverage[..., None]
        if face in ('SE', 'NW'):
            # Comparatively pale stone around the photographed slotted feature.
            frame = np.clip((.37-np.abs(u))*70, 0, 1)*np.clip((.17-yy)*70, 0, 1)
            color = color*(1-.20*frame[..., None])+np.array([.64, .62, .55])*.20*frame[..., None]
        reports.append(save_maps('obelisk-tip-'+face.lower(), color, roughness, relief, width, height))
    report = {
        'status': 'Authored photographic interpretation, not measured surface topography',
        'sources': ['commons-3563087', 'commons-obelisk-2', 'commons-war-memorial'],
        'reference_state': 'Post-2008 arrangement; close stone surfaces interpreted from 2011–2013 photographs. This is not a claim of 2026 condition.',
        'method': 'Periodic numeric fields, irregular bounded pit profiles and manually positioned tip stains; no reference image pixels read or embedded',
        'normal_convention': 'OpenGL/glTF tangent space; +Y up; metre-scaled derivatives',
        'shaft_recipes': CLASSES, 'materials': reports,
        'limits': ['Pit depths, albedo and roughness are estimates', 'Fine pit placement is procedural, not a registered scan',
                   'Stain substance and cause are unverified', 'NE face appearance lacks a close reference; generic stone retained'],
    }
    (ROOT/'research/obelisk_surface_materials.json').write_text(json.dumps(report, indent=2)+'\n')
    print('OBELISK_SURFACE_MAPS_AUTHORED', len(reports), 'materials', len(reports)*3, 'maps')


if __name__ == '__main__':
    main()
