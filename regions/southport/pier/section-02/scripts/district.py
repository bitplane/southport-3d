from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'regions/southport/pier/common'),str(REPO/'lib'),str(REPO/'tools')]
import importlib.util
spec=importlib.util.spec_from_file_location('pier_district',REPO/'regions/southport/pier/common/district.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
surfaces=module.surfaces
