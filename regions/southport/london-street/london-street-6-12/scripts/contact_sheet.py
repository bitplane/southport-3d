"""Local render index for inspection over SSH."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

root = Path(__file__).resolve().parents[1] / 'renders'
files = sorted(p for p in root.glob('*.png') if p.name != 'contact-sheet.png')
sheet = Image.new('RGB', (1200, 440*((len(files)+1)//2)), '#d9dfdc')
for i, path in enumerate(files):
    image = ImageOps.contain(Image.open(path).convert('RGB'), (600, 410))
    x, y = (i % 2)*600, (i // 2)*440
    sheet.paste(image, (x, y+25))
    ImageDraw.Draw(sheet).text((x+12, y+6), path.stem, fill='black')
sheet.save(root / 'contact-sheet.png')
