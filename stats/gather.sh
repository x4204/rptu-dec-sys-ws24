set -euo pipefail

docker compose stats --format=json | python3.12 -m stats.main > stats/stats.ndjson
