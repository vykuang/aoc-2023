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

def parse_rules(line):
    """
    parse sorting rules with format:
        <rule id>{part_comparison:new_rule,...,catchall}
    catchall could be another rule id or R or A
    comparison is one of [xmas], <|>, and some integer
    The ordering of the parsed rules must be maintained
    """
    rule_idx = line.index('{')
    ruleid = line[:rule_idx]
    rules = line[rule_idx + 1: -1].split(',') # the offsets trim the {}
    # look for <, >; otherwise catchall
    for r in rules:
        if (rte_idx := r.find(':')) > -1:
            part = r[0]
            rte = r[rte_idx+1:]
            limit = r[2:rte_idx]
            # next, determine comp op
            if r.find('<') > -1:
                next
            elif r.find('>') > -1:
                next
        else:
            # catchall route



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
    for line in read_line(fp):
        # start parsing rules


    # execute
    tstart = time_ns()

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
