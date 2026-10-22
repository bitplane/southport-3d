"""Author repeating paving PBR maps; never samples reference photographs."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'textures';out.mkdir(exist_ok=True)
n=512;rng=np.random.default_rng(743);yy,xx=np.mgrid[:n,:n];row=yy//85;col=((xx+(row%2)*64)%n)//128
noise=rng.normal(0,1.2,(n,n));variation=rng.uniform(-9,9,(7,5))[row,col]
# Four-by-six staggered rectangular slabs over a 3.6 m repeat.
xjoint=(xx+(row%2)*64)%128;yjoint=yy%85
joint=(xjoint<1.1)|(yjoint<1.1);height=np.where(joint,0,.0015)
dy,dx=np.gradient(height,3.6/n);normal=np.stack([-dx,-dy,np.ones_like(dx)],2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
Image.fromarray(np.uint8(np.clip((normal+1)*127.5,0,255))).save(out/'paving-normal.png')
for name,color in [('mixed',(151,145,130)),('pale',(182,178,162)),('dark',(65,72,76))]:
 a=np.array(color)[None,None,:]+variation[:,:,None]+noise[:,:,None];a[joint]*=.72
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/(name+'.png'))
# Authored non-directional asphalt aggregate.
for name,color in [('asphalt',(66,67,65)),('red-road',(111,76,68))]:
 noise=rng.normal(0,5,(n,n,1));a=np.array(color)[None,None,:]+noise
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/(name+'.png'))
print('Authored five repeating colour maps and one joint normal map')

# Non-directional authored lawn grain; no satellite or photograph pixels.
a=np.array([88,116,53])[None,None,:]+rng.normal(0,5,(n,n,1))
Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/'grass.png')

# Small dark block pavers seen on the Lord Street service carriageway.
bx=xx/n*18;by=yy/n*36;rows=np.floor(by).astype(int)
joints=((bx+(rows%2)*.5)%1<.035)|(by%1<.035)
pixels=np.array([72,75,72])[None,None,:]+rng.normal(0,2,(n,n,1))
pixels[joints]*=.70
Image.fromarray(np.uint8(np.clip(pixels,0,255))).save(out/'service-road.png')
