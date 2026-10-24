from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
sheet=Image.new('RGB',(1500,720),'white')
for i,name in enumerate(('front','corner','north','roof','rear')):
    im=ImageOps.contain(Image.open(root/'renders'/f'{name}.png').convert('RGB'),(500,330))
    x=(i%3)*500;y=(i//3)*360;sheet.paste(im,(x,y))
    ImageDraw.Draw(sheet).text((x+10,y+335),name,fill='black')
sheet.save(root/'renders/contact-sheet.png')
