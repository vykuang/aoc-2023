#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def get_dir(entry_dir: complex, tile: str) -> complex:
    """Determine new dir based on tile
    Returns new dir in complex: [1+0j, -1+0j, 1j, -1j]
    """
    # default values
    nx_dir = entry_dir
    split_dir = None
    logger.debug(f"entry: {entry_dir}\ttile: {tile}")
    match tile:
        # case '.':
        case "/":
            nx_dir = complex(-entry_dir.imag, -entry_dir.real)
        case "\\":
            nx_dir = complex(entry_dir.imag, entry_dir.real)
        case "-":
            if entry_dir not in [-1, 1]:
                # split
                nx_dir = complex(-entry_dir.imag, -entry_dir.real)

                split_dir = complex(entry_dir.imag, entry_dir.real)
        case "|":
            if entry_dir not in [-1j, 1j]:
                # split
                nx_dir = complex(-entry_dir.imag, -entry_dir.real)

                split_dir = complex(entry_dir.imag, entry_dir.real)
    logger.debug(f"nxdir: {nx_dir}\tsplitdir: {split_dir}")
    return nx_dir, split_dir


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    grid = [line.strip() for line in read_line(fp)]
    max_x = len(grid[0])
    max_y = len(grid)
    logger.debug(f"size: {max_y} rows x {max_x} cols")
    for line in grid:
        logger.debug(f"{line}")

    origin = [1 + 0j, 0j]  # direction, pos
    beams = [origin]
    travelled = set([0j])
    steps = 0
    while beams:
        # stop when all beams reach boundary;
        for beam in beams:
            logger.debug(f'{30*"-"}\ndir: {beam[0]}\tpos: {beam[1]}')
            # calc next tile for all beams
            nx = beam[0] + beam[1]
            if 0 <= nx.real < max_x and 0 <= nx.imag < max_y:
                # store traversed tiles if inside bounds
                travelled.add(nx)
                # update beam pos
                beam[1] = nx
                # update dir based on prior dir and new tile
                tile = grid[int(nx.imag)][int(nx.real)]
                beam[0], new_dir = get_dir(beam[0], tile)
                if new_dir:
                    logger.debug(f"new beam: {[new_dir, nx]}")
                    # handle split beam
                    beams.append([new_dir, nx])
            else:
                # out of bounds -> beam finished
                logger.debug(f"{beam} out of bound")
                beams.remove(beam)

    logger.info(f"energized tiles: {len(travelled)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
