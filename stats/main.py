# docker compose stats --format=json | python3.12 -m stats.main > stats.ndjson

import json
import fileinput

from datetime import datetime


def timestamp():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')


def main():
    for line in fileinput.input(mode='rb'):
        line = line.replace(b'\x1b[H', b'')
        line = line.replace(b'\x1b[J', b'')
        line = line.replace(b'\x1b[K', b'')

        if line == b'\n':
            continue

        stats = json.loads(line.decode())
        stats['timestamp'] = timestamp()
        stats.pop('Container')
        stats.pop('ID')
        stats.pop('PIDs')
        stats['Name'] = stats['Name'][18:-2]
        print(json.dumps(stats))


if __name__ == '__main__':
    main()
