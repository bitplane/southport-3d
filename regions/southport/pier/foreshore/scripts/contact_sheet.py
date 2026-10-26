from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[1]/'renders';Image.open(r/'overview.png').convert('RGB').save(r/'contact-sheet.jpg')
