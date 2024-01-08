#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns
from collections import namedtuple
# from itertools import cycle

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Vertex = namedtuple("Vertex", "pos rgb", defaults=[0j, None])


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def calc_polygon_area(vertices: dict) -> int:
    """
    Given dict of vertices, return the polygonal area using the triangle
    formula
    """
    area = 0
    # put the last node (origin) at first
    # to make the polygon calc more convenient
    vertices[0] = vertices[len(vertices)]
    # iterate until second last, so that [i+1] reaches the last
    for i in range(len(vertices) - 1):
        area += (
            vertices[i].pos.real * vertices[i + 1].pos.imag
            - vertices[i].pos.imag * vertices[i + 1].pos.real
        )

    return abs(area // 2)


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
    vertices = dict()
    perim = 0

    for i, line in enumerate(read_line(fp)):
        line = line.strip()
        if part_two:
            _, _, rgb = line.split()
            rgb = rgb[2:-1]  # trim () and #
            metres = int(rgb[:5], 16)
            direc = int(rgb[-1])
        else:
            direc, metres, rgb = line.split()
        match direc:
            case "U" | 3:
                direc = 1j
            case "D" | 1:
                direc = -1j
            case "L" | 2:
                direc = -1 + 0j
            case "R" | 0:
                direc = 1 + 0
        if vertices.get(i):
            pos = vertices[i].pos + direc * int(metres)
        else:
            pos = direc * int(metres)
        vertices[i + 1] = Vertex(pos, rgb)
        perim += int(metres)
        logger.debug(f"add node {i+1} {vertices[i+1]}")

    # execute
    tstart = time_ns()
    area = calc_polygon_area(vertices)
    interior = area - perim // 2 + 1
    holes_dug = perim + interior
    # output
    logger.info(f"holes: {holes_dug}\tperimeter: {perim}")
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
