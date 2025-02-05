# `benchmark`

## Setup

- create virtualenv
```
virtualenv benchmark/.venv --python $(which python3.12)
```

- activate virtualenv
```
. benchmark/.venv/bin/activate
```

- install dependencies
```
pip install -r benchmark/requirements.txt
```

## Running

```
python -m benchmark.main
```
