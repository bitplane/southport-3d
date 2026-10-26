"""Create a procedural 4 m repeat of the garden's sandstone flags.

No reference pixels are used. Joint widths and small colour variations are
visual estimates; the pattern is not an inventory of individual stones.
"""
import numpy as np
from PIL import Image
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
size=512;cell=64;rng=np.random.default_rng(3402)
colour=np.array([.53,.49,.42],dtype=np.float32)
a=np.ones((size,size,4),dtype=np.float32)
for row in range(8):
 for col in range(8):
  noise=rng.uniform(-.035,.035);a[row*cell:(row+1)*cell,col*cell:(col+1)*cell,:3]=colour+noise
# Metric joints at 0.5 m intervals, with a slight warm edge.
a[::cell,:,:3]*=.66;a[:,::cell,:3]*=.66
Image.fromarray(np.uint8(np.clip(a*255,0,255)),'RGBA').save(ROOT/'textures/garden-paving.png')
