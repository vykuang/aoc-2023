#!/usr/bin/env python3
"""
sample:
Time:      7  15   30
Distance:  9  40  200

Input:
Time:        53     71     78     80
Distance:   275   1181   1215   1524
"""
from pathlib import Path
import argparse
import logging
import sys
import math

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def find_margin(time, dist) -> int:
    """
    Solve the quadratic root for the equation
    t^2 - time * t + dist = 0
    then return the integer difference between the roots
    """
    logger.debug(f"t: {time}\td: {dist}")
    dscrmnt = math.sqrt(4 * dist)
    t0 = time**2 - dscrmnt
    t1 = time**2 + dscrmnt
    logger.debug(f"roots: {t0}, {t1}")
    return abs(math.floor(t1 - t0))


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    elif sample and part_two:
        fp = "sample2.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    for line in read_line(fp):
        tokens = line.split()
        if tokens[0] == "Time:":
            times = [int(token) for token in tokens[1:]]
            logger.debug(f"times: {times}")
        elif tokens[0] == "Distance:":
            dists = [int(token) for token in tokens[1:]]
            logger.debug(f"distances: {dists}")
        else:
            next

    # solve quadratic for each pair of (time, dist)
    margins = math.prod([find_margin(time, dist) for time, dist in zip(times, dists)])
    logger.info(f"margin power: {margins}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
