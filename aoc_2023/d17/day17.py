#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from dataclasses import dataclass
from collections import defaultdict, deque
from math import inf
from time import time_ns

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


@dataclass
class Node:
    pos: complex
    entry: complex
    n_dir: int = 0  # init to 1 when creating child nodes

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
        return hash((self.pos, self.entry, self.n_dir))

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

    def __repr__(self) -> str:
        return f"pos: {self.pos}\tentry: {self.entry}\tndir: {self.n_dir}"


def heat_loss_dijkstra(
    grid, src=0 + 0j, min_blocks: int = 0, max_blocks: int = 3, part_two: bool = False
):
    """
    Given weighted 2d grid, find the path with minimal heat loss using
    dijkstra

    Params
    ------
    grid: list[str]
        2d array of heat loss
    src: complex
        uses imag plane to denote rows; real for columns
    min_blocks: int >= 0
        minimum number of nodes moved per direction after turning
    max_blocks: int >= 1
        max number of nodes moved per direction before turning

    Returns
    -------
    loss: int
        heat loss of the optimized path
    """

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
    # target @ bottom right corner
    target = ncols - 1 + (nrows - 1) * 1j
    to_check = [src]
    dirs = [-1 + 0j, 1 + 0j, 1j, -1j]
    while to_check:
        # retrieve node with min dist[node]
        to_check = sorted(to_check, key=lambda node: dists[node], reverse=True)
        curr = to_check.pop()
        if curr in visited:
            continue
        if curr.pos == target:
            logger.info(f"potential target found: {dists[curr]}")
            if part_two:
                if curr.n_dir < min_blocks:
                    # not enough to satisfy min movements;  discard
                    continue
                else:
                    # due to our sorting (aka priority queue) the target
                    # that comes up is necessarily the shortest dist
                    # targets.append(curr)
                    # logger.info(f"{len(targets)} potential target saved")
                    return dists[curr]
            else:
                # part 1
                node = curr
                route = deque()
                if prev[node] or node == src:
                    while node:
                        route.appendleft(node.pos)
                        node = prev[node]
                logger.info(f"route: {route}")
                return dists[curr]
        # logger.debug(f'{"-"*30}\ncurrent node: {curr}: {grid[curr.imag][curr.real]}')
        # check adjacent nodes
        for dir in dirs:
            # logger.debug(f"checking dir {dir}")
            # no reverse
            if prev[curr] is not None and dir == prev[curr] - curr:
                logger.debug("next; reverse")
                continue
            # max moves in a row
            if dir == curr.entry and curr.n_dir >= max_blocks:
                logger.debug("next; too many in a row")
                continue
            # min moves in a row
            if curr != src and dir != curr.entry and curr.n_dir < min_blocks:
                # src has dir=0j
                logger.debug("next; not enough in a row")
                continue
            if dir == curr.entry:
                # increment n_dir; assign before using dists[nx]
                # to maintain same hash
                n_dir = curr.n_dir + 1
            else:
                n_dir = 1
            nx = curr + dir
            # bounds check
            if 0 <= nx.real < ncols and 0 <= nx.imag < nrows:
                # check if new dist is shorter
                nx = Node(nx, dir, n_dir)
                alt = dists[curr] + int(grid[nx.imag][nx.real])
                # logger.debug(f"alt: {alt}\t current dist: {dists[nx]}")
                if alt < dists[nx]:
                    # if so, update dist, prev
                    dists[nx] = alt
                    prev[nx] = curr
                    nx.entry = dir
                    # logger.debug(f"nx: {nx}\tdist: {alt}")
                    if nx not in visited:
                        # this needs to be checked so we do not re-add nodes
                        # that were popped from to_check
                        # logger.debug(f'added to queue')
                        to_check.append(nx)
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
    grid_rows = [line.strip() for line in read_line(fp)]
    grid = [[int(ch) for ch in line] for line in grid_rows]
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
