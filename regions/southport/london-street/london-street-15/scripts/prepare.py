"""Deterministic authored brick, clay tile and flag maps; no photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image

out = Path(__file__).resolve().parents[1] / 'textures'
out.mkdir(exist_ok=True)
rng = np.random.default_rng(1515)
n = 512
y, x = np.mgrid[:n, :n]

# Common red brick: 1.8 x .60 m repeat, eight courses, pale lime mortar.
rows = y // 64
cols = ((x + (rows % 2) * 32) // 64) % 8
brick = np.array([132, 62, 42]) + rng.normal(0, 11, (8, 8))[rows, cols][:, :, None]
brick = brick + rng.normal(0, 3, (n, n, 1))
joints = (y % 64 < 4) | ((x + (rows % 2) * 32) % 64 < 3)
brick[joints] = np.array([150, 136, 116]) + rng.normal(0, 3, (joints.sum(), 1))
Image.fromarray(np.uint8(np.clip(brick, 0, 255))).save(out / 'brick.png')

# Red clay plain tiles: small courses parallel to the eaves (2.4 x 2.2 m repeat).
rows = y // 24
cols = ((x + (rows % 2) * 16) // 32) % 16
tile = np.array([150, 66, 46]) + rng.normal(0, 13, (22, 16))[rows % 22, cols][:, :, None]
tile = tile + rng.normal(0, 4, (n, n, 1))
tile[(y % 24 < 3)] *= .58
tile[((x + (rows % 2) * 16) % 32 < 2)] *= .75
Image.fromarray(np.uint8(np.clip(tile, 0, 255))).save(out / 'tile.png')

# Grey concrete flags for the alley floor (1 m repeat over the texture).
flag = np.array([128, 126, 120]) + rng.normal(0, 5, (n, n, 1))
flag[(y % 256 < 3) | (x % 256 < 3)] *= .6
Image.fromarray(np.uint8(np.clip(flag, 0, 255))).save(out / 'flag.png')
