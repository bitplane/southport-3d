from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];canvas=Image.new('RGB',(1440,460),'white')
for i,name in enumerate(['corner','rear','roof']):
 im=ImageOps.contain(Image.open(R/'renders'/f'{name}.png').convert('RGB'),(480,420));canvas.paste(im,(i*480+(480-im.width)//2,0));ImageDraw.Draw(canvas).text((i*480+12,425),name,fill='black')
canvas.save(R/'renders/contact-sheet.png')
