#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
import time
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

# use tuples of namedtuple for @cache
Node = namedtuple("Node", "idx, shape, pos")


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def make_map(line_iter, rock="O", cube="#", space="."):
    """ """
    node_map = {
        complex(j, i): ch
        for i, line in enumerate(line_iter)
        for j, ch in enumerate(line)
        if (ch == rock or ch == cube)
    }
    # rocks = {i: pos for i, (pos, k) in enumerate(node_map.items()) if k == rock}
    # cubes = {i: pos for i, (pos, k) in enumerate(node_map.items()) if k == cube}
    # node_map = {i: {"pos": k, "node": v} for i, (k, v) in enumerate(node_map.items())}
    node_map
    return node_map


def ccw_rotate(node_map, nrows: int):
    """
    Given 2d coordinate as a complex, and nrows of grid,
    return the new coordinate after rotating 90deg CCW
    new col: row
    new row: nrows - col
    """
    return {
        idx: complex(coord.imag, nrows - coord.real) for idx, coord in node_map.items()
    }


def tilt(node_map, rock="O", cube="#", rock_edge=0, cube_edge=0) -> dict:
    """
    Tilts the node map toward north
    Returns tilted node_map
    """
    # sort rocks by rows so we're always moving the top rocks first
    rocks_sorted = sorted(node_map[rock].items(), key=lambda r: r[1].imag)
    for idx, pos in rocks_sorted:
        rock_edge = 0
        cube_edge = 0
        rock_edges = [
            r
            for r in node_map[rock].values()
            if r.real == pos.real and r.imag < pos.imag
        ]
        if rock_edges:
            rock_edge = sorted(rock_edges, key=lambda r: r.imag)[-1].imag
        cube_edges = [
            c
            for c in node_map[cube].values()
            if c.real == pos.real and c.imag < pos.imag
        ]
        if cube_edges:
            cube_edge = sorted(cube_edges, key=lambda c: c.imag)[-1].imag
        if rock_edges or cube_edges:
            edge = rock_edge if rock_edge > cube_edge else cube_edge
            tilted = edge + 1 if edge < pos.imag - 1 else pos.imag
        else:
            # go to boundary
            tilted = 0

        pos_new = complex(pos.real, tilted)
        logger.debug(f"node pos updated to {pos_new}")
        node_map[rock][idx] = pos_new
    return node_map


def main(sample: bool, part_two: bool, loglevel: str, rock="O", cube="#"):
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
    ncols = len(lines[0])
    logger.debug(f"nrows: {nrows}, ncols: {ncols}")
    node_map = make_map(lines)
    logger.debug(f"map:\n{node_map}")

    logger.debug("tilting")
    if not part_two:
        node_map = tilt(node_map)
    else:
        for i in range(1000000):
            for direc in range(4):
                # tilt first since we're start with north
                tilted = tilt(node_map)
                # then rotate
                rotate_rocks = ccw_rotate(tilted[rock], nrows)
                rotate_cubes = ccw_rotate(tilted[cube], nrows)
                node_map = {rock: rotate_rocks, cube: rotate_cubes}
                # swap nrows/ncols
                temp = nrows
                nrows = ncols
                ncols = temp

    loads = sum([nrows - r.imag for r in node_map[rock].values()])
    logger.info(f"load: {loads}")
    tstop = time.time_ns()
    runtime = (tstop - tstart) / 1e3
    logger.info(f"runtime: {runtime} us")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
