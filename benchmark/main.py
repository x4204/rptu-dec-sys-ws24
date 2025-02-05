import aioipfs
import asyncio
import json


def read_topology():
    with open('topology-state.json') as file:
        return json.loads(file.read())


async def main(top):
    host = top['ipfs-00']['ip']

    # run: docker compose exec ipfs-00 ipfs add /data/ipfs/config
    # then copy the id here
    path = '/ipfs/QmWR15oyTn7wZ5rmtE5V1SuMvDskULBWGuyxLPzZtiMjt3'

    async with aioipfs.AsyncIPFS(host=host) as client:
        res = await client.cat(path)
        import pdb; pdb.set_trace()


if __name__ == '__main__':
    asyncio.run(main(read_topology()))
