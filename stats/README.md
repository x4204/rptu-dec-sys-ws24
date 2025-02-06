# `stats`

## Setup

- create virtualenv
```
virtualenv stats/.venv --python $(which python3.12)
```

- activate virtualenv
```
. stats/.venv/bin/activate
```

- install dependencies
```
pip install -r stats/requirements.txt
```

## Running

```
bash gather.sh
```

```
python -m stats.plot
```
