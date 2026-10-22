"""Deterministic authored cladding, aggregate spandrels and red tiles; no photos."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(116);n=512;y,x=np.mgrid[:n,:n]
for name,base,noise,joints in [('cladding',[214,212,201],1.2,True),('spandrel',[145,163,157],11,False),('red-tile',[173,21,28],2,True)]:
 a=np.array(base)[None,None,:]+rng.normal(0,noise,(n,n,1))
 if joints:a[(x%128<1)|(y%64<1)]*=.85
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/(name+'.png'))
