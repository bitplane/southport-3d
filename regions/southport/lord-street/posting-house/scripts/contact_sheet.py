from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]/'renders'
sheet=Image.new('RGB',(1400,1200),'#d9dfdc')
names=[name for name in ['arcade-bases','building','front','rear','roof'] if (root/f'{name}.png').exists()][:4]
for i,name in enumerate(names):
    im=ImageOps.contain(Image.open(root/f'{name}.png').convert('RGB'),(700,565))
    x=(i%2)*700;y=(i//2)*600
    sheet.paste(im,(x,y+25));ImageDraw.Draw(sheet).text((x+12,y+8),name,fill='black')
sheet.save(root/'contact-sheet.png')
