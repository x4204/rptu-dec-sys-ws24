import collections
import json
import matplotlib.pyplot as plt

from datetime import datetime


COLORS = [
    'indianred',
    'orangered',
    'goldenrod',
    'olive',
    'forestgreen',
    'turquoise',
    'darkcyan',
    'deepskyblue',
    'steelblue',
    'royalblue',
    'mediumpurple',
    'fuchsia',
]


def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')


def parse_size(text):
    if text.endswith('kB'):
        return int(float(text[:-2]) * (1000 ** 1))
    if text.endswith('MiB'):
        return int(float(text[:-3]) * (1024 ** 2))
    if text.endswith('GiB'):
        return int(float(text[:-3]) * (1024 ** 3))
    if text == '0B':
        return 0
    assert False, text


def to_bytes(text):
    fst, snd = text.split(' / ')
    return parse_size(fst), parse_size(snd)


def parse_stat_line(line):
    data = json.loads(line)
    stat = { 'name': data['Name'] }

    read, write = to_bytes(data['BlockIO'])
    stat['blk_read'] = read
    stat['blk_write'] = write

    read, write = to_bytes(data['NetIO'])
    stat['net_read'] = read
    stat['net_write'] = write

    mem_usage, _ = to_bytes(data['MemUsage'])
    stat['mem_usage'] = mem_usage

    stat['cpu_usage'] = float(data['CPUPerc'][:-1])

    stat['ts'] = parse_timestamp(data['timestamp'])

    return stat


def read_stats():
    stats = collections.defaultdict(list)

    with open('stats/stats.ndjson') as file:
        for line in file:
            stat = parse_stat_line(line)
            stats[stat['name']].append(stat)

    return stats


def main(stats):
    assert len(stats) <= len(COLORS), f'{len(stats)} > {len(COLORS)}'

    metrics = [
        ('cpu_usage', 'CPU Usage (%)'),
        ('mem_usage', 'Memory Usage (Bytes)'),
        ('blk_read', 'Disk Read (Bytes)'),
        ('blk_write', 'Disk Write (Bytes)'),
        ('net_read', 'Network Read (Bytes)'),
        ('net_write', 'Network Write (Bytes)'),
    ]

    plt.figure(figsize=(18, 8))
    for metric_name, metric_desc in metrics:
        for node in sorted(stats.keys()):
            plt.plot(
                [stat['ts'] for stat in stats[node]],
                [stat[metric_name] for stat in stats[node]],
                color=COLORS[int(node[-2:])],
                label=node,
            )

        plt.xlabel('Time')
        plt.xticks(rotation=45)

        plt.ylabel(metric_desc)

        plt.legend(
            loc='upper center',
            ncol=len(stats),
            bbox_to_anchor=(0.5, 1.1),
        )
        # plt.show()
        plt.savefig(f'tex/figures/{metric_name}.png', bbox_inches='tight')
        plt.clf()


if __name__ == '__main__':
    main(read_stats())
