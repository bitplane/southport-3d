from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]/'renders'
paths=sorted(p for p in root.glob('*.png') if p.name!='contact-sheet.png')
sheet=Image.new('RGB',(960,((len(paths)+1)//2)*360),'#ddd')
for i,path in enumerate(paths):
    picture=ImageOps.contain(Image.open(path).convert('RGB'),(480,330))
    x,y=i%2*480,i//2*360
    sheet.paste(picture,(x,y))
    ImageDraw.Draw(sheet).text((x+8,y+334),path.stem,fill='black')
sheet.save(root/'contact-sheet.png')
