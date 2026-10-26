from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ['models','renders','textures']:(ROOT/name).mkdir(exist_ok=True)
