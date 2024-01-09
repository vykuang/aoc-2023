#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Rule = namedtuple("Rule", "part op arg dest", defaults=["", "", None, ""])


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
    rule_idx = line.index("{")
    ruleid = line[:rule_idx]
    rules = line[rule_idx + 1 : -1].split(",")  # the offsets trim the {}
    # look for <, >; otherwise catchall
    parsed_rules = []
    for r in rules:
        if (rte_idx := r.find(":")) > -1:
            part = r[0]
            op = r[1]  # use eval
            dest = r[rte_idx + 1 :]
            arg = r[2:rte_idx]
            parsed_rules.append(Rule(part, op, arg, dest))
        else:
            # catchall route
            parsed_rules.append(Rule(dest=r))
    return {ruleid: parsed_rules}


def parse_parts(line):
    """
    parts have the format
        {x=...,m=...,a=...,s=...}
    where ... are integers
    Stored as namedtuples
    """
    return {ch[0]: int(ch[2:]) for ch in line[1:-1].split(",")}


def apply_rule(part: dict, rule: dict) -> str:
    """Apply a set of subrules and return the outcome"""
    for subr in rule:
        if subr.part:
            # not catchall
            if eval(f"{part[subr.part]}{subr.op}{subr.arg}"):
                return subr.dest
            else:
                continue  # next rule
        else:
            return subr.dest  # catchall


def apply_range_rule(part: dict, rule: dict):
    """
    Apply rules to ranges of the part
    Returns new part ranges based on rule branches
    """
    for subr in rule:
        if subr.part:
            # not catchall
            comps = [eval(f"{subpart}{subr.op}{subr.arg}")
                    for subpart in part[subr.part]]
            if all(comps):
                # true for both lower/upper; return whole part
                return part, subr.dest
            elif not any(comps):
                # false for both; next rule
                continue
            else:
                # look at the op
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
    rules = {}
    parts = []
    read_rules = True
    for line in read_line(fp):
        # start parsing rules
        logger.debug(f"line: {line}")
        if not line.strip():
            # empty lines separate rules and parts
            read_rules = False
            continue
        elif read_rules:
            rules |= parse_rules(line.strip())
        else:
            # read parts now
            parts.append(parse_parts(line.strip()))

    logger.debug(f"rules: {rules}")
    logger.debug(f"parts: {parts}")

    # execute
    tstart = time_ns()
    part_sums = []
    for part in parts:
        # follow rules for each part, starting with rules['in']
        rule_id = "in"
        while rule_id not in ["R", "A"]:
            rule_id = apply_rule(part, rules[rule_id])
        if rule_id == "A":
            part_sums.append(sum(part.values()))
            logger.debug(f"accept part {part}\tnew sums: {part_sums}")

    # output
    logger.info(f"sums: {sum(part_sums)}")
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
