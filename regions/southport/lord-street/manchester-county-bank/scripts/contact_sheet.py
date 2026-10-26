"""Compact review of whichever views the render stage produced."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1];paths=[p for p in (root/'renders').glob('*.png') if p.stem!='contact-sheet']
canvas=Image.new('RGB',(1200,450*((len(paths)+2)//3)),'white')
for i,p in enumerate(sorted(paths)):
 im=ImageOps.contain(Image.open(p).convert('RGB'),(400,420));x=i%3*400;y=i//3*450
 canvas.paste(im,(x+(400-im.width)//2,y));ImageDraw.Draw(canvas).text((x+10,y+425),p.stem,fill='black')
canvas.save(root/'renders/contact-sheet.png')
