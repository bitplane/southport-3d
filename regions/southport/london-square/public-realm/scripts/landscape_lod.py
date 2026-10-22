import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(os.environ.get('SOUTHPORT_REPO_ROOT',Path(__file__).resolve().parents[5]))/'lib'))
from southport3d.landscape import tree

def build_lod(name,settings,asset_dir):
    return tree(settings['level'],name).finish([])
