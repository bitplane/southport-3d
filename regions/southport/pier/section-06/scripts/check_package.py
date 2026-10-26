from pathlib import Path
import sys,argparse
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args()
REPO=a.recipe.resolve().parents[4]
sys.path.insert(0,str(REPO/'regions/southport/pier/common'))
import importlib.util
spec=importlib.util.spec_from_file_location("pier_package_checks",REPO/"regions/southport/pier/common/check_package.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.run(a.package,a.recipe,REPO)
