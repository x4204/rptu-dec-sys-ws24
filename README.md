# Decentralized Systems

## Setup

```
git submodule update --init --recursive
```


## Milestone 1: compile kubo from the source

Build dependencies:
- `go` version 1.23
- `make`

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

Open `$HOME/.ipfs/config`, find `"Bootstrap"` record and delete everything from
list, so it should look like this:
```
"Bootstrap": [],
```

## Milestone 4: make IPFS nodes never connect to other nodes automatically

- see: `milestone4.patch`
```
rows 093-143: get all routers at the start of the node
rows 167-173: get all routers that can do contentRouting
rows 198-204: get all routers obtained from different methods
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
