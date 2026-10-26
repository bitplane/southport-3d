from pathlib import Path
root=Path(__file__).resolve().parents[1]
for d in ['models','renders','textures']:(root/d).mkdir(exist_ok=True)
