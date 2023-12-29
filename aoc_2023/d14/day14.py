#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
import time
from functools import cache
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Node = namedtuple("Node", "pos, shape")


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def draw_map(node_items, nrows: int, ncols: int):
    positions = {n.pos: n.shape for n in node_items}
    lines = []
    for row in range(nrows):
        line = ""
        for col in range(ncols):
            ch = shape if (shape := positions.get(col + 1j * row)) else "."
            line += ch
        lines.append(line)
    return lines


def make_map(line_iter, rock="O", cube="#", space="."):
    """
    Given a grid of rocks, cubes, and spaces,
    return tuple of pos and shape for each rock and cube
    """
    node_map = (
        Node(complex(j, i), ch)
        for i, line in enumerate(line_iter)
        for j, ch in enumerate(line)
        if (ch == rock or ch == cube)
    )
    # node_map = (Node(i, k, v) for i, (k, v) in enumerate(node_map.items()))
    # node_map = {i: {"pos": k, "node": v} for i, (k, v) in enumerate(node_map.items())}
    return tuple(node_map)


@cache
def ccw_rotate(node_items: tuple, nrows: int):
    """
    Given 2d coordinate as a complex, and nrows of grid,
    return the new coordinate after rotating 90deg CCW
    new col: row
    new row: nrows - col
    """
    return tuple(
        Node(pos=complex(n.pos.imag, nrows - n.pos.real), shape=n.shape)
        for n in node_items
    )


@cache
def cw_rotate(node_items: tuple, nrows: int) -> tuple:
    """
    Rotates 90deg CW given tuple of Node containing
    "pos" attribute describing 2D coordinates using
    complex numbers, e.g. 2+3j for element in 2nd col, 3rd row
    (0-based index)
    """
    return tuple(
        Node(pos=complex(nrows - n.pos.imag - 1, n.pos.real), shape=n.shape)
        for n in node_items
    )


@cache
def tilt(node_tuples: tuple, rock="O", cube="#", rock_edge=0, cube_edge=0) -> dict:
    """
    Tilts the node_items toward north

    node_items: node_map.items() = (idx, (Node))
    Returns tilted node_map
    """
    # convert from dict_items to list for mutability
    node_items = list(node_tuples)
    # sort rocks by rows so we're always moving the top rocks first
    # collect only rocks as their Node
    rocks = [n for n in node_items if n.shape == rock]
    # sort rocks by rows
    rocks_sorted = sorted(rocks, key=lambda r: r.pos.imag)
    # iterate through rocks to look for any rocks above it
    for r in rocks_sorted:
        # consider column above each 'rock' using original node_items
        # so that cubes are included
        edges = [
            n.pos.imag
            for n in node_items
            if n.pos.real == r.pos.real and n.pos.imag < r.pos.imag
        ]

        if edges:
            # take the lowest node; [-1] selects the highest .imag
            edge = sorted(edges)[-1]
            # do not check if edge is already above current rock;
            # it's always + 1 anyway
            tilted = edge + 1
        else:
            # go to boundary
            tilted = 0

        pos_new = complex(r.pos.real, tilted)
        # logger.debug(f"node pos updated to {pos_new}")
        node_items.remove(r)
        node_items.append(Node(pos_new, rock))

    return tuple(node_items)


def main(
    sample: bool, part_two: bool, loglevel: str, n_cycles=1000000000, rock="O", cube="#"
):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    # timing
    tstart = time.time_ns()
    # read into mem
    lines = list(read_line(fp))
    nrows = len(lines)
    ncols = len(lines[0].strip())
    logger.info(f"nrows: {nrows}, ncols: {ncols}")
    node_map = make_map(lines)

    logger.debug("tilting")
    if not part_two:
        node_map = tilt(node_map)
        load = sum([nrows - r.pos.imag for r in node_map if r.shape == rock])
    else:
        # save load for each cycle
        past_loads = []
        past_nodes = []
        for i in range(n_cycles):
            for direc in range(4):
                # tilt first since we're start with north
                tilted = tilt(node_map)
                # logger.debug(f'after tilting {direc}:')
                # for line in draw_map(tilted, nrows, ncols):
                #     logger.debug(f'{line}')
                # then rotate
                # node_map = ccw_rotate(tilted, nrows)
                node_map = cw_rotate(tilted, nrows)
                # swap nrows/ncols
                temp = nrows
                nrows = ncols
                ncols = temp
                # logger.debug(f'after rotating CW:')
                # for line in draw_map(node_map, nrows, ncols):
                #     logger.debug(f'{line}')

            # logger.debug(f'after cycle {i+1}:')
            # for line in draw_map(node_map, nrows, ncols):
            #     logger.debug(f'{line}')
            load = sum([nrows - r.pos.imag for r in node_map if r.shape == rock])
            # check for repeat
            node_hash = hash(node_map)
            # if load in past_loads:
            if node_hash in past_nodes:
                n_first = past_nodes.index(node_hash)
                duration = i - n_first
                n_cycling = n_cycles - n_first
                n_remain = n_cycling % duration
                load = past_loads[n_first + n_remain - 1]
                logger.info(
                    f"n_first: {n_first}\tduration: {duration}\tn_remain:{n_remain}"
                )
                break
            else:
                past_nodes.append(node_hash)
                past_loads.append(load)
                # if i+1 % 100 == 0:
                logger.info(
                    f"completed cycle {i+1}\truntime: {(time.time_ns() - tstart)/1e6} ms"
                )

    logger.info(f"load: {load}")
    tstop = time.time_ns()
    runtime = (tstop - tstart) / 1e6
    logger.info(f"runtime: {runtime} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
