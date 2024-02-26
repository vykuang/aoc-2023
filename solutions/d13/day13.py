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


def transpose(pattern: list[str]) -> list[str]:
    """Given list of equal length str, transpose the characters"""
    # try 1
    # transposed = []
    # for i in range(len(pattern[0])):
    #     transposed.append([row[i] for row in pattern])
    # try 2
    # return ["".join([row[i] for row in pattern]) for i in range(len(pattern[0]))]
    # from megathread (and itertools recipe in docs)
    return [*zip(*pattern)]


def find_reflection(pattern: list[str], old_line=0) -> int:
    """Given list of equal len str, find the in-between row of reflection,
    if exists

    Iterates through the rows to find when row_n == row_n-1
    """
    prev = None
    n_row = None
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
            if (above < 0 or below == len(pattern)) and i != old_line:
                n_row = i
                break
        prev = row
    return n_row


def find_smudge(pattern: list[str], r_old, c_old) -> int:
    """
    Find the new reflection point if only one tile
    in the pattern is flipped
    """
    for row in range(len(pattern)):
        logger.debug(f"old {pattern[row]}")
        for j, col in enumerate(pattern[row]):
            chk = pattern.copy()
            # str is immutable
            flip = "#" if col == "." else "."
            chk[row] = chk[row][:j] + flip + chk[row][j + 1 :]
            if r_ref := find_reflection(chk, r_old):
                logger.debug(f"row found: {r_ref}; flipped {row}, {j}")
                return r_ref, None
            if c_ref := find_reflection(transpose(chk), c_old):
                logger.debug(f"col found: {c_ref}; flipped {row}, {j}")
                return None, c_ref


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
        # each set of pattern is divided by newline
        if line := line.strip():
            pattern.append(line)
        else:
            patterns.append(pattern)
            pattern = []
    # no empty line at end of file; last case as edge case
    patterns.append(pattern)

    # execute
    tstart = time_ns()
    rows = cols = 0
    for p in patterns:
        r_ref = c_ref = None
        logger.debug(f"pattern:\n{p}")
        if r_ref := find_reflection(p):
            logger.debug(f"ref row found: {r_ref}")
            # if found, no need to look for vertical
        else:
            p_transposed = transpose(p)
            logger.debug(f"transposed:\n{p_transposed}")
            if c_ref := find_reflection(p_transposed):
                logger.debug(f"ref col found: {c_ref}")
        if part_two:
            # brute-force
            logger.debug(f"passing {r_ref}, {c_ref} into smudge")
            try:
                r_ref, c_ref = find_smudge(p, r_ref, c_ref)
            except TypeError:
                logger.error("no reflection found:")
                for r in p:
                    logger.error(r)
        if r_ref:
            rows += r_ref
        else:
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
