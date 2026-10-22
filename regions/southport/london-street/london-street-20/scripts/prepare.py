"""Deterministic authored brick and slate maps; no photographic pixels."""
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

# Slate courses aligned by the roof face UVs, not world-axis projection.
rows = y // 64
columns = ((x + (rows % 2) * 32) // 64) % 8
shade = rng.normal(0, 8, (8, 8))[rows, columns]
slate = np.array([72, 78, 80]) + shade[:, :, None]
slate = slate + rng.normal(0, 1.8, (n, n, 1))
joints = (y % 64 < 3) | ((x + (rows % 2) * 32) % 64 < 2)
slate[joints] *= .62
Image.fromarray(np.uint8(np.clip(slate, 0, 255))).save(out / 'slate.png')

# Fine speckled granite used on the substantial shopfront piers.
granite = np.array([146,147,141]) + rng.normal(0,18,(n,n,1))
granite[rng.random((n,n))<.08] *= .55
Image.fromarray(np.uint8(np.clip(granite,0,255))).save(out/'granite.png')
