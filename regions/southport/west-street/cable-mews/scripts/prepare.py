"""Authored stretcher-bond brick map; no photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(2468);n=512;y,x=np.mgrid[:n,:n];row=y//64;col=((x+(row%2)*32)//64)%8
shade=rng.normal(0,7,(8,8))[row,col]+rng.normal(0,2,(n,n))
a=np.array([145,70,51])[None,None,:]+shade[:,:,None]
joint=(y%64<4)|((x+(row%2)*32)%64<3);a[joint]=np.array([164,140,122])+rng.normal(0,2,(joint.sum(),1))
Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/'brick.png')
