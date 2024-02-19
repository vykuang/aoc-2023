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

def find_arrangements(springs, grps, cache={}, working='.', broken='#', unknown='?') -> int:
    """
    Count number of valid arrangements using recursion and memoization
    groups refer to contiguous broken springs (#)
    """
    # check cache
    if (key := (springs, grps)) in cache:
        return cache[key]
    # base case
    if not grps:
        # still valid if no more brokens
        if broken not in springs:
            # unknown could still be in springs, but the only way for it
            # for it to be valid is if they are all working,
            # thus only one valid arrangement
            return 1
        else:
            # more broken springs not listed in groups; invalid
            return 0
    if not springs:
        # but groups still exist; must be invalid
        return 0

    # recursive
    nx_sp = springs[0]
    nx_grp = grps[0]


    if nx_sp == broken:
        # fixed as broken
        # this and the first group must be able to be converted to brokens
        brokens = springs[:nx_grp].replace(unknown, broken)
        if working in brokens:
            return 0
        if len(brokens) != nx_grp:
            return 0
        # else:
        #     if len(grps) == 1:
        #         return 1
        #     else:
        #         return 0
        if springs[nx_grp] in [unknown, working]:
            # must be allowed to be a separator, otherwise current group
            # is invalidated
            # +1 skips, assuming it must be '.'
            num_arrng = find_arrangements(springs[nx_grp+1:], grps[1:], cache)
            cache[(springs[nx_grp+1:], grps[1:])] = num_arrng
            return num_arrng
        return 0

    elif nx_sp == working:
        # fixed as working
        num_arrng = find_arrangements(springs[nx_grp:], grps, cache)
        cache[(springs[nx_grp:], grps)] = num_arrng
        return num_arrng

    else:
        # question mark = could be both
        num_working = find_arrangements(springs[nx_grp:], grps, cache)
        num_broken =
        return broken_spring() + find_arrangements(springs[1:], grps, cache)


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    # read input

    # execute
    tstart = time_ns()
    num_arrngs = 0
    for line in read_line(fp):
        springs, grps = line.split()
        springs = '.'.join(sp for sp in springs.split('.') if sp)
        # immutability for caching
        grps = tuple([int(n) for n in grps.split(",")])
        if part_two:
            springs = '?'.join(springs for _ in range(5))
            grps *= 5
        logger.debug(f"springs: {springs}\ngroups: {grps}")

        num_arrngs += find_arrangements(springs, grps)
        logger.debug('-'*10)

    logger.info(f"ans: {num_arrngs}")
    # output

    tstop = time_ns()
    logger.info(f"runtime: {(tstop-tstart)/1e6} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
