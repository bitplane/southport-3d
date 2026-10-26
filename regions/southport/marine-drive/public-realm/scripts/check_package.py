"""Validate the measured ground and separate Marine Way deck in actual LoD files."""
import runpy
from pathlib import Path
import sys
recipe=Path(sys.argv[sys.argv.index('--recipe')+1]).resolve()
repo=recipe.parents[4]
sys.path.insert(0,str(repo/'tools'))
runpy.run_path(str(repo/'tools/check_terrain_package.py'),run_name='__main__')
