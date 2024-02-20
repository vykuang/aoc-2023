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


def count_broken(springs, grps, cache, working=".", broken="#", unknown="?") -> int:
    """
    helper func to guardrail the recursion
    """
    logger.debug(f"counting brokens; sp: {springs}\ngroups: {grps}")
    nx_grp = grps[0]
    # fix unknowns as broken springs to match group
    brokens = springs[:nx_grp].replace(unknown, broken)
    if len(brokens) != nx_grp:
        # # does not match
        return 0
    if working in brokens:
        # prune; invalid
        return 0
    # if not springs[nx_grp:] and len(grps) > 1:
    #     # no more springs after current group, but groups still exist
    #     return 0
    if len(springs) == nx_grp:
        # remaining springs = num specified in next group
        if len(grps) == 1:
            # last group
            return 1
        else:
            # '#' remains but no more groups; invalid
            return 0
    if springs[nx_grp] in [unknown, working]:
        # must be allowed to be a separator, otherwise current group
        # is invalidated
        # +1 skips, assuming it must be '.'
        # num_arrng = find_arrangements(springs[nx_grp+1:], grps[1:], cache)
        # cache[(springs[nx_grp+1:], grps[1:])] = num_arrng
        # return num_arrng
        return find_arrangements(springs[nx_grp + 1 :], grps[1:], cache)
    return 0


def find_arrangements(
    springs, grps, cache={}, working=".", broken="#", unknown="?"
) -> int:
    """
    Count number of valid arrangements using recursion and memoization
    groups refer to contiguous broken springs (#)
    """
    # check cache
    if (key := (springs, grps)) in cache:
        logger.debug("cached value")
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

    # match springs[0]:
    #     case broken:
    #         return count_broken(springs, grps, cache)
    #     case working:

    #     case unknown:

    if nx_sp == broken:
        num_arrng = count_broken(springs, grps, cache)

    elif nx_sp == working:
        # groups do not change; move on to next
        num_arrng = find_arrangements(springs[1:], grps, cache)
    elif nx_sp == unknown:
        # question mark = could be both
        num_working = find_arrangements(springs[1:], grps, cache)
        num_broken = count_broken(springs, grps, cache)
        num_arrng = num_working + num_broken
    else:
        raise ValueError("Unrecognized spring type")

    cache[(springs, grps)] = num_arrng
    return num_arrng


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
    cache = {}
    for line in read_line(fp):
        springs, grps = line.split()
        # immutability for caching
        grps = tuple([int(n) for n in grps.split(",")])
        if part_two:
            springs = "?".join(springs for _ in range(5))
            grps *= 5
        springs = ".".join(sp for sp in springs.split(".") if sp)
        logger.debug(f"springs: {springs}\ngroups: {grps}")

        num_arrngs += find_arrangements(springs, grps, cache)
        logger.debug(f"running total: {num_arrngs}\tcache size: {len(cache)}")
        logger.debug("-" * 10)

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
