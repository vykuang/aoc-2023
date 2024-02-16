#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
import re
from itertools import starmap, chain
import operator

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def find_gear_parts(
    above: str,
    curr: str,
    below: str,
    part_two: bool = False,
    p_sym=re.compile(r"[^\d\s.]"),
    p_gear=re.compile(r"\*"),
    p_num=re.compile(r"\d+"),
) -> list:
    """ """
    # list() allows reuseability
    logger.debug(f"above:\t{above}curr:\t{curr}below:\t{below}")
    nums = [p_num.finditer(line) for line in [above, curr, below] if line]
    nums = list(chain.from_iterable(nums))
    logger.debug(f"nums:{nums}")
    parts = []
    if curr:
        gears = gears = p_gear.finditer(curr) if part_two else p_sym.finditer(curr)
        for gear in gears:
            logger.debug(f"gear start and end: {gear.start()}-{gear.end()}")
            # collect numbers if position of the gear is adj to number
            adj_part = [
                int(num.group(0))
                for num in nums
                if (num.start() - 1 <= gear.start() <= num.end())
            ]
            # only append if we have a pair
            if part_two and (num_parts := len(adj_part)) == 2:
                parts.append(adj_part)
                logger.debug(f"found part {adj_part}")
            elif not part_two:
                parts.extend(adj_part)
            else:
                logger.info(f"found wrong parts {adj_part}")
                logger.info(f"above:\t{above}curr:\t{curr}below:\t{below}")
    return parts


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
    logger.debug(f"Using {fp}")
    logger.info(f"Pt. ii: {part_two}")

    # analyze rolling window of 3 lines
    # adding `\s` to our regex is crucial, to ignore all whitespace char
    # note that this soln requires an empty line atthe end of input file
    # otherwise a separate section after our for loop is required to
    # specifically handle the last line
    prog_sym = re.compile(r"[^\d\s.]")
    prog_num = re.compile(r"\d+")
    n_2 = n_1 = None
    total = 0
    for line in read_line(fp):
        if part_two:
            total += sum(
                starmap(operator.mul, find_gear_parts(n_2, n_1, line, part_two))
            )
        else:
            total += sum(find_gear_parts(n_2, n_1, line))
        # rollover
        n_2 = n_1
        n_1 = line
    logger.info(f"total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
