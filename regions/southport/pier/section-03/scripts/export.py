from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'regions/southport/pier/common'),str(REPO/'lib'),str(REPO/'tools')]
import bpy
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pier.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/pier.glb'),export_format='GLB')
