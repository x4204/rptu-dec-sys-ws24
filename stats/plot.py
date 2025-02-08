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

            if (stat['ts'] - prev_stat[stat['name']]['ts']).total_seconds() > 1:
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


def bytes_pretty(count):
    idx = 0
    while count > 1024:
        count /= 1024
        idx += 1

    return ' '.join([f'{count:.2f}', ['B', 'KiB', 'MiB', 'GiB'][idx]])


def avg(ns):
    return sum(ns) / len(ns)


def main():
    if len(sys.argv) != 3:
        print('usage: python -m stats.plot <in-path> <out-path>')
        raise SystemExit(1)

    _, in_path, out_path = sys.argv

    stats, buckets, totals = read_stats(in_path)

    kind = out_path.split('/')[-1]
    table_caption = {
        'original': 'Original Kubo',
        'ring': 'Ring',
        'grid': 'Grid',
        'graph-random': 'Random graph',
        'graph-complete': 'Complete graph',
    }[kind]

    with open(f'{out_path}/avg.tex', 'w') as file:
        file.write('\\begin{table}[H]\n')
        file.write('\\begin{center}\n')
        file.write(f'\\caption{{{table_caption} -- metrics averages}}\n')
        file.write(f'\\label{{tab:{kind}-avg}}\n')
        file.write('\\begin{tabular}{|c|c|c|c|c|c|c|}\n')
        file.write('\\hline\n')
        file.write('   & CPU usage & Memory usage & Disk read & Disk write & Network read & Network write\\\\\n')
        file.write('\\hline\n')

        for node in sorted(buckets):
            bs = buckets[node]
            file.write(f'{node[-2:]} & ')
            file.write(f'{avg(bs['cpu_usage']):.2f}\\% & ')
            file.write(f'{bytes_pretty(avg(bs['mem_usage']))} & ')
            file.write(f'{bytes_pretty(avg(bs['blk_read']))}/s & ')
            file.write(f'{bytes_pretty(avg(bs['blk_write']))}/s & ')
            file.write(f'{bytes_pretty(avg(bs['net_read']))}/s & ')
            file.write(f'{bytes_pretty(avg(bs['net_write']))}/s\\\\\n')

        file.write('\\hline\n')
        file.write('\\end{tabular}\n')
        file.write('\\end{center}\n')
        file.write('\\end{table}\n')

    with open(f'{out_path}/total.tex', 'w') as file:
        file.write('\\begin{table}[H]\n')
        file.write('\\begin{center}\n')
        file.write(f'\\caption{{{table_caption} -- metrics totals}}\n')
        file.write(f'\\label{{tab:{kind}-total}}\n')
        file.write('\\begin{tabular}{|c|c|c|c|c|c|c|}\n')
        file.write('\\hline\n')
        file.write('   & Disk read & Disk write & Network read & Network write\\\\\n')
        file.write('\\hline\n')

        for node in sorted(buckets):
            ts = totals[node]
            file.write(f'{node[-2:]} & ')
            file.write(f'{bytes_pretty(ts['blk_read'])} & ')
            file.write(f'{bytes_pretty(ts['blk_write'])} & ')
            file.write(f'{bytes_pretty(ts['net_read'])} & ')
            file.write(f'{bytes_pretty(ts['net_write'])}\\\\\n')

        file.write('\\hline\n')
        file.write('\\end{tabular}\n')
        file.write('\\end{center}\n')
        file.write('\\end{table}\n')

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
