"""Deterministic authored masonry/slate maps; no photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(1874)
for name,colour in [('sandstone',(163,145,115)),('ashlar',(172,156,126)),('slate',(81,87,90)),('brick',(133,85,64))]:
    data=np.clip(np.array(colour)[None,None,:]+rng.normal(0,2.2,(512,512,1)),0,255).astype('uint8')
    image=Image.fromarray(data);draw=ImageDraw.Draw(image)
    course=32 if name=='sandstone' else 64
    width=80 if name=='sandstone' else 128
    mortar=tuple(max(0,v-18) for v in colour)
    for row,y in enumerate(range(0,512,course)):
        draw.line((0,y,512,y),fill=mortar,width=2)
        for x in range(-width+(row%2)*width//2,512,width):
            draw.line((x,y,x,y+course),fill=mortar,width=1)
    image.save(ROOT/'textures'/f'{name}.png')
