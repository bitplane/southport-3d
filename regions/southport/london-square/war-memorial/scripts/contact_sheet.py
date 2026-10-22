"""Lay out existing Blender renders with inspection labels; no image retouching."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
paths=sorted((ROOT/'renders').glob('[0-9][0-9]_*.png'))
width,height=640,440;cols=4;rows=(len(paths)+cols-1)//cols
sheet=Image.new('RGB',(cols*width,rows*height+90),'#20252a')
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
draw.text((20,14),'SOUTHPORT / LONDON SQUARE — EXTERIOR STUDY',font=font,fill='white')
checkpoint=json.loads((ROOT/'research/progress_checkpoint.json').read_text())['checkpoint']
draw.text((20,47),checkpoint+' · Dimensions estimated · Interiors and names deferred',font=small,fill='#d7d1bd')
for i,path in enumerate(paths):
    x=(i%cols)*width;y=(i//cols)*height+90
    im=Image.open(path).convert('RGB');im.thumbnail((width-12,height-42),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(width-im.width)//2,y))
    label=path.stem.replace('_',' ')
    draw.text((x+12,y+height-34),label,font=small,fill='white')
sheet.save(ROOT/'renders/contact-sheet.png')
print(ROOT/'renders/contact-sheet.png')
