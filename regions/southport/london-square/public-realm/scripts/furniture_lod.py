import os,sys
from pathlib import Path
ROOT=Path(os.environ.get('SOUTHPORT_REPO_ROOT',Path(__file__).resolve().parents[5]))
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.street import furniture

def build_lod(name,settings,asset_dir):
    return furniture(settings['kind'],settings['level'],name).finish([])
