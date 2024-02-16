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


def transpose(pattern: list[str]) -> list[str]:
    """Given list of equal length str, transpose the characters"""
    # transposed = []
    # for i in range(len(pattern[0])):
    #     transposed.append([row[i] for row in pattern])
    return ["".join([row[i] for row in pattern]) for i in range(len(pattern[0]))]


def find_reflection(pattern: list[str]) -> int:
    """Given list of equal len str, find the in-between row of reflection,
    if exists

    Iterates through the rows to find when row_n == row_n-1
    """
    prev = None
    for i, row in enumerate(pattern):
        if row == prev:
            logger.debug(f"checking row {i}")
            # potential reflection point found
            dist = 1
            while (
                (above := i - dist - 1) >= 0
                and (below := i + dist) < len(pattern)
                and pattern[above] == pattern[below]
            ):
                # iterate away from reflection point
                dist += 1
            # check if we iterated to either end
            logger.debug(f"dist: {dist}")
            if above < 0 or below == len(pattern):
                return i
        prev = row
    logger.debug("no reflection found")


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    patterns = []
    pattern = []
    for line in read_line(fp):
        logger.debug(f"line: {line}")
        if l := line.strip():
            pattern.append(l)
        else:
            patterns.append(pattern)
            pattern = []
    # no empty line at end of file; last case as edge case
    patterns.append(pattern)

    rows = []
    cols = []
    for i, p in enumerate(patterns):
        logger.debug(f"pattern {i}:\n{p}")
        r_ref = find_reflection(p)
        if r_ref:
            logger.debug(f"ref row found: {r_ref}")
            rows.append(r_ref)
        p_transposed = transpose(p)
        logger.debug(f"transposed:\n{p_transposed}")
        c_ref = find_reflection(p_transposed)
        if c_ref:
            logger.debug(f"ref col found: {c_ref}")
            cols.append(c_ref)

    logger.debug(f"cols: {cols}\nrows: {rows}")
    logger.info(f"total: {sum(cols) + 100 * sum(rows)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
