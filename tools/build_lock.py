"""Non-blocking POSIX locks for generated asset directories."""
from contextlib import contextmanager
import fcntl
import os
import re


@contextmanager
def asset_lock(root, asset):
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', asset):
        raise ValueError(f'Invalid lock ID: {asset!r}')
    directory = root / 'build' / '.locks'
    directory.mkdir(parents=True, exist_ok=True)
    # Keep the inode: unlinking a lock file can let two writers own different locks.
    with (directory / f'{asset}.lock').open('a+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError(f'{asset}: another build/publication is writing; retry when it finishes') from error
        try:
            handle.seek(0)
            handle.truncate()
            handle.write(f'pid={os.getpid()}\n')
            handle.flush()
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
