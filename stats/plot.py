import collections
import json
import math
import matplotlib.pyplot as plt
import sys

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
    if text.endswith('MB'):
        return int(float(text[:-2]) * (1000 ** 2))
    if text.endswith('GB'):
        return int(float(text[:-2]) * (1000 ** 3))
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


def read_stats(path):
    stats = collections.defaultdict(list)

    prev_stat = {}
    buckets = {}
    totals = {}

    with open(path) as file:
        for line in file:
            stat = parse_stat_line(line)
            
            if not prev_stat.get(stat['name']):
                prev_stat[stat['name']] = stat
                buckets[stat['name']] = {}
                buckets[stat['name']]['cpu_usage'] = []
                buckets[stat['name']]['mem_usage'] = []
                buckets[stat['name']]['blk_read'] = []
                buckets[stat['name']]['blk_write'] = []
                buckets[stat['name']]['net_read'] = []
                buckets[stat['name']]['net_write'] = []

            if (stat['ts'] - prev_stat[stat['name']]['ts']).total_seconds() > 10:
                buckets[stat['name']]['blk_read'].append(stat['blk_read']-prev_stat[stat['name']]['blk_read'])
                buckets[stat['name']]['blk_write'].append(stat['blk_write']-prev_stat[stat['name']]['blk_write'])
                buckets[stat['name']]['net_write'].append(stat['net_write']-prev_stat[stat['name']]['net_write'])
                buckets[stat['name']]['net_read'].append(stat['net_read']-prev_stat[stat['name']]['net_read'])

                prev_stat[stat['name']] = stat
            buckets[stat['name']]['cpu_usage'].append(stat['cpu_usage'])
            buckets[stat['name']]['mem_usage'].append(stat['mem_usage'])

            stats[stat['name']].append(stat)
    
    for node in sorted(stats.keys()):
        buckets[node]['blk_read'].append(stats[node][-1]['blk_read']-prev_stat[node]['blk_read'])
        buckets[node]['blk_write'].append(stats[node][-1]['blk_write']-prev_stat[node]['blk_write'])
        buckets[node]['net_read'].append(stats[node][-1]['net_read']-prev_stat[node]['net_read'])
        buckets[node]['net_write'].append(stats[node][-1]['net_write']-prev_stat[node]['net_write'])

        totals[node] = {}
        totals[node]['blk_read'] = stats[node][-1]['blk_read']
        totals[node]['blk_write'] = stats[node][-1]['blk_write']
        totals[node]['net_write'] = stats[node][-1]['net_write']
        totals[node]['net_read'] = stats[node][-1]['net_read']
    
    return (stats, buckets, totals)


def main():
    if len(sys.argv) != 3:
        print('usage: python -m stats.plot <in-path> <out-path>')
        raise SystemExit(1)

    _, in_path, out_path = sys.argv

    stats, buckets, totals = read_stats(in_path)

    with open(f'{out_path}/avg_and_total.txt', 'w') as file:
        for node in sorted(buckets.keys()):
            file.write(f'{node}\n')
            file.write('Average values:\n')
            file.write(f'avg_cpu_usage: {sum(buckets[node]['cpu_usage'])/len(buckets[node]['cpu_usage'])}\n')
            file.write(f'avg_mem_usage: {sum(buckets[node]['mem_usage'])/len(buckets[node]['mem_usage'])}\n')
            file.write(f'avg_blk_read: {sum(buckets[node]['blk_read'])/len(buckets[node]['blk_read'])}\n')
            file.write(f'avg_blk_write: {sum(buckets[node]['blk_write'])/len(buckets[node]['blk_write'])}\n')
            file.write(f'avg_net_read: {sum(buckets[node]['net_read'])/len(buckets[node]['net_read'])}\n')
            file.write(f'avg_net_write: {sum(buckets[node]['net_write'])/len(buckets[node]['net_write'])}\n\n')

            file.write('Total values:\n')
            file.write(f'total_blk_read: {totals[node]['blk_read']}\n')
            file.write(f'total_blk_write: {totals[node]['blk_write']}\n')
            file.write(f'total_net_read: {totals[node]['net_read']}\n')
            file.write(f'total_net_write: {totals[node]['net_write']}\n\n')

    assert len(stats) <= len(COLORS), f'{len(stats)} > {len(COLORS)}'

    metrics = [
        ('cpu_usage', 'CPU Usage (%)'),
        ('mem_usage', 'Memory Usage (Bytes)'),
        ('blk_read', 'Disk Read (Bytes)'),
        ('blk_write', 'Disk Write (Bytes)'),
        ('net_read', 'Network Read (Bytes)'),
        ('net_write', 'Network Write (Bytes)'),
    ]

    plt.rc('font', size=14)
    plt.figure(figsize=(10, 6))
    for metric_name, metric_desc in metrics:
        for node in sorted(stats.keys()):
            plt.plot(
                [stat['ts'] for stat in stats[node]],
                [stat[metric_name] for stat in stats[node]],
                color=COLORS[int(node[-2:])],
                label=node[-2:],
            )

        plt.xlabel('Time')
        plt.xticks(rotation=45)

        plt.ylabel(metric_desc)

        plt.legend(
            loc='upper center',
            ncol=math.ceil(len(stats) / 2),
            bbox_to_anchor=(0.5, 1.25),
        )
        # plt.show()
        plt.savefig(f'{out_path}/{metric_name}.png', bbox_inches='tight')
        plt.clf()


if __name__ == '__main__':
    main()
