from pathlib import Path
from PIL import Image
import numpy as np
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(128);n=512;y,x=np.mgrid[:n,:n]
row=y//64;col=((x+(row%2)*64)%512)//128
v=rng.uniform(-5,5,(8,4))[row,col]+rng.normal(0,.9,(n,n))
a=np.array([183,181,170])[None,None,:]+v[:,:,None]
joint=((x+(row%2)*64)%128<1)|(y%64<1);a[joint]*=.89
Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/'stone.png')
row=y//42;col=((x+(row%2)*32)%512)//64
v=rng.uniform(-9,9,(13,8))[row,col]+rng.normal(0,1,(n,n))
a=np.array([68,76,81])[None,None,:]+v[:,:,None];a[(y%42<2)|((x+(row%2)*32)%64<1)]*=.7
Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/'slate.png')
