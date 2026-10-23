from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
canvas=Image.new('RGB',(1440,560),'white')
for i,name in enumerate(['street','overview']):
 im=Image.open(root/'renders'/f'{name}.png').convert('RGB');im=ImageOps.contain(im,(720,520));canvas.paste(im,(i*720+(720-im.width)//2,0));ImageDraw.Draw(canvas).text((i*720+12,532),name,fill='black')
canvas.save(root/'renders/contact-sheet.png')
