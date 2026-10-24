"""Deterministic authored masonry and slate maps; no photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(101218)
for name,rgb,rows,columns in [('brick',(140,66,43),10,10),('slate',(77,80,79),8,6),('render',(201,198,181),0,0)]:
    pixels=np.clip(np.array(rgb)[None,None,:]+rng.normal(0,3,(512,512,1)),0,255).astype('uint8')
    im=Image.fromarray(pixels);draw=ImageDraw.Draw(im)
    if rows:
        dy=512/rows;dx=512/columns
        for row in range(rows):
            y=round(row*dy)
            draw.line((0,y,512,y),fill=tuple(max(0,c-21) for c in rgb),width=2)
            for col in range(-1,columns+1):
                x=round((col+(row%2)*.5)*dx)
                draw.line((x,y,x,round(y+dy)),fill=tuple(max(0,c-17) for c in rgb),width=2)
    im.save(root/'textures'/f'{name}.png')
