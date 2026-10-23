#!/usr/bin/env python3
"""Serve the generated viewer and its local snag queue on loopback by default."""
import argparse
import json
import hashlib
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from snag_store import DEFAULT_QUEUE, MAX_BODY, SnagStore

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, queue=DEFAULT_QUEUE, **kwargs):
        self.snags = SnagStore(queue)
        super().__init__(*args, **kwargs)

    def json_response(self, value, status=200):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if not path.startswith('/api/'):
            return super().do_GET()
        if path == '/api/events':
            return self.events()
        try:
            parts = path.strip('/').split('/')
            if parts == ['api', 'snags']:
                return self.json_response({'snags': self.snags.list()})
            if parts[:2] == ['api', 'snags'] and len(parts) == 3:
                return self.json_response(self.snags.read(parts[2]))
            if parts[:2] == ['api', 'snags'] and len(parts) == 5 and parts[3] == 'files':
                image = self.snags.image(parts[2], parts[4])
                body = image.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', {'.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp'}[image.suffix])
                self.send_header('Content-Length', str(len(body)))
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                self.wfile.write(body)
                return
        except (ValueError, FileNotFoundError):
            pass
        self.json_response({'error': 'Snag not found'}, 404)

    def events(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()
        previous = None
        try:
            while True:
                try:
                    body = (Path(self.directory) / 'catalog.json').read_bytes()
                    revision = hashlib.sha256(body).hexdigest()
                    if revision != previous:
                        self.wfile.write(('event: catalog\ndata: ' + json.dumps({'revision': revision}) + '\n\n').encode())
                        previous = revision
                    else:
                        self.wfile.write(b': keepalive\n\n')
                except FileNotFoundError:
                    self.wfile.write(b': waiting for publication\n\n')
                self.wfile.flush()
                time.sleep(2)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def do_POST(self):
        if urlsplit(self.path).path != '/api/snags':
            return self.json_response({'error': 'Unknown endpoint'}, 404)
        # Do not let an unrelated website write into the local queue.
        origin = self.headers.get('Origin')
        if origin and (urlsplit(origin).scheme not in {'http','https'} or
                       urlsplit(origin).netloc != self.headers.get('Host')):
            return self.json_response({'error': 'Use the viewer on this server'}, 403)
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            return self.json_response({'error': 'Expected JSON'}, 415)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                return self.json_response({'error': 'Snag must be smaller than 24 MB'}, 413)
            payload = json.loads(self.rfile.read(length))
            record = self.snags.create(payload)
        except (ValueError, UnicodeError) as exc:
            return self.json_response({'error': str(exc)}, 400)
        except OSError:
            return self.json_response({'error': 'Could not save the snag queue; check server permissions and disk space'}, 500)
        self.json_response(record, 201)

    def list_directory(self, path):
        self.send_error(404, 'Run python3 tools/project.py publish to prepare the viewer')
        return None

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--snag-dir', type=Path, default=DEFAULT_QUEUE,
                        help='Local queue directory, outside the repository by default')
    args = parser.parse_args()
    directory = ROOT / 'dist'
    directory.mkdir(exist_ok=True)
    handler = partial(Handler, directory=str(directory), queue=args.snag_dir)
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f'Southport viewer: http://{args.bind}:{args.port}', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
