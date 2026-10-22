"""Authored material maps; no downloaded photographic texture content."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(840)
for name,colour,course,width in [('brick',(140,80,57),20,58),('slate',(79,83,81),38,82),('spandrel',(165,144,121),0,0),('roof',(193,191,180),0,0)]:
    a=np.clip(np.array(colour)[None,None,:]+rng.normal(0,4 if name=='spandrel' else 2,(512,512,1)),0,255).astype('uint8')
    im=Image.fromarray(a);d=ImageDraw.Draw(im)
    if course:
        for row,y in enumerate(range(0,512,course)):
            d.line((0,y,512,y),fill=tuple(max(0,v-24) for v in colour),width=2)
            for x in range(-width+(row%2)*width//2,512,width):d.line((x,y,x,y+course),fill=tuple(max(0,v-18) for v in colour),width=1)
    im.save(ROOT/'textures'/f'{name}.png')
