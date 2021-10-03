"""speed.py

Thin wrapper around speedtest-cli to average a few results
"""

import argparse
import os
import pathlib
import subprocess
import sys
from datetime import datetime

from speedtest import Speedtest

def get_speed(lines, word):
    """Return a float of the speed based on first word"""

    line = next(line for line in lines if line.startswith(word))
    return float(line.split()[1])


def avg(l):
    """Compute the average of a list"""
    return sum(l) / len(l)


def main(runs=3, drop_outliers=False, outfile=None):
    server = Speedtest().get_best_server()["id"]
    speeds = {"Download": [], "Upload": []}

    speedtest = pathlib.Path(sys.prefix) / "bin" / "speedtest-cli"
    if not speedtest.is_file():
        speedtest = "speedtest-cli"
    for _ in range(runs):
        cmd = subprocess.run(
            [speedtest, "--server", str(server)],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        raw_output = cmd.stdout
        lines = raw_output.splitlines()

        for updown in speeds.keys():
            speed = get_speed(lines, updown + ":")
            speeds[updown].append(speed)

    dt = datetime.now()
    output = "Test started at {}\n" "Averaging results over {} runs\n".format(
        dt, runs
    )
    for updown in speeds.keys():
        if drop_outliers and len(speeds[updown]) > 4:
            trimmed_speeds = sorted(speeds[updown])[1:-1]
            trimmed_msg = " (dropping highest and lowest)"
        else:
            trimmed_speeds = speeds[updown]
            trimmed_msg = ""
        output += "{} average{}: {:.02f}\n".format(
            updown, trimmed_msg, avg(trimmed_speeds)
        )
    if outfile is None:
        print(output)
    else:
        with open(outfile, "a") as f:
            f.write(
                "{0:%Y-%m-%d %H:%M},{1:.02f},{2:.02f},{3:.02f},{4:.02f},"
                "{5},{6}\n".format(
                    dt,
                    avg(speeds["Download"]),
                    avg(sorted(speeds["Download"])[1:-1]),
                    avg(speeds["Upload"]),
                    avg(sorted(speeds["Upload"])[1:-1]),
                    runs,
                    bool(drop_outliers),
                )
            )


def _cli():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument("-s", "--server", help="Specify nondefault server")
    parser.add_argument("-r", "--runs", type=int, help="Number of runs")
    parser.add_argument(
        "--drop-outliers",
        action="store_true",
        help="If runs >= 5, drop the highest and lowest",
    )
    parser.add_argument(
        "-o", "--outfile", help="Append output to file instead of stdout"
    )
    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    main(**_cli())
