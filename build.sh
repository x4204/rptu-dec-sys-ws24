#!/bin/bash

set -euo pipefail

branch='dec-sys'

cd kubo
if [ "$(git branch --show-current)" != "$branch" ]; then
  echo 'ERROR: kubo submodule is not on branch' $branch
  exit 1
else
  make build
fi
