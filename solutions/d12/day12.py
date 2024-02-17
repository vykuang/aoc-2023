#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import Counter

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def find_arrangements(springs: str, sep="?") -> list:
    """
    Return all possible substitutions of "?"
    For each "?", return a new string replaced by either "." or "#"
    """
    # base case: no '?' found
    # if (pos := springs.find(sep)) == -1:
    if sep not in springs:
        return [springs]

    # otherwise, recursively replace '?' with both '.' and '#'
    temp = [springs.replace(sep, ch, 1) for ch in [".", "#"]]
    arrangements = []
    for perm in temp:
        arrangements.extend(find_arrangements(perm))
    return arrangements


def is_valid_arrng(spring: str, grps: list[int], sp="#") -> bool:
    """
    does the spring arrangement satisfy the conditions
    specified in grps?
    """
    logger.debug(f"checking: {spring}")
    if Counter(spring)[sp] != sum(grps):
        logger.debug(f"springs: {Counter(spring)[sp]}\tneed: {sum(grps)}")
        return False
    # check arrangement
    else:
        count_grps = []
        curr = 0
        for ch in spring:
            if ch == "#":
                curr += 1
            else:
                count_grps.append(curr)
                curr = 0
        # in case last ch is also '#'
        count_grps.append(curr)

        count_grps = [c for c in count_grps if c]
        logger.debug(f"count: {count_grps}\tcheck: {grps}")
        return grps == count_grps


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    num_arrngs = []
    for line in read_line(fp):
        springs, grps = line.split()
        # remove extraneous '.' to prune states
        springs = '.'.join([sp for sp in springs.split('.') if sp])
        grps = [int(n) for n in grps.split(",")]
        if part_two:
            springs = "?".join(springs for _ in range(5))
            grps *= 5
        logger.debug(f"springs: {springs}\tgroups: {grps}")

        all_arrng = find_arrangements(springs)
        logger.debug(f"all arrangements:\n{list(all_arrng)}")
        num_valids = sum([is_valid_arrng(spring, grps) for spring in all_arrng])
        logger.debug(f"valids: {num_valids}")
        num_arrngs.append(num_valids)

    logger.info(f"{sum(num_arrngs)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
