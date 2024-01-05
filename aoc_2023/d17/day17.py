#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from dataclasses import dataclass
from collections import defaultdict, deque
from itertools import groupby
from math import inf
from time import time_ns

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def all_equal(iterable):
    "Returns True if all the elements are equal to each other."
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


@dataclass(eq=False)
class Node:
    pos: complex
    entry: complex
    dir_count: int = 0

    @property
    def real(self):
        # computed attribute via @property
        return int(self.pos.real)

    @real.setter
    def real(self, value):
        # node.real = new_val assignment is already
        # disallowed since this function only raises Exception
        # but this provides a more specific message
        raise Exception("read only")

    @property
    def imag(self):
        return int(self.pos.imag)

    @imag.setter
    def imag(self, val):
        raise Exception("read only")

    def __hash__(self):
        return hash((self.pos, self.entry))

    def __sub__(self, other):
        return self.pos - other.pos

    def __add__(self, other):
        return self.pos + other.pos


def heat_loss_dijkstra(grid, src=0 + 0j, depth_limit=3):
    """ """
    ncols = len(grid[0])
    nrows = len(grid)
    logger.info(f"grid size: {nrows} x {ncols}")
    # mark all vertices as inf (unvisited)
    dists = defaultdict(lambda: inf)
    # dist to source initialize to 0
    src = Node(src, entry=0j)
    dists[src] = 0
    # init all prev to None
    prev = defaultdict(lambda: None)
    visited = set()
    target = ncols - 1 + (nrows - 1) * 1j
    # to_check = [col + row * 1j for row in range(nrows) for col in range(ncols)]
    to_check = [src]
    while to_check:
        # retrieve node with min dist[node]
        to_check = sorted(to_check, key=lambda node: dists[node], reverse=True)
        curr = to_check.pop()
        if curr in visited:
            continue
        if curr.pos == target:
            logger.info("target found")
            # debug
            node = curr
            route = deque()
            if prev[node] or node == src:
                while node:
                    route.appendleft(node)
                    node = prev[node]
            logger.info(f"route: {route}")
            return dists[curr]
        logger.debug(
            f'{"-"*30}\ncurrent node: ({int(curr.real)}, {int(curr.imag)}): {grid[int(curr.imag)][int(curr.real)]}'
        )
        # check adjacent nodes
        for dir in [-1, 1, 1j, -1j]:
            logger.debug(f"checking dir {dir}")
            # no reverse
            if prev[curr] is not None and dir == prev[curr] - curr:
                logger.debug("next; reverse")
                continue
            # max 3 in a row
            last_dirs = [dir]
            depth = 0
            node = curr
            # prev[node] = 0j will skip this section,
            # if not explicitly checking for "is not None"
            while prev[node] is not None and depth < depth_limit:
                last_dirs.append(node - prev[node])
                node = prev[node]
                depth += 1
            if depth == depth_limit and all_equal(last_dirs):
                logger.debug("next; 3 in a row")
                continue
            nx = curr.pos + dir
            logger.debug(f"checking node ({int(nx.real)}, {int(nx.imag)})")
            # bounds check
            if 0 <= nx.real < ncols and 0 <= nx.imag < nrows:
                # check if new dist is shorter
                nx = Node(nx, dir)
                alt = dists[curr] + int(grid[int(nx.imag)][int(nx.real)])
                if alt < dists[nx]:
                    # if so, update dist, prev
                    dists[nx] = alt
                    prev[nx] = curr
                    to_check.append(nx)
                    logger.debug(f"updated dist: {alt}")
            else:
                logger.debug("next; outside or visited")
                continue
        visited.add(curr)
        # f = input()


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
    grid = [line.strip() for line in read_line(fp)]
    # execute
    tstart = time_ns()
    dist = heat_loss_dijkstra(grid)

    # output
    logger.info(f"lowest heat loss: {dist}")
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
