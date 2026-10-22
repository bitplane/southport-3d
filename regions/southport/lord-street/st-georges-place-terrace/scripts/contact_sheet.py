from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
names=['building','front','bay','portal','rear','roof']
canvas=Image.new('RGB',(1500,1040),'#eeeeec');draw=ImageDraw.Draw(canvas)
for i,name in enumerate(names):
    im=Image.open(ROOT/'renders'/f'{name}.png').convert('RGB');im.thumbnail((500,490))
    x=(i%3)*500;y=(i//3)*520
    canvas.paste(im,(x+(500-im.width)//2,y+25));draw.text((x+12,y+6),name,fill='black')
canvas.save(ROOT/'renders/contact-sheet.png')
