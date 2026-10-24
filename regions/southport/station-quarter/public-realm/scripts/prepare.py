"""Author repeating paving PBR maps; never samples reference photographs."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'textures';out.mkdir(exist_ok=True)
n=256;rng=np.random.default_rng(743);yy,xx=np.mgrid[:n,:n];row=yy//43;col=((xx+(row%2)*32)%n)//64
noise=rng.normal(0,1.2,(n,n));variation=rng.uniform(-9,9,(7,5))[row,col]
# Four-by-six staggered rectangular slabs over a 3.6 m repeat.
xjoint=(xx+(row%2)*32)%64;yjoint=yy%43
joint=(xjoint<1.1)|(yjoint<1.1);height=np.where(joint,0,.0015)
dy,dx=np.gradient(height,3.6/n);normal=np.stack([-dx,-dy,np.ones_like(dx)],2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
Image.fromarray(np.uint8(np.clip((normal+1)*127.5,0,255))).save(out/'paving-normal.png')
for name,color in [('mixed',(123,130,132)),('pale',(169,170,166)),('dark',(65,72,76))]:
 a=np.array(color)[None,None,:]+variation[:,:,None]+noise[:,:,None];a[joint]*=.72
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/(name+'.png'))
