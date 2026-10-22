#!/usr/bin/env python3
"""Build a compact local comparison image from successful LOD outputs."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw

root = Path(sys.argv[1])
suffix = '-oblique' if '--oblique' in sys.argv[2:] else ''
manifest = json.loads((root / 'manifest.json').read_text())
width, height = 384, 424
columns = 1 + 2 * len(manifest['levels'])
sheet = Image.new('RGB', (width * columns, height * len(manifest['targets'])), '#262626')
draw = ImageDraw.Draw(sheet)
for row, target in enumerate(manifest['targets']):
    tiles = [(root / target['id'] / ('master' + suffix + '.png'), f"{target['id']} master: {target['source_triangles']:,} tris")]
    for level in target['lods']:
        if level.get('strategy') == 'omit':
            tiles += [(None, level['id'] + ' OMITTED'), (None, 'No geometry or textures')]
            continue
        folder = root / target['id'] / level['id']
        tiles += [(folder / ('without-normal' + suffix + '.png'), f"{level['id']} without normal: {level['triangles']:,} tris"),
                  (folder / ('baked' + suffix + '.png'), f"{level['id']} baked: {level['texture_size']} px")]
    for col, (path, label) in enumerate(tiles):
        if path is not None:
            with Image.open(path) as image:
                image.thumbnail((width, width))
                sheet.paste(image, (col * width, row * height + 32))
        draw.text((col * width + 8, row * height + 10), label, fill='white')
sheet.save(root / ('comparison' + suffix + '.png'))
print(root / ('comparison' + suffix + '.png'))
