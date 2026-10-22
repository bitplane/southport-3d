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

for i in range(4):
 a=np.array([183+i*2,181+i*2,170+i*2])[None,None,:]+rng.normal(0,1.1,(n,n,1))
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/('ashlar'+str(i)+'.png'))

# Painted running-bond brick on the researched rear. 16 x 24 bricks per
# 3.6 x 1.8 metre UV repeat, authored here without photographic pixels.
ny,nx=768,1024;yy,xx=np.mgrid[:ny,:nx];row=yy//32
col=((xx+(row%2)*32)%nx)//64
v=rng.uniform(-5,3,(24,16))[row,col]+rng.normal(0,.65,(ny,nx))
a=np.array([206,205,195])[None,None,:]+v[:,:,None]
joints=(yy%32<2)|((xx+(row%2)*32)%64<2)
a[joints]=np.array([178,179,172])
Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/'rear-white-brick.png')
