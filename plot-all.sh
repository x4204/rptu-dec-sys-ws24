set -xeuo pipefail

python -m stats.plot stats/original.ndjson tex/figures/original
python -m stats.plot stats/ring.ndjson tex/figures/ring
python -m stats.plot stats/grid.ndjson tex/figures/grid
python -m stats.plot stats/graph-random.ndjson tex/figures/graph-random
python -m stats.plot stats/graph-complete.ndjson tex/figures/graph-complete
