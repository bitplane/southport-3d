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
    if name=='sandstone':
        # Authored irregular coursed rubble, with varied weathered stone faces.
        image=Image.new('RGB',(512,512),(174,157,127));draw=ImageDraw.Draw(image)
        y=-12
        while y<512:
            h=int(rng.integers(15,27));x=-int(rng.integers(10,70))
            while x<512:
                w=int(rng.integers(24,78));tone=float(rng.normal(0,22))
                c=tuple(int(np.clip(v+tone,40,235)) for v in colour)
                draw.polygon([(x+2,y+2),(x+w-2,y+1),(x+w-1,y+h-2),(x+1,y+h-1)],fill=c)
                x+=w
            y+=h
        data=np.asarray(image).astype(float)+rng.normal(0,5,(512,512,1))
        # Preserve the family mean so reduced maps do not change masonry colour.
        data+=np.array(colour)-data.mean(axis=(0,1))
        image=Image.fromarray(np.clip(data,0,255).astype('uint8'))
    image.save(ROOT/'textures'/f'{name}.png')
