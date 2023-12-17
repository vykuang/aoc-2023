#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def main(sample: bool, part_two: bool, loglevel: str):
    """
    Pathfinding?
    Given a map of pipes, find the furthest distance from the start
    F, 7, J, L are elbow pipes
    -: straights
    .: ground
    S: start
    """

    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    pipe_map = read_line(fp)
    # find 'S' pos
    # pipes could only connect n/e/s/w, so check the 4 adj squares
    # -: - on east/west; F, L on west only, 7, J on east only
    # |: | on north/south; J, L on south only, F, 7 on north only
    # F: east/south; -, 7, J on east, J, L on south
    # 7: south/west; -, F, L west, J, L south
    # J: north/west; -, F, L west, 7, F north
    # L: north/east; -, 7, J on east, 7, F north
    # S: - e/w, | n/s,


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
