#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
import re

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


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
    prog_sym = re.compile(r"[^\d.]")
    prog_num = re.compile(r"\d+")
    n_2 = n_1 = None
    total = 0
    for line in read_line(fp):
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
