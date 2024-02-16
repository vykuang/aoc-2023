#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

# char of each pipe shape; use imag plane to denote north/south
pipe_open = {
    "F": [1, 1j],
    "7": [-1, 1j],
    "J": [-1j, -1],
    "L": [1, -1j],
    "S": [1j, 1, -1j, -1],
    "-": [-1, 1],
    "|": [1j, -1j],
}

# compatible pipe shapes for each direction
# shapes belonging to -1j (north) means that if we
# look north, these are the shapes that are compatible
compatible = {
    -1j: ["S", "|", "7", "F"],  # looking north
    1: ["S", "-", "7", "J"],
    1j: ["S", "|", "J", "L"],
    -1: ["S", "-", "F", "L"],
}


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def find_next_pipe(
    shape, pos, pipe_map, prev_d=None, pipe_open=pipe_open, compatible=compatible
):
    """
    Returns the next compatible pipe shape and position
    pipe_map uses complex num as coordinate keys
    pipe_open[shape] provides which directions are open
    compatible[dir] provides list of shapes that accept entries
    __from__ that dir
    """
    entry = -prev_d if prev_d else None
    for d in [1j, 1, -1j, -1]:
        if d != entry:
            pos_chk = pos + d
            chk = pipe_map.get(pos_chk)
            if chk and chk in compatible[d] and d in pipe_open[shape]:
                return chk, pos_chk, d


def scanrow(left_x, right_x, bot_y, top_y, pipe_map, path_map):
    """
    Returns pos of nodes inside the loop
    """
    # start from min y -> max y
    # then check for '.' from min x -> min y
    inside_nodes = []
    step_y = 1 if top_y > bot_y else -1
    step_x = 1 if right_x > left_x else -1
    for row in range(bot_y, top_y, step_y):
        logger.debug(f"row: {row}")
        logger.debug(
            f"line: {''.join([pipe_map[x + row * (1j)] for x in range(left_x, right_x)])}"
        )
        inside = False
        for col in range(left_x, right_x, step_x):
            pos = col + row * (1j)
            if pipe_map[pos] == "." and inside:
                inside_nodes.append(pos)
            elif pos in path_map:
                # flip our count condition
                logger.debug("flip inside")
                inside = not inside
            else:
                next
        logger.debug(f"running point: {len(inside_nodes)}")
    return inside_nodes


def scancol(left_x, right_x, bot_y, top_y, pipe_map, path_map):
    """
    scan columns from left to right, top to bottom for inside nodes
    """
    inside_nodes = []
    for col in range(left_x, right_x):
        logger.debug(f"col: {col}")
        logger.debug(
            f"line: {''.join([pipe_map[col + y * (1j)] for y in range(bot_y, top_y)])}"
        )
        inside = False
        for row in range(bot_y, top_y):
            pos = col + row * 1j
            if pipe_map[pos] == "." and inside:
                inside_nodes.append(pos)
            elif pos in path_map:
                logger.debug("flip inside")
                inside = not inside
            else:
                next
        logger.debug(f"running point: {len(inside_nodes)}")
    return inside_nodes


def transpose(c: complex) -> complex:
    """
    Treating c as a 2d coord, transpose it
    e.g. 3 - 4j ->  4 - 3j
    """
    return complex(-c.imag, -c.real)


def calc_polygon_area(vertices: list) -> int:
    """
    append the first to complete the formula in one convenient loop
    """
    num_vertices = len(vertices)
    vertices.append(vertices[0])
    area = sum(
        [
            vertices[i].real * vertices[i + 1].imag
            - vertices[i].imag * vertices[i + 1].real
            for i in range(num_vertices)
        ]
    )
    return abs(area / 2)


def main(sample: bool, part_two: bool, loglevel: str):
    """
    Pathfinding?
    Given a map of pipes, find the furthest distance from the start
    F, 7, J, L are elbow pipes
    -: straights
    .: ground
    S: start
    Given pos_s, search each cardinal dir
    for each dir, look for a compatible pipe, given current pipe
    """

    logger.setLevel(loglevel)
    if sample:
        fp = "sample.txt"
    else:
        fp = "input.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    pipe_map = {}
    s_row = s_col = 0
    for y, row in enumerate(read_line(fp)):
        for x, ch in enumerate(row):
            pos = x + y * 1j
            pipe_map |= {pos: ch}
            # find 'S'
            if ch == "S":
                pos_s = pos

    logger.debug(f"origin: {pos_s}")
    curr = "S"
    pos_curr = pos_s
    step = 0
    d = None
    path_map = []
    vertices = []
    while not (curr == "S" and step):
        curr, pos_curr, d = find_next_pipe(curr, pos_curr, pipe_map, d)
        if part_two and curr in "7LJF":
            # collect all pos
            # path_map.append(pos_curr)
            # collect all elbows, i.e. vertices
            vertices.append(pos_curr)
            logger.debug(f"step {step}\tshape {curr}\tpos {pos_curr}")
        step += 1
    if part_two:
        logger.info(f"{len(vertices)} vertices found")
        # find A using shoelace, then i using Pick's
        area = calc_polygon_area(vertices)
        logger.info(f"area: {area}\tstep: {step}")
        interior = area - step // 2 + 1
        # # iterate over all rows of bounding box
        # xs = [int(p.real) for p in path_map]
        # ys = [int(p.imag) for p in path_map]
        # left_x = min(xs)
        # right_x = max(xs) + 1
        # top_y = max(ys) + 1
        # bot_y = min(ys)
        # logger.debug(f"bounding box: {left_x}, {bot_y} to {right_x}, {top_y}")
        # inside_hscan = scanrow(left_x, right_x, bot_y, top_y, pipe_map, path_map)
        # inside_vscan = scancol(left_x, right_x, bot_y, top_y, pipe_map, path_map)
        # logger.debug(f"hscan: {inside_hscan}\nvscan: {inside_vscan}")
        # inside_nodes = set(inside_hscan).intersection(set(inside_vscan))
        # n_in = len(inside_nodes)
        logger.info(f"points inside: {interior - (interior % 1)}")

    else:
        logger.info(f"furthest point: {step//2}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
