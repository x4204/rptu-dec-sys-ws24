import sys

if sys.version_info < (3, 11):
    print('ERROR: your python is old; use a python version >= 3.11')
    raise SystemExit(1)

import glob
import math
import pprint
import re
import shutil
import subprocess
import time
import tomllib

from pathlib import Path
from threading import Thread


def run_process(*args, **kwargs):
    print(f'RUN: {args} {kwargs}')
    result = subprocess.run(*args, **kwargs)
    if result.returncode != 0:
        print(f'ERROR: exit code: {result.returncode}')
        raise SystemExit(1)
    return result


def validate_topology(topology):
    print('-' * 50)
    print('INFO: validating topology')

    if set(topology) != {'nodes', 'links'}:
        print('ERROR: invalid topology params')
        raise SystemExit(1)

    if len(set(topology['nodes'])) != len(topology['nodes']):
        print('ERROR: non-unique topology names')
        raise SystemExit(1)

    orphaned = set(topology['nodes'])
    for a, b in topology['links']:
        orphaned.discard(a)
        orphaned.discard(b)
    if len(orphaned) != 0:
        print(f'ERROR: orphaned nodes: {orphaned}')
        raise SystemExit(1)

    print('INFO: done')


def stop_and_remove_containers():
    print('-' * 50)
    print('INFO: stopping and removing containers')

    run_process([
        'docker', 'compose', 'down', '--volumes', '--remove-orphans',
    ])

    print('INFO: done')


def remove_ipfs_storage():
    print('-' * 50)
    print('INFO: removing ipfs storage')

    for path in glob.glob('.docker/kubo/ipfs-*'):
        print(f'  {path}')
        shutil.rmtree(path)

    print('INFO: done')


def create_ipfs_storage(topology):
    print('-' * 50)
    print('INFO: creating ipfs storage')

    root = Path('.docker/kubo')
    for name in topology['nodes']:
        path = root.joinpath(name)
        print(f'  {path}')
        path.mkdir()

    print('INFO: done')


def generate_docker_compose_yml(topology):
    print('-' * 50)
    print('INFO: generating docker-compose.yml')

    with open('docker-compose.yml', 'w') as file:
        file.write('services:\n')
        for index, node in enumerate(topology['nodes']):
            file.write(f'  {node}:\n')
            file.write(f"    image: 'kubo:local'\n")
            file.write(f'    environment:\n')
            file.write(f"      LIBP2P_FORCE_PNET: '1'\n")
            file.write(f"      IPFS_LOGGING: 'debug'\n")
            file.write(f'    volumes:\n')
            file.write(f"      - './.docker/kubo/{node}:/data/ipfs'\n")
            file.write(f"      - './.docker/kubo/swarm.key:/data/ipfs/swarm.key'\n")
            file.write(f"      - './.docker/kubo/container-init.d:/container-init.d'\n")
            file.write(f"      - './kubo/cmd/ipfs/ipfs:/usr/local/bin/ipfs'\n")
            if index != len(topology['nodes']) - 1:
                file.write('\n')

    print('INFO: done')


def start_containers():
    print('-' * 50)
    print('INFO: starting containers')

    run_process(['docker', 'compose', 'up'])

    print('INFO: done')


def setup_ipfs_nodes(topology):
    for _ in range(2 + math.ceil(math.sqrt(len(topology['nodes'])))):
        print('INFO: waiting...')
        time.sleep(1)

    nodes = {
        name: { 'container': None, 'ip': None, 'id': None }
        for name in topology['nodes']
    }

    print('-' * 50)
    print('INFO: collecting container names')

    result = run_process(
        ['docker', 'compose', 'ps'],
        capture_output=True,
    )
    for line in result.stdout.splitlines()[1:]:
        container = line.decode().split(' ')[0]
        name = re.match(r'^.+\-(ipfs\-\d+)\-\d+$', container)[1]
        nodes[name]['container'] = container

    rnodes = set(nodes) # running nodes
    enodes = set(topology['nodes']) # expected nodes
    if rnodes != enodes:
        print('ERROR: nodes are not running', enodes - rnodes)
        raise SystemExit(1)

    print('INFO: done')
    print('-' * 50)
    print('INFO: collecting container ips')

    for name, attrs in nodes.items():
        print(f'  {name}')
        result = run_process(
            [
                'docker', 'inspect', '-f',
                '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                attrs['container'],
            ],
            capture_output=True,
        )
        attrs['ip'] = result.stdout.decode().strip()

    print('INFO: done')
    print('-' * 50)
    print('INFO: collecting node ids')

    for name, attrs in nodes.items():
        print(f'  {name}')
        result = run_process(
            [
                'docker', 'compose', 'exec', name,
                'ipfs', 'id', '-f', '<id>',
            ],
            capture_output=True,
        )
        attrs['id'] = result.stdout.decode()

    print('INFO: done')
    pprint.pprint(nodes)
    print('-' * 50)
    print('INFO: configuring topology')

    for a, b in topology['links']:
        print(f'  {a} <-> {b}')
        name = a
        address = '/'.join([
            '/ip4', nodes[b]['ip'],
            'tcp/4001/ipfs', nodes[b]['id'],
        ])
        run_process(
            [
                'docker', 'compose', 'exec', name,
                'ipfs', 'swarm', 'connect', address,
            ],
        )

    print('INFO: done')

    print('-' * 50)
    print('INFO: READY !!!!')


def deploy_topology(topology):
    validate_topology(topology)
    stop_and_remove_containers()
    remove_ipfs_storage()
    create_ipfs_storage(topology)
    generate_docker_compose_yml(topology)

    threads = [
        Thread(target=start_containers),
        Thread(target=setup_ipfs_nodes, args=(topology,)),
    ]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        for thread in threads:
            thread.join()
        time.sleep(1)


def visualise_topology(topology):
    print('digraph G {')
    for node in topology['nodes']:
        print(f'  "{node}" [shape=square];')
    print()
    for a, b in topology['links']:
        print(f'  "{a}" -> "{b}" [dir=both];')
    print('}')


def main():
    if len(sys.argv) != 3:
        print('ERROR: <cmd> <topology> were not provided')
        print('usage: python -m milestone5.main <cmd> <topology>')
        raise SystemExit(1)

    _, cmd, topology_path = sys.argv
    with open(topology_path, 'rb') as file:
        topology = tomllib.load(file)

    if cmd == 'deploy':
        deploy_topology(topology)
    elif cmd == 'graphviz':
        visualise_topology(topology)
    else:
        print(f'ERROR: invalid <cmd>: {cmd}')


if __name__ == '__main__':
    main()
