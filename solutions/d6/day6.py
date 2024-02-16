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


def is_int(num: float) -> bool:
    """Is our float equal to its int?
    using subtraction and int() introduces precision issues related
    to float arithmetic
    use % modulo instead
    """
    # return num - int(num) == 0
    return num % 1 == 0


def find_margin(time, dist) -> int:
    """
    Solve the quadratic root for the equation
    t^2 - time * t + dist = 0
    then return the integer difference between the roots
    """
    logger.debug(f"t: {time}\td: {dist}")
    dscrmnt = math.sqrt(time**2 - 4 * dist)
    t0 = (time - dscrmnt) / 2
    t1 = (time + dscrmnt) / 2
    logger.debug(f"roots: {t0:.2f}, {t1:.2f}")
    # handle perfect ints as edge cases, since they should not count
    n_soln = math.floor(t1) - math.ceil(t0) + 1
    if is_int(t0):
        n_soln -= 2
    logger.debug(f"num. soln = {n_soln}")
    return n_soln


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    for line in read_line(fp):
        tokens = line.split()
        if tokens[0] == "Time:":
            if part_two:
                time = int("".join(tokens[1:]))
                logger.debug(f"time: {time}")
            else:
                times = [int(token) for token in tokens[1:]]
                logger.debug(f"times: {times}")
        elif tokens[0] == "Distance:":
            if part_two:
                dist = int("".join(tokens[1:]))
                logger.debug(f"distance: {dist}")
            else:
                dists = [int(token) for token in tokens[1:]]
                logger.debug(f"distances: {dists}")
        else:
            next

    # solve quadratic for each pair of (time, dist)
    if part_two:
        margins = find_margin(time, dist)
    else:
        margins = math.prod(
            [find_margin(time, dist) for time, dist in zip(times, dists)]
        )
    logger.info(f"margin power: {margins}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
