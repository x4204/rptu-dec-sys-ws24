# Decentralized Systems

## Prerequisites

- `git`
- `go` version 1.23
- `make`
- `python` version >= 3.11


## Setup

```
git submodule update --init --recursive
```


## Milestone 1: compile kubo from the source

To build:
```
$ ./build.sh
```

To use `ipfs`:
```
$ ./ipfs --help
```


## Milestone 2: upload a file using IPFS daemon

Docs: https://docs.ipfs.tech/how-to/command-line-quick-start

- create a symlink so that the config points to `.ipfs` in the current repo
```
$ ln -s $PWD/.ipfs ~/.ipfs
```

```
$ ./ipfs init
```

```
$ ./ipfs daemon
```

```
$ ./ipfs add files/quickstart.pdf
added Qmedg8bBBkraZg8KBj2our9fSJx4fnruniFZ9ejm1AGiAb quickstart.pdf
```

```
$ ./ipfs cat /ipfs/Qmedg8bBBkraZg8KBj2our9fSJx4fnruniFZ9ejm1AGiAb > /tmp/quickstart.pdf
```

```
$ diff -s files/quickstart.pdf /tmp/quickstart.pdf
Files files/quickstart.pdf and /tmp/quickstart.pdf are identical
```


## Milestone 3: delete all bootstrap nodes

- remove bootstrap nodes from the config file:
```
$ ipfs bootstrap rm --all
```


## Milestone 4: make IPFS nodes never connect to other nodes automatically

- see: `milestone4.patch`
```
rows 093-143: get all routers at the start of the node (bootstrap peers)

rows 167-173: get all routers that can do contentRouting

rows 198-204: get all routers obtained from different methods (commented out
for now, because otherwise ./ipfs init panics)

rows 263-317: try to connect to nodes after unexpected errors
```

- apply patch:
```
patch -p0 kubo/core/node/libp2p/routing.go < milestone4.patch
```

- rebuild
```
./build.sh
```

- start the node:
```
$ ./ipfs daemon
```

- check if there are peers:
```
$ ./ipfs swarm peers
```

If there are no peers then the result of the command must be empty

NOTE: cannot access `/webui` with these changes though


## Milestone 5: create a private IPFS network with a specific topology

References:
- https://github.com/ahester57/ipfs-private-swarm#2-generate-swarmkey
- https://freedium.cfd/https://medium.com/@s_van_laar/deploy-a-private-ipfs-network-on-ubuntu-in-5-steps-5aad95f7261b
- https://raw.githubusercontent.com/ipfs-cluster/ipfs-cluster/master/docker-compose.yml

Swarm key: `.docker/kubo/swarm.key`

To build the Docker image:
```
$ ./build-image.sh
```

See `milestone5/*.toml` for a list of available topologies

To deploy a specific topology:
```
$ python -m milestone5.main deploy milestone5/<topology>.toml
```

To visualise a specific topology:
```
$ python -m milestone5.main graphviz milestone5/<topology>.toml
```
then copy+paste the output here:
https://dreampuf.github.io/GraphvizOnline/#digraph%20G%20{}

- [ ] add config for grid
- [ ] add config for complete graph
- [ ] add config for random graph
