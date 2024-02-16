#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import namedtuple
from itertools import cycle
from functools import reduce
from math import gcd

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

MapRecord = namedtuple("MapRecord", ["key", "left", "right"])


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def parse_map_entry(line: str) -> dict:
    """
    parse "AAA = (BBB, CCC)" to dict:
    {'AAA': {'L': 'BBB', 'R': 'CCC'}}
    skip re in lieu of effective hardcoding
    """
    k = line[:3]
    l = line[7:10]
    r = line[12:15]
    r = MapRecord(k, l, r)
    return r


def count_cycles(
    start: str, ends, dirs_cycle: cycle, node_map: dict, part_two: bool = False
):
    """ """
    node = start
    counter = 0

    while node not in ends:
        d = next(dirs_cycle)
        logger.debug(
            f'current node: {node}\tL:{node_map[node]["L"]}\tR:{node_map[node]["R"]}, going {d}'
        )
        node = node_map[node][d]
        logger.debug(f"new node: {node}")
        counter += 1
        logger.debug(f"step: {counter}")

    return counter


def lcm(a, b):
    return a * b // gcd(a, b)


def main(sample: bool, part_two: bool, loglevel: str):
    """
    starting at AAA, how many steps tor each ZZZ?
    """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    lines = read_line(fp)
    dirs = next(lines).strip()
    logger.info(f"length of dirs: {len(dirs)}")
    logger.debug(f"dirs: {dirs}")
    next(lines)  # skip empty line
    # node_map = {}
    # for line in lines:
    #     if (parsed := parse_map_entry(line.strip())):
    #         k, l, r = parsed
    #         node_map[k] = {'L': l, 'R': r}

    # node_map = {parsed[0]: {'L': parsed[1], 'R': parsed[2]} for line in lines if (parsed := parse_map_entry(line))}
    node_map = {
        parsed.key: {"L": parsed.left, "R": parsed.right}
        for line in lines
        if (parsed := parse_map_entry(line))
    }
    logger.debug(f"node map: {node_map}")

    dirs_cycle = cycle(dirs)
    if part_two:
        starts = [node for node in node_map if node[-1] == "A"]
        ends = [node for node in node_map if node[-1] == "Z"]
        logger.info(f"num starts: {len(starts)}\tnum ends: {len(ends)}")
        num_cycles = []
        for start in starts:
            num = count_cycles(start, ends, dirs_cycle, node_map, part_two)
            num_cycles.append(num)
            logger.info(f"start: {start}\tnum: {num}")

        n_steps = reduce(lcm, num_cycles)
        logger.info(f"total steps for part 2: {n_steps}")

    else:
        start = "AAA"
        ends = ["ZZZ"]
        counter = count_cycles(start, ends, dirs_cycle, node_map)

        logger.info(f"total steps to reach {ends[0]}: {counter}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
