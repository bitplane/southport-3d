"""Authored stone cladding and mottled polished pier textures; no photo inputs."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(118122);n=512;y,x=np.mgrid[:n,:n]
noise=rng.normal(0,.9,(n,n))
colour=np.array([186,183,169])[None,None,:]+noise[:,:,None]
colour[(x%128<1)|(y%128<1)]*=.80
Image.fromarray(np.uint8(np.clip(colour,0,255))).save(out/'cladding.png')
# Multiscale mineral-like mottling on green-grey shopfront piers.
coarse=rng.uniform(0,1,(32,32));im=Image.fromarray(np.uint8(coarse*255)).resize((n,n),Image.Resampling.BICUBIC)
a=np.asarray(im)/255;veins=np.sin(x*.04+y*.023+3*a)
base=np.array([126,137,116])[None,None,:];v=(a-.5)*80+veins*13
Image.fromarray(np.uint8(np.clip(base+v[:,:,None],0,255))).save(out/'pier.png')
