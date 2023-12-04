#!/usr/bin/env python3
from pathlib import Path
import argparse
import re
import logging
import sys
from collections import defaultdict
import math

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    # boilerplate #
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    elif sample and part_two:
        fp = "sample2.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.debug(f"Using {fp}")
    # BOILERPLATE END #

    total = 0
    cmax = dict(red=12, green=13, blue=14)
    p_id = re.compile(r"\d+")
    p_sets = re.compile(r"(\d+) (red|blue|green)[, ]*")
    for record in read_line(fp):
        colors = defaultdict(list)
        gid, _ = record.split(":")
        gid = int(p_id.search(gid).group(0))
        logger.debug(f"ID: {gid}")
        # sets = sets.split(';')
        cubecounts = p_sets.finditer(record)
        logger.debug("parsed sets:")
        for m in cubecounts:
            logger.debug(f"count: {m.group(1)}; color: {m.group(2)}")
            colors[m.group(2)].append(int(m.group(1)))
            logger.debug(f"colors: {colors}")
        setmax = {color: max(colors[color]) for color in colors}
        logger.debug(f"setmax:\n{setmax}")
        if not part_two:
            if all([setmax[color] <= cmax[color] for color in setmax]):
                total += gid
        else:
            total += math.prod(setmax.values())
        logger.debug(f"new total: {total}")

    logger.info(f"total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
