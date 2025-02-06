import sys
import aioipfs
import asyncio
import json
import subprocess
import time
from random import randbytes, randint

files = []
host = '127.0.0.1'
port = 5000
times = []
nn = 0
timeout = 5
nodes = {}

def run_process(*args, **kwargs):
    print(f'RUN: {args} {kwargs}')
    result = subprocess.run(*args, **kwargs)
    if result.returncode != 0:
        print(f'ERROR: exit code: {result.returncode}')
        raise SystemExit(1)
    return result

def read_topology():
    with open('topology-state.json') as file:
        return json.loads(file.read())

def port_to_name(port):
    return 'ipfs-0'+str(port % 10) if port < 5010 else 'ipfs-'+str(port % 100)

async def first_scenario(host, port, size):
    name = None
    async with aioipfs.AsyncIPFS(host=host, port=port) as client:
            entry = await client.core.add_bytes(randbytes(size*1024*1024))
            name = entry['Name']
    for i in range(10):
        async with aioipfs.AsyncIPFS(host=host, port=port+i) as client:
            await client.core.cat(name)

async def second_scenario(host, port, size):
    name = None
    async with aioipfs.AsyncIPFS(host=host, port=port) as client:
            entry = await client.core.add_bytes(randbytes(size*1024*1024))
            name = entry['Name']
    for i in range(9):
        async with aioipfs.AsyncIPFS(host=host, port=port+i+1) as client:
            bytes = await client.core.cat(name)
            entry = await client.core.add_bytes(randbytes(size*1024*1024))
            name = entry['Name']

async def run(size):
    lastDownload = True
    curr_port=port+randint(0,9)
    for i in range(100):
        if randint(0, 100) <= 15 and lastDownload:
            async with aioipfs.AsyncIPFS(host=host, port=curr_port) as client:
                entry = await client.core.add_bytes(randbytes(size*1024*1024))
                files.append(entry['Name'])
        else:
            i = randint(0,len(files)-1)
            try:
                async with asyncio.timeout(timeout):
                    async with aioipfs.AsyncIPFS(host=host, port=curr_port) as client:
                        st = time.time()
                        await client.core.cat(files[i])
                        et = time.time()
                        times.append(et-st)
                        print(len(times), et-st)
                lastDownload = True
            except TimeoutError:
                global nn
                nn += 1
                lastDownload = False
                print("NN:", nn)

async def simulation(size):
    for i in range(4):
        async with aioipfs.AsyncIPFS(host=host, port=port+i*3) as client:
            entry = await client.core.add_bytes(randbytes(size*1024*1024))
            files.append(entry['Name'])
        neighbors = nodes[port_to_name(port+i*3)]['neighbors']
        neighbor = neighbors[randint(0, len(neighbors)-1)]
        async with aioipfs.AsyncIPFS(host=host, port=port+int(neighbor.split('-')[1])) as client:
            await client.core.cat(entry['Name'])
        neighbors = nodes[neighbor]['neighbors']
        neighbor = neighbors[randint(0, len(neighbors)-1)]
        async with aioipfs.AsyncIPFS(host=host, port=port+int(neighbor.split('-')[1])) as client:
            await client.core.cat(entry['Name'])
    
    await asyncio.gather(*[
        run(size) for i in range(100)
    ])

async def lol(host, port, size):
    namees = []
    for i in range(9):
        async with aioipfs.AsyncIPFS(host=host, port=port+i) as client:
            entry = await client.core.add_bytes(randbytes(size*1024*1024))
            namees.append(entry['Name'])
    for i in range(9):
        async with aioipfs.AsyncIPFS(host=host, port=port+i+1) as client:
            await client.core.cat(namees[i])

async def main(top):
    if len(sys.argv) != 3:
        print('usage: python -m benchmark.main <file_size> <timeout>')
        raise SystemExit(1)
    global timeout
    _, size, timeout = sys.argv
    size = int(size)
    timeout = int(timeout)
    global nodes
    nodes = read_topology()

    # await first_scenario(host, port, size)
    # await second_scenario(host, port, size)
    # await lol(host, port, size)
    await simulation(size)

if __name__ == '__main__':
    asyncio.run(main(read_topology()), debug=True)
