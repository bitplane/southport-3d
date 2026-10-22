#!/usr/bin/env python3
"""Serve only the generated viewer package, on loopback by default."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
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
    args = parser.parse_args()
    directory = ROOT / 'dist'
    directory.mkdir(exist_ok=True)
    handler = partial(Handler, directory=str(directory))
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f'Southport viewer: http://{args.bind}:{args.port}', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
