"""Local, untracked snag queue. No reference images enter model publication."""
import base64
import binascii
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import math
from pathlib import Path
import re
import shutil
import uuid

DEFAULT_QUEUE = Path(__file__).resolve().parents[2] / 'snags'
MAX_BODY = 24 * 1024 * 1024
MAX_IMAGE = 5 * 1024 * 1024
ID = re.compile(r'^[0-9a-f]{32}$')
STATUSES = {'open', 'in_progress', 'done'}


def now():
    return datetime.now(timezone.utc).isoformat()


def vector(value, length, name):
    if not isinstance(value, list) or len(value) != length or any(
        isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
        for v in value
    ):
        raise ValueError('Invalid ' + name)
    return value


def image_bytes(value):
    if not isinstance(value, str):
        raise ValueError('Missing image data')
    match = re.fullmatch(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)', value)
    if not match or len(value) > MAX_IMAGE * 4 // 3 + 100:
        raise ValueError('Use PNG, JPEG or WebP images up to 5 MB each')
    try:
        data = base64.b64decode(match[2], validate=True)
    except binascii.Error as exc:
        raise ValueError('Invalid image encoding') from exc
    kind = match[1]
    valid = (kind == 'png' and data.startswith(b'\x89PNG\r\n\x1a\n')
             or kind == 'jpeg' and data.startswith(b'\xff\xd8\xff')
             or kind == 'webp' and data.startswith(b'RIFF') and data[8:12] == b'WEBP')
    if not valid or len(data) > MAX_IMAGE:
        raise ValueError('Invalid or oversized image')
    return data, 'jpg' if kind == 'jpeg' else kind


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError('Expected a snag object')
    comment = payload.get('comment')
    if not isinstance(comment, str) or not comment.strip() or len(comment) > 10000:
        raise ValueError('Write a comment (up to 10,000 characters)')
    view = payload.get('view')
    if not isinstance(view, dict) or len(json.dumps(view)) > 250000:
        raise ValueError('Missing or oversized camera context')
    camera = view.get('camera', {})
    if not isinstance(camera, dict):
        raise ValueError('Invalid camera context')
    vector(camera.get('position'), 3, 'camera position')
    quaternion = vector(camera.get('quaternion'), 4, 'camera rotation')
    if not .99 < sum(v*v for v in quaternion) < 1.01:
        raise ValueError('Invalid camera rotation')
    vector(camera.get('target'), 3, 'camera target')
    for key, low, high in [('fov', 1, 179), ('aspect', .01, 100)]:
        v = camera.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not low <= v <= high:
            raise ValueError('Invalid camera ' + key)
    if view.get('quality') not in {'auto', 'detail', 'walk', 'district'}:
        raise ValueError('Invalid viewing level')
    rect = vector(payload.get('box'), 4, 'selection box')
    x, y, width, height = rect
    if min(x, y) < 0 or min(width, height) <= 0 or x+width > 1.000001 or y+height > 1.000001:
        raise ValueError('Draw a box within the screenshot')
    screenshot = image_bytes(payload.get('screenshot'))
    photos = payload.get('photos', [])
    if not isinstance(photos, list) or len(photos) > 5:
        raise ValueError('Attach at most five photos')
    attachments = []
    for photo in photos:
        if not isinstance(photo, dict):
            raise ValueError('Invalid photo')
        data, extension = image_bytes(photo.get('data'))
        label = photo.get('name', 'Photo')
        if not isinstance(label, str) or len(label) > 255:
            raise ValueError('Invalid photo label')
        attachments.append((label, data, extension))
    return comment.strip(), view, rect, screenshot, attachments


class SnagStore:
    def __init__(self, root=DEFAULT_QUEUE):
        self.root = Path(root)

    def directory(self, snag_id):
        if not ID.fullmatch(snag_id):
            raise ValueError('Invalid snag ID')
        return self.root / snag_id

    def read(self, snag_id):
        return json.loads((self.directory(snag_id) / 'snag.json').read_text())

    def list(self):
        if not self.root.exists():
            return []
        return sorted([self.read(p.name) for p in self.root.iterdir()
                       if p.is_dir() and ID.fullmatch(p.name) and (p/'snag.json').is_file()],
                      key=lambda r: r['created_at'], reverse=True)

    def create(self, payload):
        comment, view, box, screenshot, photos = validate(payload)
        self.root.mkdir(parents=True, exist_ok=True)
        snag_id = uuid.uuid4().hex
        temporary = self.root / ('.pending-' + snag_id)
        temporary.mkdir()
        try:
            image, extension = screenshot
            filename = 'view.' + extension
            (temporary / filename).write_bytes(image)
            attachments = []
            for i, (name, data, extension) in enumerate(photos, 1):
                path = f'photo-{i}.{extension}'
                (temporary / path).write_bytes(data)
                attachments.append({'name': name, 'file': path})
            record = dict(schema_version=1, id=snag_id, status='open', created_at=now(),
                          comment=comment, box=box, view=view, screenshot=filename,
                          photos=attachments, history=[])
            (temporary / 'snag.json').write_text(json.dumps(record, indent=2) + '\n')
            temporary.rename(self.directory(snag_id))
            return record
        except Exception:
            shutil.rmtree(temporary)
            raise

    def image(self, snag_id, filename):
        record = self.read(snag_id)
        allowed = {record['screenshot'], *(p['file'] for p in record['photos'])}
        if filename not in allowed:
            raise FileNotFoundError(filename)
        return self.directory(snag_id) / filename

    @contextmanager
    def locked(self, snag_id):
        with (self.directory(snag_id) / '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def update(self, snag_id, status, note='', claim=False):
        if status not in STATUSES:
            raise ValueError('Invalid snag status')
        with self.locked(snag_id):
            record = self.read(snag_id)
            if claim and record['status'] != 'open':
                raise ValueError('Snag is already claimed or completed')
            record['history'].append(dict(at=now(), previous=record['status'], status=status, note=note))
            record['status'] = status
            path = self.directory(snag_id) / 'snag.json'
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(record, indent=2) + '\n')
            temporary.replace(path)
            return record
