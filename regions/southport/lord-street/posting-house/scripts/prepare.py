"""Deterministic authored masonry and slate maps, never reference-image pixels."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(1901)
for name, colour, course, width in [('brick',(153,77,53),32,112),('stone',(196,184,157),128,256),('slate',(92,101,105),64,96)]:
    values=np.clip(np.array(colour)[None,None,:]+rng.normal(0,2,(512,512,1)),0,255).astype('uint8')
    im=Image.fromarray(values);d=ImageDraw.Draw(im)
    joint=(109,101,88) if name=='brick' else (166,155,132) if name=='stone' else (63,71,74)
    for y in range(0,512,course):
        d.line((0,y,512,y),fill=joint,width=2)
        for x in range(-(y//course%2)*width//2,512,width):d.line((x,y,x,y+course),fill=joint,width=2)
    im.save(ROOT/'textures'/f'{name}.png')
