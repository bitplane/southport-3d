"""Compatibility import for the memorial's existing construction modules."""
import os
import sys
from pathlib import Path
repo = Path(os.environ['SOUTHPORT_REPO_ROOT']) if 'SOUTHPORT_REPO_ROOT' in os.environ else Path(__file__).resolve().parents[5]
sys.path.insert(0, str(repo / 'lib'))
from southport3d.geometry import *
