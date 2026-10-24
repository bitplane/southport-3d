"""Deterministic authored granite grains; no reference photograph pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(365);size=512
# One metre square. Mottled feldspar with small dark mica/quartz grains.
coarse=np.asarray(Image.fromarray(np.uint8(rng.uniform(40,215,(128,128)))).resize((size,size),Image.Resampling.BILINEAR),dtype=float)/255-.5
fine=rng.normal(0,7,(size,size))
a=np.array([126,87,81])[None,None,:]+(coarse*100+fine)[:,:,None]
mica=rng.random((size,size))<.045;a[mica]*=.40
quartz=rng.random((size,size))<.055;a[quartz]=a[quartz]*.7+70
Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/'granite.png')
