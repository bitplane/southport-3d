"""Procedural decking, six 200 mm boards across a repeating metric atlas."""
import numpy as np
from PIL import Image

def run(root):
    y,x=np.mgrid[:512,:512];rng=np.random.default_rng(15025)
    board=(x*6//512);grain=np.sin(y*.13+x*.09)*1.6+np.sin(y*.39+x*.022)*1.5
    shade=np.array([3,-4,1,5,-2,-1])[board]+grain+rng.normal(0,1.1,x.shape)
    rgb=np.stack([108+shade,102+shade,87+shade],axis=2)
    seam=(x*6%512)<10;rgb[seam]=[44,43,36]
    Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(root/'textures/deck.png')
