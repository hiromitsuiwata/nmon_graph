#!/usr/local/bin/python3

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import io

month_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
             "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}


def read_nmon(filepath, str, remove_first_line):
    length = len(str) + 1
    with open(filepath) as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
    filtered = list(map(lambda x: x[length:], filter(
        lambda x: x.startswith(str), lines)))
    if remove_first_line:
        print(filtered[0])
        return filtered[1:]
    else:
        return filtered


def lines_to_df(lines, names):
    df = pd.read_csv(io.StringIO('\n'.join(lines)), header=None, names=names)
    df = df.drop('time', axis=1)
    return df


def lines_to_df_datetime(lines):
    datetime_lines = []
    for line in lines:
        split = line.split(',')
        time = split[1]
        date_split = split[2].split('-')
        datetime_str = date_split[2] + '-' + \
            replace_month(date_split[1]) + '-' + date_split[0] + 'T' + time
        datetime_lines.append(datetime_str)
    df = pd.read_csv(io.StringIO('\n'.join(datetime_lines)), header=None)
    df[0] = pd.to_datetime(df[0])
    return df


def replace_month(str):
    return month_map[str]


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('filepath', help='filepath: nmon file path')
    args = parse.parse_args()
    filepath = args.filepath
    print(filepath)

    df_cpu_all = lines_to_df(read_nmon(filepath, "CPU_ALL", True), [
                             "time", "User%", "Sys%", "Wait%", "Idle%", "Steal%", "Busy", "CPUs"])
    df_memory = lines_to_df(read_nmon(filepath, "MEM", True), [
        "time", "memtotal", "hightotal", "lowtotal", "swaptotal", "memfree", "highfree", "lowfree", "swapfree", "memshared", "cached", "active", "bigfree", "buffers", "swapcached", "inactive"])
    df_datetime = lines_to_df_datetime(read_nmon(filepath, "ZZZZ", False))

    df = pd.concat([df_datetime, df_cpu_all, df_memory], axis=1)
    df = df.set_index(0)
    print(df)

    fig, ax = plt.subplots(1, 2, tight_layout=False, figsize=(12.0, 6.0))
    fig.subplots_adjust(bottom=0.2)

    ax[0].tick_params(axis="x", labelrotation=45)
    ax[1].tick_params(axis="x", labelrotation=45)

    ax[0].grid(True)
    ax[1].grid(True)
    ax[0].stackplot(df.index, df['User%'], df['Sys%'],
                    df['Wait%'], labels=['User%', 'Sys%', 'Wait%'])
    ax[1].plot(df.index, df['memfree'], label='memfree')
    ax[1].plot(df.index, df['memtotal'], label='memtotal')
    ax[0].legend(loc='upper right')
    ax[1].legend(loc='upper right')

    ax[0].set_ylabel('CPU%')
    ax[1].set_ylabel('MEM(MB)')

    plt.show()
