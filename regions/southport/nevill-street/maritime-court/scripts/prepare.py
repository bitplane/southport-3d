"""Deterministic authored buff-brick texture; no reference-image pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parents[1]/'textures';p.mkdir(exist_ok=True)
n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(30141910)
r=y//32;c=((x+(r%2)*32)//64)%8
v=rng.normal(0,9,(16,8))[r,c];a=np.array([164,139,102])+v[:,:,None]+rng.normal(0,2,(n,n,1))
j=(y%32<2)|((x+(r%2)*32)%64<2);a[j]=np.array([155,145,124])
Image.fromarray(np.uint8(np.clip(a,0,255))).save(p/'buff-brick.png')
