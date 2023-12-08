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

    first = True
    for line in read_line(fp):
        match line.split():
            case ["seeds:", *seeds]:
                inits = [int(seed) for seed in seeds]
                logger.debug(f"inits: {inits}")
            case [mapdir, "map:"]:
                src, _, dest = mapdir.split("-")

                logger.debug(f"src: {src}\tdest: {dest}")
            case _:
                dest_start, src_start, rng = [int(num) for num in line.split()]
                curr_map |= {
                    src: dest
                    for src, dest in zip(range(src_start, rng), range(dst_start, rng))
                }
                logger.debug(dest_start, src_start, rng)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
