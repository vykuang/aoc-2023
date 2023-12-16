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


def parse_map_entry(line: str) -> dict:
    """
    parse "AAA = (BBB, CCC)" to dict:
    {'AAA': {'L': 'BBB', 'R': 'CCC'}}
    """
    k = line[:3]
    l = line[7:10]
    r = line[12:15]
    return k, l, r


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    dirs = read_line(fp)
    logger.debug(f"dirs: {dirs}")
    next(read_line(fp))  # skip empty line
    node_map = {parse_map_entry(line) for line in read_line(fp)}
    logger.debug(f"node map: {node_map}")
    # for line in read_line(fp):
    #    logger.debug(f'{line}')
    #    tokens = line.split()
    #    if len(tokens) == 1:
    #        dirs = tokens
    #    elif len(tokens) > 1:
    #        node_map.update(parse_map_entry(line))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
