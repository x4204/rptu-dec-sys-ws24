#!/bin/sh

set -e

docker build --progress=plain --tag kubo:local .
docker run --rm -it -v ./:/cwd kubo:local cp /go/bin/ipfs /cwd/ipfs
ln -s $PWD/.ipfs $HOME/.ipfs 2>/dev/null || true
