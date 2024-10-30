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
