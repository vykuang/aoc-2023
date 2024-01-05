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


@dataclass
class Node:
    pos: complex
    entry: complex
    n_dir: int = 1  # init to 1 when creating child nodes

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
    def imag(self, value):
        raise Exception("read only")

    def __hash__(self):
        return hash((self.pos, self.entry))

    def __sub__(self, other):
        # only works between Nodes
        return self.pos - other.pos

    def __add__(self, other):
        if isinstance(other, Node):
            addend = other.pos
        elif isinstance(other, complex):
            addend = other
        else:
            raise ValueError("Not supported")
        return self.pos + addend


def heat_loss_dijkstra(
    grid, src=0 + 0j, min_blocks: int = 0, max_blocks: int = 3, part_two: bool = False
):
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
    targets = []
    while to_check:
        # retrieve node with min dist[node]
        to_check = sorted(to_check, key=lambda node: dists[node], reverse=True)
        curr = to_check.pop()
        if curr in visited:
            continue
        if curr.pos == target:
            logger.info("potential target found")
            if part_two:
                logger.info(f"n_dir: {curr.n_dir}")
                if curr.n_dir < min_blocks:
                    # not enough to satisfy min movements;  discard
                    continue
                else:
                    targets.append(curr)
                    logger.info(f"{len(targets)} potential target saved")
                    continue

            else:
                node = curr
                route = deque()
                if prev[node] or node == src:
                    while node:
                        route.appendleft(node.pos)
                        node = prev[node]
                logger.info(f"route: {route}")
                return dists[curr]
        logger.debug(
            f'{"-"*30}\ncurrent node: ({curr.real}, {curr.imag}, {curr.entry}): {grid[curr.imag][curr.real]}'
        )
        # check adjacent nodes
        for dir in [-1 + 0j, 1 + 0j, 1j, -1j]:
            # logger.debug(f"checking dir {dir}")
            # no reverse
            if prev[curr] is not None and dir == prev[curr] - curr:
                logger.debug("next; reverse")
                continue
            # min moves in a row
            if curr is not src and dir != curr.entry and curr.n_dir < min_blocks:
                logger.debug("next; not enough in a row")
                continue
            # max moves in a row
            if dir == curr.entry and curr.n_dir >= max_blocks:
                logger.debug("next; too many in a row")
                continue
            nx = curr + dir
            # logger.debug(f"checking node ({int(nx.real)}, {int(nx.imag)})")
            # bounds check
            if 0 <= nx.real < ncols and 0 <= nx.imag < nrows:
                # check if new dist is shorter
                nx = Node(nx, dir)
                alt = dists[curr] + int(grid[nx.imag][nx.real])
                if alt < dists[nx]:
                    # if so, update dist, prev
                    dists[nx] = alt
                    prev[nx] = curr
                    nx.entry = dir
                    if dir == curr.entry:
                        nx.n_dir = curr.n_dir + 1
                        logger.debug(
                            f"n_dir updated; dir: {dir}\tentry: {curr.entry}\tndir: {nx.n_dir}"
                        )
                    if nx not in visited:
                        # this needs to be checked so we do not re-add nodes
                        # that were popped from to_check
                        to_check.append(nx)
                    logger.debug(f"updated dist for node {nx.pos}: {alt}")
            else:
                logger.debug("next; outside or visited")
                continue
        visited.add(curr)
        # logger.debug(f'queue length: {len(to_check)}')
        # f = input()

    if part_two:
        # process our list of targets
        real_target = min(targets, key=lambda t: dists[t])
        return dists[real_target]


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample2.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    # read input
    grid = [line.strip() for line in read_line(fp)]
    # execute
    tstart = time_ns()
    if part_two:
        min_blocks = 4
        max_blocks = 10
    else:
        min_blocks = 0
        max_blocks = 3
    dist = heat_loss_dijkstra(
        grid, min_blocks=min_blocks, max_blocks=max_blocks, part_two=part_two
    )

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
