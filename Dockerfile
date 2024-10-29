FROM golang:1.23.2-bookworm AS build

WORKDIR /tmp/build

RUN wget https://github.com/ipfs/kubo/releases/download/v0.31.0/kubo-source.tar.gz
RUN tar -xzf kubo-source.tar.gz
RUN make build

# ------------------------------------------------------------------------------
FROM golang:1.23.2-bookworm

ENV IPFS_PATH="/ipfs"

WORKDIR /ipfs

COPY --from=build /tmp/build/cmd/ipfs/ipfs /go/bin

RUN groupadd --system --gid 1000 kubo
RUN useradd kubo --uid 1000 --gid 1000 --create-home --shell /bin/bash

USER 1000:1000
