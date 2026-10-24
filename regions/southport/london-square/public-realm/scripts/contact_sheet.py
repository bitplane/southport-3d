from pathlib import Path
assert list((Path(__file__).resolve().parents[1]/'renders').glob('*.png')), 'No review renders produced'
