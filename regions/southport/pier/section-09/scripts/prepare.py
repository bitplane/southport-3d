from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'regions/southport/pier/common'),str(REPO/'lib'),str(REPO/'tools')]
from prepare import run
run(ROOT)
