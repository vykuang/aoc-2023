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
    # handles all other cases,
    # e.g. no more springs after current group, but groups still exist
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


def count_arrng(springs, grps, working=".", broken="#", unknown="?"):
    """
    dynamic programming, iterative, bottom up/tabular approach
    given count for '#??.', 2, we can use that result to count
    '###.#??.', (3, 2)
    table setup:
    rows: cont. groups, reversed. e.g. (1,1,3) -> 3, 1, 1
    columns: springs, 0-indexed
    Fill from top right corner
    """

    def count_working():
        """
        Retrieve prev cell, to the right
        """
        if col < len(springs) - 1:
            # retrieve from prev if not the end
            return dp[row][col + 1]
        # if first spring encountered is working, it cannot be valid
        return 0

    def count_broken():
        """
        First check that we have a valid sequence,
        if so, retrieve from above row, group + 1 cells to the right
        if not, set 0
        """
        chk_seq = springs[col : col + grp].replace(unknown, broken)
        logger.debug(f"chk_seq: {chk_seq}")
        if working in chk_seq or len(chk_seq) != grp:
            logger.debug("invalid")
            return 0
        if col + grp == len(springs):
            # prevents index out of range error
            return 1
        if springs[col + grp] in [unknown, working]:
            # check we have a valid sep after our group
            # preprocessing reduced all contiguous '.' to singlular '.'
            # guaranteeing that the sp after possible '.' must be possible '#'
            if row > 0:
                # retrieve from row above, [grp + 1] indices to the right
                # the +1 fixes spring to be '.', if it is '?'
                return dp[row - 1][col + grp + 1]
            return 1
        # all others are not valid, e.g. the required sep
        # char is '#'
        return 0

    # initialize dp[] to zeroes
    dp = [[0 for _ in range(len(springs))] for _ in range(len(grps))]
    grp_curr = []
    # start from top right towards bottom left
    for row in range(len(grps)):
        # starting point depends on the groups being checked
        grp = grps.pop()
        grp_curr = [grp] + grp_curr
        start_idx = len(springs) - (sum(grp_curr) + len(grp_curr) - 1)
        end_idx = sum(grps) + len(grps) - 1
        logger.debug(f"row {row}\tgroup {grp}\tstart {start_idx}\tend {end_idx}")
        # iterate from right
        for col in range(start_idx, end_idx, -1):
            if (spring := springs[col]) == working:
                logger.debug("working")
                # carry over from prev cell (on the right)
                dp[row][col] = count_working()
            elif spring == broken:
                logger.debug("broken")
                cell = count_broken()
                dp[row][col] = cell
            else:
                # if '?', add both
                logger.debug("unknown")
                # if (n_broken := count_broken()) == 0 and dp[row][col+1] > 0:
                dp[row][col] = count_working() + count_broken()
        logger.debug(f"row {row}: {dp[row]}")
    return dp[-1][0]


def main(sample: bool, part_two: bool, loglevel: str):
    """
    ???.### 1,1,3
    .??..??...?##. 1,1,3
    ?#?#?#?#?#?#?#? 1,3,1,6
    ????.#...#... 4,1,1
    ????.######..#####. 1,6,5
    ?###???????? 3,2,1
    """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    tstart = time_ns()
    num_arrngs = 0
    cache = {}
    diffs = []
    for line in read_line(fp):
        springs, grps = line.split()
        grps = [int(n) for n in grps.split(",")]
        if part_two:
            springs = "?".join([springs for _ in range(5)])
            grps *= 5
        # remove extraneous '.'
        springs = ".".join(sp for sp in springs.split(".") if sp)
        logger.debug(f"springs: {springs}\tgroups: {grps}")

        n_memo = find_arrangements(springs, tuple(grps), cache)
        n_dp = count_arrng(springs, grps)
        if n_dp != n_memo:
            logger.info(f"dp: {n_dp}\tmemo: {n_memo}\n{line}")
            diffs.append(line)
        # logger.debug(f"total: {num_arrngs} {'='*20}")

    if not sample:
        with open("diffs.txt", "w") as f:
            f.writelines(diffs)
    tstop = time_ns()
    logger.info(f"{num_arrngs}")
    logger.info(f"runtime: {(tstop-tstart)/1e6:.3f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
