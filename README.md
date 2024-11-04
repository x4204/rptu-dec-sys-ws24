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

- https://docs.ipfs.tech/how-to/command-line-quick-start

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

Go to "config" file in its default directory( probably "/home/$user_name/.ipfs")

Find "Bootstrap" record and delete everything from list, so it should look like 
```
$"Bootstrap": [],
```

## Milestone 4: make IPFS nodes never connect to other nodes automatically

Go to "routing.go" in Kubo directory. From main directory of Kubo:
```
cd core/node/libp2p
```

Open "routing.go" and delete rows:
263-317 (Try to connect to nodes after unexpected errors)
198-204 (Get all routers obtained from different methods)
167-173 (Get all routers that can do contentRouting)
93-143 (Get all routers at the start of the node)

