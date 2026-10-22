"""Author repeatable material maps; no reference photographs become textures."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
# sRGB encoding of the Detail ashlar's linear (.626, .545, .397).
# Keeping the same albedo prevents a whole-facade colour jump at Walk.
rng = np.random.default_rng(1892)
for name, colour in [('sandstone',(207,195,169)),('slate',(91,98,88)),('rear-brick',(130,94,70))]:
    n = 512
    noise = rng.normal(0, 2.2, (n,n,1))
    values = np.clip(np.array(colour)[None,None,:] + noise, 0, 255).astype('uint8')
    im = Image.fromarray(values)
    draw = ImageDraw.Draw(im)
    if name == 'sandstone':
        for y in range(0,n,128):
            draw.line((0,y,n,y),fill=(179,168,145),width=2)
            for x in range((y//128%2)*256,n,256):draw.line((x,y,x,y+128),fill=(189,178,154),width=1)
    else:
        height = 64 if name == 'slate' else 48
        width = 96 if name == 'slate' else 160
        for y in range(0,n,height):
            draw.line((0,y,n,y),fill=(53,59,54) if name=='slate' else (89,82,71),width=3)
            for x in range(-(y//height%2)*width//2,n,width):
                draw.line((x,y,x,y+height),fill=(60,65,59) if name=='slate' else (89,82,71),width=2)
    im.save(ROOT/'textures'/f'{name}.png')
