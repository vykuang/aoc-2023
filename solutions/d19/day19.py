#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns
from collections import namedtuple
from functools import reduce

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
            arg = int(r[2:rte_idx])
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


def apply_range_rule(part: dict, rule: list) -> list:
    """
    Apply rules to ranges of the part
    Returns new part ranges based on rule branches

    params
    ------
    part: dict
        {'x': [min, max], 'm':[...], 'a': [...], 's': [...]}
    rule: list
        [Rule(part, op, arg, dest), ...]

    Returns
    ------
    assigned_parts: list
        [{rule_id: {part0}}, ..., {rule_id_n: {part_n}}]
    """
    # parts = {}
    # can't use dict; each rule may have multiple outlets to A or R
    # use list of dict(dest: part)
    parts = []
    for subr in rule:
        if subr.part:
            # not catchall
            logger.debug(f"part: {part}")
            logger.debug(f"rule: {subr}")
            comps = [
                eval(f"{subpart}{subr.op}{subr.arg}") for subpart in part[subr.part]
            ]
            if all(comps):
                # true for both lower/upper; return whole part
                logger.debug(f"both true; send to {subr.dest}")
                parts.append({subr.dest: part})
                break
            elif not any(comps):
                # false for both; next rule
                logger.debug("none true; next rule")
                continue
            else:
                # change only subr.part's values
                split = part.copy()
                # look at the op
                if subr.op == "<":
                    split[subr.part] = [part[subr.part][0], subr.arg - 1]
                    part[subr.part] = [subr.arg, part[subr.part][1]]
                else:
                    # '>'
                    split[subr.part] = [subr.arg + 1, part[subr.part][1]]
                    part[subr.part] = [part[subr.part][0], subr.arg]
                parts.append({subr.dest: split})
                logger.debug(f"split: {split}")
        else:
            logger.debug(f"sending {part} to {subr.dest}")
            parts.append({subr.dest: part})
    logger.debug(f"returning parts:\n{parts}")
    return parts


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
    if not part_two:
        parts = []
    read_rules = True
    for line in read_line(fp):
        # start parsing rules
        # logger.debug(f"line: {line}")
        if not line.strip():
            # empty lines separate rules and parts
            if part_two:
                # read only the rules
                break
            read_rules = False
            continue
        elif read_rules:
            rules |= parse_rules(line.strip())
        else:
            # read parts now
            parts.append(parse_parts(line.strip()))

    # logger.debug(f"rules: {rules}")
    # if not part_two:
    #     logger.debug(f"parts: {parts}")

    # execute
    tstart = time_ns()
    if part_two:
        accept = []
        rule_id = "in"
        part_min = 1
        part_max = 4000
        parts = {rule_id: {letter: [part_min, part_max] for letter in "xmas"}}

        while parts:
            logger.debug(f"\n\nparts to check: {parts}")
            check_parts = {}
            for rule_id, part in parts.items():
                logger.debug(f"applying {rule_id} to {part}")
                new_parts = apply_range_rule(part, rules[rule_id])
                # process 'A' and 'R's; potential multiple A/R per rule
                # use append to keep parts separate
                accept += [list(p.values())[0] for p in new_parts if "A" in p.keys()]
                # removed all A and Rs

                for p in new_parts:
                    check_parts |= (
                        p
                        if ("A" not in p.keys()) and ("R" not in p.keys())
                        else check_parts
                    )
            parts = check_parts
            # f = input()

        # accept: list[dict]
        logger.debug(f"{len(accept)} accepts:\n{accept}")
        # num_poss = reduce(lambda x, y: x * (y[1]-y[0]+1), accept, 1)
        num_poss = 0
        for p in accept:
            num_poss += reduce(lambda x, y: x * (y[1] - y[0] + 1), list(p.values()), 1)
        logger.info(f"num possibilities: {num_poss}")

    else:
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
