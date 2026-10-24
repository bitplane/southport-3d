"""Small authored block-paving repeat; no photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
n=256;yy,xx=np.mgrid[:n,:n];row=yy//32;shift=16*(row%2)
joint=((xx+shift)%64<2)|(yy%32<2)
rng=np.random.default_rng(813);colour=np.array([108,96,83])[None,None,:]+rng.normal(0,1.5,(n,n,1));colour[joint]*=.7
Image.fromarray(np.uint8(np.clip(colour,0,255))).save(out/'paving.png')
height=np.where(joint,0,.001);dy,dx=np.gradient(height,1.2/n);normal=np.stack([-dx,-dy,np.ones_like(dx)],2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
Image.fromarray(np.uint8(np.clip((normal+1)*127.5,0,255))).save(out/'paving-normal.png')
