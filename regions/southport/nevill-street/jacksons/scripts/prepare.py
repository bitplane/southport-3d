"""Draw the visible, limited shop name and description from the 2026 frontage."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parents[1]/'textures';P.mkdir(exist_ok=True)
im=Image.new('RGB',(1024,160),'#eeeae1');d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf';font=ImageFont.truetype(f,79);d.text((20,8),'Jacksons',font=font,fill='#171717');d.text((365,26),'Traditional Fish And Chips',font=ImageFont.truetype(f,52),fill='#171717');im.save(P/'fascia.png')
