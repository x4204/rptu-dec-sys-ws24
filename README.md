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

See `kubo.diff` and `kad.diff`


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

**NOTE:** `milestone5/graph-random.toml` was generated by ogma using this
config:
```
ogma.generate.barabasiAlbert({ nodes: 11, m0: 3, m: 2 })
```
https://doc.linkurious.com/ogma/latest/examples/generator-barabasi-albert.html


## Milestone 6: use docker to run your customized IPFS daemon

Basically same as Milestone 5 but with docker.

**NOTE:** "[...] able to run multiple IPFS peers simultaneously [...] try to
start multiple IPFS daemons locally". What is the difference between a peer and
a daemon in this context?


## Milestone 7: write a IPFS network simulator

Basically the same as Milestone 7, but automated, given a topology config.


## Milestone 8: profile different topologies and the original IPFS daemon

NOTE: current workarounds made in the code to force kubo respect a specific
topology does not seem to work fully. Given the following peer topology:
```
00 <--> 01
01 <--> 02
```
(notice that `00` and `02` are not peered), if `00` uploads a file, then it's
not possible to fetch the same file from `02` (unless `01` fetches it first).
What's the problem? Is that intended behaviour?

> ![NOTE]
> According to the TA, the above is expected behaviour and perfectly fine,
> because ipfs has some kind of "lazy download".

- [ ] use for simulation: https://aioipfs.readthedocs.io/en/latest/
- [ ] warmup?
