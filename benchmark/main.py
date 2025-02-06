import aioipfs
import asyncio
import json
import numpy
import random
import subprocess
import sys
import time

files = []
host = '127.0.0.1'
port = 5000
times = []
nn = 0
timeout = 5
nodes = {}
rng = open('/dev/urandom', 'rb')


def read_topology():
    with open('topology-state.json') as file:
        return json.loads(file.read())


def port_to_name(port):
    return f'ipfs-{port % 100:02d}'


def gen_random_file_size():
    while True:
        n = numpy.random.zipf(1.5)
        if n >= 1 and n <= 500:
            return n


def gen_random_content():
    size = gen_random_file_size() * 1024 * 1024
    return rng.read(size)


async def run():
    last_download_ok = True
    curr_port = port + random.randint(0, len(nodes) - 1)

    for i in range(100):
        if random.randint(0, 100) <= 15 and last_download_ok:
            async with aioipfs.AsyncIPFS(host=host, port=curr_port) as client:
                entry = await client.core.add_bytes(gen_random_content())
                files.append(entry['Name'])
        else:
            i = random.randint(0,len(files)-1)
            try:
                async with asyncio.timeout(timeout):
                    async with aioipfs.AsyncIPFS(host=host, port=curr_port) as client:
                        st = time.time()
                        await client.core.cat(files[i])
                        et = time.time()
                        times.append(et-st)
                        print(len(times), et-st)
                last_download_ok = True
            except TimeoutError:
                global nn
                nn += 1
                last_download_ok = False
                print("NN:", nn)


async def simulation():
    for i in range(4):
        async with aioipfs.AsyncIPFS(host=host, port=port+((i*3) % len(nodes))) as client:
            entry = await client.core.add_bytes(gen_random_content())
            files.append(entry['Name'])

        neighbors = nodes[port_to_name(port+((i*3) % len(nodes)))]['neighbors']
        neighbor = neighbors[random.randint(0, len(neighbors)-1)]
        async with aioipfs.AsyncIPFS(host=host, port=port+int(neighbor[-2:])) as client:
            await client.core.cat(entry['Name'])

        neighbors = nodes[neighbor]['neighbors']
        neighbor = neighbors[random.randint(0, len(neighbors)-1)]
        async with aioipfs.AsyncIPFS(host=host, port=port+int(neighbor[-2:])) as client:
            await client.core.cat(entry['Name'])

    await asyncio.gather(*[run() for i in range(100)])


async def main():
    if len(sys.argv) != 2:
        print('usage: python -m benchmark.main <timeout>')
        raise SystemExit(1)

    global timeout
    _, timeout = sys.argv
    timeout = int(timeout)

    global nodes
    nodes = read_topology()

    await simulation()

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
