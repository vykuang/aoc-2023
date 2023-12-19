#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
import re
from itertools import chain

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def find_gx(line: str, nrow: int, re_gx=re.compile("#")) -> list:
    """
    Finds all occurrences of gx and their location
    """
    xs = [m.start() for m in re_gx.finditer(line)]
    return [complex(x, -nrow) for x in xs]


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    # collect initial g locations
    gmap = [find_gx(line, nrow) for nrow, line in enumerate(read_line(fp))]
    gmap = list(chain.from_iterable(gmap))
    logger.debug(gmap)

    # use all gx loc to find empty rows/cols
    gx_rows = [int(c.imag) for c in gmap]
    gx_cols = [int(c.real) for c in gmap]
    logger.debug(f"gx rows: {gx_rows}\tgx cols: {gx_cols}")
    empty_rows = set(range(0, min(gx_rows), -1)).difference(gx_rows)
    empty_cols = set(range(max(gx_cols))).difference(gx_cols)
    logger.debug(f"empty rows: {empty_rows}\nempty cols: {empty_cols}")

    # move galaxies based on expanded space
    # iterate through the galaxies
    mult = 1e6 if part_two else 2
    gdict = {}
    for i, g in enumerate(gmap):
        # count how many rows are above, and how many cols before
        logger.debug(f"pre exp: {g}")
        nrows_abv = sum([g.imag < empty for empty in empty_rows])
        g -= nrows_abv * 1j * (mult - 1)

        ncols_bef = sum([g.real > empty for empty in empty_cols])
        g += ncols_bef * (mult - 1)
        logger.debug(f"post exp: {g}")
        gdict |= {i: g}

    # calculate manhattan dist for all pairs using expanded coordinates
    logger.debug(f"gdict: {gdict}")
    pairs = [(i, j) for i in gdict for j in gdict if i < j]
    logger.debug(f"unique pairs: {len(pairs)}")
    distances = [
        abs(c.real) + abs(c.imag) for c in [gdict[p[1]] - gdict[p[0]] for p in pairs]
    ]
    for d, p in zip(distances, pairs):
        logger.debug(f"pair: {p}\tdist: {d}")
    logger.info(f"total: {sum(distances)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
