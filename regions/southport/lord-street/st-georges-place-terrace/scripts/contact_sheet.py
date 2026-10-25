from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
names=[name for name in ['building','front','signs','bay','portal','rear','roof'] if (ROOT/'renders'/f'{name}.png').is_file()]
assert names,'No renders to assemble'
canvas=Image.new('RGB',(1500,520*((len(names)+2)//3)),'#eeeeec');draw=ImageDraw.Draw(canvas)
for i,name in enumerate(names):
    im=Image.open(ROOT/'renders'/f'{name}.png').convert('RGB');im.thumbnail((500,490))
    x=(i%3)*500;y=(i//3)*520
    canvas.paste(im,(x+(500-im.width)//2,y+25));draw.text((x+12,y+6),name,fill='black')
canvas.save(ROOT/'renders/contact-sheet.png')
