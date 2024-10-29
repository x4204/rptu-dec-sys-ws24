# Decentralized Systems


## Milestone 1: compile kubo from the source

Docker is being used for the build process. To build `ipfs`:
```
$ ./build.sh
```
This shell script will:
- build `ipfs`
- copy the binary into the current directory
- symlink `~/.ipfs` to `./.ipfs`

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
