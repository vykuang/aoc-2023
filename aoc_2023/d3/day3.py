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
    p_gear=re.compile(r"\*"),
    p_num=re.compile(r"\d+"),
) -> list[tuple]:
    """ """
    # num_a = list(p_num.finditer(above))
    # num_curr = list(p_num.finditer(curr))
    # num_b = list(p_num.finditer(below))
    # list() allows reuseability
    logger.debug(f"above:\t{above}curr:\t{curr}below:\t{below}")
    nums = [p_num.finditer(line) for line in [above, curr, below] if line]
    nums = list(chain.from_iterable(nums))
    logger.debug(f"nums:{nums}")
    parts = []
    if curr:
        for gear in p_gear.finditer(curr):
            logger.debug(f"gear start and end: {gear.start()}-{gear.end()}")
            part = [
                int(num.group(0))
                for num in nums
                if (num.start() >= gear.start() - 1 and num.start() <= gear.end())
                or (num.end() >= gear.start() and num.end() < gear.end())
            ]
            if len(part) == 2:
                parts.append(part)
                logger.debug(f"found part {part}")
            else:
                logger.debug(f"found wrong parts {part}")

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

    # analyze rolling window of 3 lines
    # adding `\s` to our regex is crucial, to ignore all whitespace char
    # note that this soln requires appending an empty line to the input
    prog_sym = re.compile(r"[^\d\s.]")
    prog_num = re.compile(r"\d+")
    n_2 = n_1 = None
    total = 0
    for line in read_line(fp):
        if part_two:
            total += sum(starmap(operator.mul, find_gear_parts(n_2, n_1, line)))
        else:
            if not n_2:
                # first line
                n_2 = line
                next
            elif not n_1:
                # check first line
                n_1 = line
                nums = prog_num.finditer(n_2)
                sym_curr = list(prog_sym.finditer(n_2))
                sym_blw = list(prog_sym.finditer(n_1))

                for n in nums:
                    logger.debug(f"current: {n.group(0)}")

                    a = n.start() - 1
                    b = n.end()
                    for sym in [*sym_curr, *sym_blw]:
                        # use sym.start(), the actual pos
                        if sym.start() >= a and sym.start() <= b:
                            logger.debug(f"add {int(n.group(0))}")
                            total += int(n.group(0))
                            # move on to next num
                            break
            else:
                nums = prog_num.finditer(n_1)
                sym_abv = list(prog_sym.finditer(n_2))
                sym_curr = list(prog_sym.finditer(n_1))
                sym_blw = list(prog_sym.finditer(line))
                for n in nums:
                    logger.debug(f"current: {n.group(0)}")

                    a = n.start() - 1
                    b = n.end()
                    for sym in [*sym_abv, *sym_curr, *sym_blw]:
                        # use sym.start(), the actual pos
                        if sym.start() >= a and sym.start() <= b:
                            logger.debug(f"add {int(n.group(0))}")
                            total += int(n.group(0))
                            # move on to next num
                            break

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
