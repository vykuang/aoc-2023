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
    logger.debug(f"pattern:\n{pattern}")
    pattern = pattern.replace(".", "0").replace("#", "1")
    return [[bit for bit in line] for line in pattern.split("\n") if line]


def find_reflection(pattern: list[str], diff_lim=0) -> int:
    """
    Given a bit matrix, compare rows from the reflection line until
    diff_lim differences are found, and one or both ends is reached
    if diff_lim = 0, we're looking for perfect reflections
    if diff_lim = 1, we're looking for reflections with 1 smudge
    """
    logger.debug(f"first row:{pattern[0]}")
    bmat = [int("".join(p), base=2) for p in pattern]
    prev = bmat[0]
    for i, row in enumerate(bmat[1:], start=1):
        # initialize the new counters for each row comparison
        diff = 0
        above = i - 1
        below = i
        while diff <= diff_lim:
            if above < 0 or below >= len(bmat):
                # reach the end
                break
            # equiv to bin(num).count('1')
            diff += (bmat[above] ^ bmat[below]).bit_count()
            above -= 1
            below += 1

            # check until ends; current check b/w i-1 and i
            # + 1 accounts for us starting from 1st row instead of 0th
            # e.g. at i = 1, we're actually at the 2nd row of matrix
        if diff == diff_lim:
            # ensures we're not _under_ our req
            return i


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
    ndiff = 1 if part_two else 0
    rows = cols = 0
    for p in patterns:
        # r_ref = c_ref = None
        logger.debug(f"pattern:\n{p}")
        logger.debug(f"len: {len(p)}\tfirst row: {p[0]}")
        if r_ref := find_reflection(p, ndiff):
            logger.debug(f"ref row found: {r_ref}")
            # if found, no need to look for vertical
            rows += r_ref
        else:
            p_transposed = [*zip(*p)]
            logger.debug(f"transposed:\n{p_transposed}")
            if c_ref := find_reflection(p_transposed, ndiff):
                logger.debug(f"ref col found: {c_ref}")
                cols += c_ref
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
