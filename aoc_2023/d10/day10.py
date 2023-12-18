#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

# char of each pipe shape; use imag plane to denote north/south
pipe_open = dict(
    # h=[-1, 1],
    # v=[1j, -1],
    F=[1, -1j],
    # 7=[-1, -1j],
    J=[1j, -1],
    L=[1, 1j],
    S=[1j, 1, -1j, -1],
    # insert rest of pipe shapes
)
pipe_open.update({"7": [-1, -1j], "-": [-1, 1], "|": [1j, -1j]})
# compatible pipe shapes for each direction
# shapes belonging to 1j (north) means that if we
# look north, these are the shapes that are compatible
compatible = {
    1j: ["S", "|", "7", "F"],
    1: ["S", "-", "7", "J"],
    -1j: ["S", "|", "J", "L"],
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
    if not sample:
        fp = "input.txt"
    elif part_two:
        fp = "sample2.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    pipe_map = {}
    s_row = s_col = 0
    for y, row in enumerate(read_line(fp)):
        for x, ch in enumerate(row):
            pos = x + y * (-1j)
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
    while not (curr == "S" and step):
        curr, pos_curr, d = find_next_pipe(curr, pos_curr, pipe_map, d)
        if part_two:
            # collect all pos
            path_map.append(pos)
        else:
            step += 1
            logger.debug(f"step {step}\tshape {curr}\tpos {pos_curr}")
    if part_two:
        # iterate over all rows of bounding box
        xs = [int(p.real) for p in path_map]
        ys = [int(p.imag) for p in path_map]
        left_x = min(xs)
        right_x = max(xs)
        top_y = max(ys)
        bot_y = min(ys)
        n_in = 0
        # start from min y -> max y
        # then check for '.' from min x -> min y
        for row in range(bot_y, top_y):
            logger.debug(f"row: {row}")
            logger.debug(
                f"line: {[pipe_map[x + row * (-1j)] for x in range(left_x, right_x)]}"
            )
            inside = False
            for col in range(left_x, right_x):
                pos = col + row * (-1j)
                if (chk := pipe_map[pos]) == "." and inside:
                    n_in += 1
                elif pos in path_map:
                    # flip our count condition
                    logger.debug("flip inside")
                    inside = not inside
                else:
                    next
        logger.info(f"points inside: {n_in}")

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
