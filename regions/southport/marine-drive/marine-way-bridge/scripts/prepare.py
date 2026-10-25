"""Small reproducible concrete texture; no source photograph pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1];(r/'textures').mkdir(exist_ok=True)
a=np.random.default_rng(2004).normal(0,2.0,(256,256,1));base=np.array([161,161,151])[None,None,:];im=np.clip(base+a,0,255).astype('uint8');im[:2]=[131,134,128];Image.fromarray(im).save(r/'textures/concrete.png')
