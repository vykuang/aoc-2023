#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
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


def heat_loss_dijkstra(grid, src=0 + 0j):
    """ """
    ncols = len(grid[0])
    nrows = len(grid)
    logger.info(f"grid size: {nrows} x {ncols}")
    # mark all vertices as inf (unvisited)
    dists = defaultdict(lambda: inf)
    # dist to source initialize to 0
    dists[src] = 0
    prev = defaultdict(lambda: None)
    entry = defaultdict(lambda: 0j)
    # dir_count = defaultdict(lambda: 0)
    visited = set()
    target = ncols - 1 + (nrows - 1) * 1j
    to_check = [src]
    while to_check:
        to_check = sorted(to_check, key=lambda node: dists[node], reverse=True)
        curr = to_check.pop()
        # logger.debug(f'current node: {int(curr.imag)}, {int(curr.real)}: {grid[int(curr.imag)][int(curr.real)]}')
        # check adjacent nodes
        for dir in [-1, 1, 1j, -1j]:
            # logger.debug(f'checking dir {dir}')
            # no reverse
            if dir == -entry[curr]:
                # logger.debug('next; reverse')
                continue
            # max 3 in a row
            # this logic is flawed since entry[] is only updated when dist is
            if (
                dir == entry[curr] == entry[prev[curr]] == entry[prev[prev[curr]]]
            ):  # == entry[prev[prev[prev[curr]]]]:
                # logger.debug('next; 3 in a row')
                continue
            nx = curr + dir
            # logger.debug(f'checking node {int(nx.imag)}, {int(nx.real)}')
            if nx == target:
                logger.info("target found")
                dists[nx] = dists[curr] + int(grid[int(nx.imag)][int(nx.real)])
                prev[nx] = curr
                # debug
                node = nx
                route = deque()
                if prev[node] or node == src:
                    while node:
                        route.appendleft(node)
                        node = prev[node]
                logger.info(f"route: {route}")
                return dists[nx]
            # bounds check
            elif 0 <= nx.real < ncols and 0 <= nx.imag < nrows and nx not in visited:
                # check if new dist is shorter
                to_check.append(nx)
                alt = dists[curr] + int(grid[int(nx.imag)][int(nx.real)])
                if alt < dists[nx]:
                    # if so, update dist, prev, entry
                    dists[nx] = alt
                    prev[nx] = curr
                    entry[nx] = dir
                    # logger.debug(f'updated dist: {alt}')
            else:
                # logger.debug('next; outside or visited')
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
