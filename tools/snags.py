#!/usr/bin/env python3
"""Inspect, claim and resolve local viewer snags without adding them to Git."""
import argparse
import json
from snag_store import DEFAULT_QUEUE, SnagStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', default=str(DEFAULT_QUEUE))
    sub = parser.add_subparsers(dest='command', required=True)
    listing = sub.add_parser('list')
    listing.add_argument('--all', action='store_true', help='Include completed snags')
    for name in ['show', 'claim', 'resolve', 'reopen']:
        command = sub.add_parser(name)
        command.add_argument('id')
        if name != 'show':command.add_argument('--note', default='')
    args = parser.parse_args()
    store = SnagStore(args.queue)
    try:
        if args.command == 'list':
            for record in reversed(store.list()):
                if args.all or record['status'] != 'done':
                    print(record['id'], record['status'], record['comment'].splitlines()[0][:100])
        elif args.command == 'show':
            record = store.read(args.id)
            record['directory'] = str(store.directory(args.id))
            print(json.dumps(record, indent=2))
        else:
            status = {'claim': 'in_progress', 'resolve': 'done', 'reopen': 'open'}[args.command]
            record = store.update(args.id, status, args.note, claim=args.command == 'claim')
            print(record['id'], record['status'])
    except (ValueError, FileNotFoundError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':main()
