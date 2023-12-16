#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from itertools import accumulate, pairwise
import operator

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f

def differences(points: list[int]) -> list[int]:
    """Returns first difference of list of ints"""
    pairs = pairwise(points)
    diffs = [p[1] - p[0] for p in pairs]
    logger.debug(f'diffs: {diffs}')
    return diffs

def predict_polynomial(line_diffs: list, part_two: bool = False) -> int:
    """
    Given list of differences, each subsequent sequence one level deeper than the prior,
    calculate the next polynomial item in the original sequence
    The last sequence in the list should consist of only one number
    Add that number to the last item of the prior list, append it, and repeat
    until we reach the first list
    """

    addend = 0
    for diffs in line_diffs[::-1]:
        diffs.append(diffs[-1] + addend)
        if part_two:
            prior = diffs[0] - addend
        addend = diffs[-1]

    return addend

def extrapolate_past(line_diffs: list) -> int:
    """
    Find the value prior to the first in the original sequence
    """

    sub = 0
    for diffs in line_diffs[::-1]:


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    preds = []
    for line in read_line(fp):
        points = [int(num) for num in line.split()]
        base_diff_found = False
        line_diffs = [points]
        while not base_diff_found:
            diffs = differences(points)
            # save the diffs
            line_diffs.append(diffs)
            # check for equality
            if len(set(diffs)) > 1:
                # not all the same; get diffs again
                points = diffs
            else:
                preds.append(predict_polynomial(line_diffs))
                base_diff_found = True

        logger.debug(f'pred: {preds[-1]}')
    logger.info(f'total extrapolated values: {sum(preds)}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
