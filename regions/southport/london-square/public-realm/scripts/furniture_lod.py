import os,sys
from pathlib import Path
ROOT=Path(os.environ.get('SOUTHPORT_REPO_ROOT',Path(__file__).resolve().parents[5]))
sys.path.insert(0,str(ROOT/'lib'))
from southport3d.street import furniture as generic_furniture
from signals import signal
from lord_street_lamps import lamp

def furniture(kind,level="detail",name=None):
    if kind=="lord-street-lamp":return lamp(level,name)
    return signal(kind,level,name) if kind in ("signal","pedestrian") else generic_furniture(kind,level,name)

def build_lod(name,settings,asset_dir):
    return furniture(settings['kind'],settings['level'],name).finish([])
