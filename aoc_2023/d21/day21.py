#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns
from collections import deque, defaultdict

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


class Node:
    def __init__(self, parent, children) -> None:
        self.parent = parent
        self.children = children
        self.visited = False


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def dfs_nsteps(
    grid: list,
    visited: set,
    plots: set,
    node: complex,
    depth: int = 0,
    n_steps: int = 6,
):
    """
    Searches for all nodes
    """
    # label node as _discovered_ at depth=n_steps
    # f = input()
    logger.debug(f"checking {node}\tdepth: {depth}")
    if depth == n_steps and node not in visited:
        visited.add(node)
        logger.debug(f"adding {node}\t{len(visited)} nodes found")
        return
    # diving for more nodes
    for plot in [node + direc for direc in [-1, 1j, 1, -1j]]:
        if plot in plots and depth < n_steps:
            # check boundary
            # only check for visited when adding n_step nodes
            # check for n_steps
            dfs_nsteps(grid, visited, plots, plot, depth=depth + 1, n_steps=n_steps)

    return visited


def bfs_nsteps(plots: set, root: complex, n_steps: int):
    """
    Find all potential landing nodes in n_steps by finding shortest
    paths to all nodes, and checking for parity
    """
    logger.debug(f"root: {root}\tn_steps: {n_steps}")
    queue = deque([root])
    visited = set([root])
    parents = defaultdict(list)
    while queue:
        node = queue.popleft()
        # n_steps - 1: root is included in parents,
        # so len(parents[node]) = 1 @ step 1
        # step = 4 when len = 4; child nodes are 5th step; allow enqueue
        # step = 5 when len = 5; do not allow further enqueues
        enqueue = True if len(parents[node]) < n_steps - 1 else False
        logger.debug(f"visiting {node}; further enqueue {enqueue}")
        for plot in [node + direc for direc in [-1, 1j, 1, -1j]]:
            if plot not in visited and plot in plots:
                # 1 do not revisit
                # 2 check for boundary and rocks
                # 3 check depth
                visited.add(plot)
                parents[plot] = parents[node] + [node]  # same as append
                if enqueue:
                    # only continue if n_step not reached
                    queue.append(plot)
                logger.debug(f"checking {plot}\tparents: {parents[plot]}")
        # f = input()
    return parents, visited


def main(sample: bool, part_two: bool, loglevel: str, plot=".", rock="#", start="S"):
    """ """
    logger.setLevel(loglevel)
    if sample:
        fp = "sample.txt"
        n_steps = 6
    else:
        fp = "input.txt"
        n_steps = 64
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    # read input
    grid = [line.strip() for line in read_line(fp)]
    plots = set(
        [
            col + row * 1j
            for row, line in enumerate(grid)
            for col, ch in enumerate(line)
            if ch == plot
        ]
    )

    logger.debug(f"plots loc:\n{plots}")
    src = [
        col + row * 1j
        for row, line in enumerate(grid)
        for col, ch in enumerate(line)
        if ch == start
    ][0]
    # starting point is also plot
    plots.add(src)
    logger.debug(f"start: {src}")
    visited = set()

    # execute
    tstart = time_ns()
    # dfs_nsteps(grid, visited, plots, src, n_steps=n_steps)
    parents, visited = bfs_nsteps(plots, src, n_steps)
    parity = n_steps % 2
    targets = [p for p, lineage in parents.items() if len(lineage) % 2 == parity]

    # output
    visited = targets
    logger.debug(f"visited:\n{visited}")
    logger.info(f"num nodes: {len(visited)}")
    # for row in range(len(grid)):
    #     line = ''
    #     for col in range(len(grid[0])):
    #         if (node := col + row * 1j) in visited:
    #             line += 'O'
    #         elif node not in plots:
    #             line += rock
    #         elif node == src:
    #             line += 'S'
    #         else:
    #             line += plot
    #     print(line)
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
