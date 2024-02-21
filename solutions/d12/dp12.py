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


def count_arrng(springs, grps):
    """
    dynamic programming, bottom up/tabular approach
    table setup:
    """


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    num_arrngs = 0
    for line in read_line(fp):
        springs, grps = line.split()
        grps = [int(n) for n in grps.split(",")]
        if part_two:
            springs = "?".join([springs for _ in range(5)])
            grps *= 5
        # remove extraneous '.'
        springs = ".".join(sp for sp in springs.split(".") if sp)
        logger.debug(f"springs: {springs}\tgroups: {grps}")

        num_arrngs += count_arrng(springs, grps)
        logger.debug(f"total: {num_arrngs}")

    logger.info(f"{sum(num_arrngs)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
