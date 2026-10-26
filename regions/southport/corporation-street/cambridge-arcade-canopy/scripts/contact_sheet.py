from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]/'renders';Image.open(R/'arcade.png').convert('RGB').save(R/'contact-sheet.jpg')
