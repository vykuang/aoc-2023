#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def bit_convert(pattern):
    """
    Convert "...##.#" patterns into 0s and 1s
    Each pattern becomes a matrix of bits
    """
    pattern = pattern.replace(".", "0").replace("#", "1")
    return [[int(bit) for bit in line] for line in pattern.split("\n")]


def find_reflection(pattern: list[str], ndiff=0) -> int:
    """
    Given a bit matrix, compare adjacent rows until one with
    ndiff differences is found
    """

    return n_row


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    patterns = [bit_convert(p) for p in "".join(read_line(fp)).split("\n\n")]

    # execute
    tstart = time_ns()
    rows = cols = 0
    for p in patterns:
        r_ref = c_ref = None
        logger.debug(f"pattern:\n{p}")
        logger.debug(f"len: {len(p)}\tfirst row: {p[0]}")
        if r_ref := find_reflection(p):
            logger.debug(f"ref row found: {r_ref}")
            # if found, no need to look for vertical
        else:
            p_transposed = [*zip(*p)]
            logger.debug(f"transposed:\n{p_transposed}")
            if c_ref := find_reflection(p_transposed):
                logger.debug(f"ref col found: {c_ref}")
    # output
    logger.info(f"total: {cols + 100 * rows}")

    tstop = time_ns()
    logger.info(f"runtime: {(tstop-tstart)/1e6:.3f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
