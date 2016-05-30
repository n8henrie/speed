"""speed.py

Thin wrapper around speedtest-cli to average a few results
"""

import subprocess
import argparse
from datetime import datetime


def get_speed(lines, word):
    """Return a float of the speed based on first word"""

    line = next(line for line in lines if line.startswith(word))
    return float(line.split()[1])


def avg(l):
    """Compute the average of a list"""
    return sum(l) / len(l)


def main(server=1773, runs=3, drop_outliers=False):
    speeds = {'Download': [], 'Upload': []}
    for _ in range(runs):
        cmd = subprocess.run(['speedtest-cli', '--server', str(server)],
                             stdout=subprocess.PIPE, universal_newlines=True)
        raw_output = cmd.stdout
        lines = raw_output.splitlines()

        for updown in speeds.keys():
            speed = get_speed(lines, updown + ":")
            speeds[updown].append(speed)

    print("Test started at {}".format(datetime.now()))
    print("Averaging results over {} runs".format(runs))
    for updown in speeds.keys():
        if drop_outliers and len(speeds[updown]) > 4:
            trimmed_speeds = sorted(speeds[updown])[1:-1]
            trimmed_msg = " (dropping highest and lowest)"
        else:
            trimmed_speeds = speeds[updown]
            trimmed_msg = ""
        print("{} average{}: {:.02f}\n".format(updown, trimmed_msg,
                                               avg(trimmed_speeds)))


def _cli():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('-s', '--server', help="Specify nondefault server")
    parser.add_argument('-r', '--runs', type=int, help="Number of runs")
    parser.add_argument('--drop-outliers', action='store_true',
                        help="If runs >= 5, drop the highest and lowest")
    args = parser.parse_args()
    return vars(args)

if __name__ == '__main__':
    main(**_cli())
