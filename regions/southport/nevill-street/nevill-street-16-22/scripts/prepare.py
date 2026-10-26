"""Deterministic authored brick, clay-tile and granite maps; no photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image

out = Path(__file__).resolve().parents[1] / 'textures'
out.mkdir(exist_ok=True)
rng = np.random.default_rng(612)
n = 512
y, x = np.mgrid[:n, :n]

# Eight courses in a 1.8 x .60 metre repeat. Alternating stretchers, fine mortar.
rows = y // 64
columns = ((x + (rows % 2) * 32) // 64) % 8
variation = rng.normal(0, 10, (8, 8))[rows, columns]
brick = np.array([137, 73, 50]) + variation[:, :, None]
brick = brick + rng.normal(0, 3, (n, n, 1))
joints = (y % 64 < 4) | ((x + (rows % 2) * 32) % 64 < 3)
brick[joints] = np.array([154, 139, 119]) + rng.normal(0, 3, (joints.sum(), 1))
Image.fromarray(np.uint8(np.clip(brick, 0, 255))).save(out / 'brick.png')

# Clay-tile courses aligned by the roof face UVs, not world-axis projection.
rows = y // 64
columns = ((x + (rows % 2) * 32) // 64) % 8
shade = rng.normal(0, 8, (8, 8))[rows, columns]
slate = np.array([71, 77, 79]) + shade[:, :, None]
slate = slate + rng.normal(0, 1.8, (n, n, 1))
joints = (y % 64 < 3) | ((x + (rows % 2) * 32) % 64 < 2)
slate[joints] *= .62
Image.fromarray(np.uint8(np.clip(slate, 0, 255))).save(out / 'slate.png')

# Authored speckled polished granite, not photographic source pixels.
granite=np.array([139,119,111])+rng.normal(0,15,(n,n,1))
granite+=rng.normal(0,4,(n,n,3))
Image.fromarray(np.uint8(np.clip(granite,0,255))).save(out/"granite.png")

# Independently authored restrained weathering for the broad charcoal covering.
# Imagery does not resolve its exact material or sheet joint spacing.
weather = rng.normal(0,1.0,(n,n))
for k in range(28):
 fx,fy=rng.integers(-5,6,2)
 if fx==fy==0:continue
 weather += 2.8*np.cos(2*np.pi*(fx*x+fy*y)/n+rng.uniform(0,2*np.pi))/(1+.2*(fx*fx+fy*fy))
cover=np.array([72,75,78])+weather[:,:,None]
Image.fromarray(np.uint8(np.clip(cover,0,255))).save(out/'covering.png')
