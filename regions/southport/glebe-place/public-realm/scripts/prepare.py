"""Authored paving and patchy service asphalt, without reference pixels."""
from pathlib import Path
import numpy as np
from PIL import Image

out=Path(__file__).resolve().parents[1]/'textures'
out.mkdir(exist_ok=True)
rng=np.random.default_rng(51826174)
n=512
y,x=np.mgrid[:n,:n]
for name,colour in [('asphalt',[91,91,84]),('paving',[167,162,145]),('blocks',[81,85,82]),('tactile',[174,142,93])]:
    pixels=np.array(colour)+rng.normal(0,3,(n,n,1))
    if name=='asphalt':
        patches=np.asarray(Image.fromarray(np.uint8(rng.uniform(60,180,(20,20)))).resize((n,n),Image.Resampling.BICUBIC)).astype(float)
        pixels=pixels+(patches-120)[:,:,None]*.22
    if name in ['paving','blocks']:
        row=y//64
        joints=(y%64<2)|((x+(row%2)*32)%(128 if name=='paving' else 64)<2)
        pixels[joints]*=.70
    if name=='tactile':
        dots=((x%32-16)**2+(y%32-16)**2)<36
        pixels[dots]*=1.10
    Image.fromarray(np.uint8(np.clip(pixels,0,255))).save(out/(name+'.png'))
