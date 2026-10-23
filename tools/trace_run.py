"""Execute a recipe and record Python-visible input dependencies (also in Blender)."""
import atexit
import json
import os
from pathlib import Path
import runpy
import sys


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    script, depfile, *extra = args
    opened = set()

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes)):
            mode = args[1]
            # Ignore writes and file descriptors. C-side Blender reads are covered
            # by conservative explicit inputs and master integrity checks.
            if mode is None or not any(flag in str(mode) for flag in 'wax+'):
                opened.add(os.fsdecode(args[0]))

    def save():
        paths = opened | {getattr(m, '__file__', '') for m in tuple(sys.modules.values())}
        result = []
        for name in paths:
            if not name:
                continue
            path = Path(name).resolve()
            if path.suffix == '.pyc':
                try:
                    from importlib.util import source_from_cache
                    path = Path(source_from_cache(str(path)))
                except ValueError:
                    pass
            if path.is_file():
                result.append(str(path))
        Path(depfile).write_text(json.dumps(sorted(set(result)), indent=2) + '\n')

    sys.addaudithook(audit)
    atexit.register(save)
    sys.path.insert(0, str(Path(script).parent))
    # Existing Blender recipes parse options following '--'.
    sys.argv = [script, *(['--'] if os.environ.get('SOUTHPORT_TRACE_BLENDER') == '1' and extra else []), *extra]
    runpy.run_path(script, run_name='__main__')
    save()


if __name__ == '__main__':
    main()
