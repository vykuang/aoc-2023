#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


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
                nx_dir = 1
                split_dir = -1
            if entry_dir not in [-1j, 1j]:
                # split
                nx_dir = 1j
                split_dir = -1j
    logger.debug(f"nxdir: {nx_dir}\tsplitdir: {split_dir}")
    return nx_dir, split_dir


class Beam:
    def __init__(self, direc: complex, pos: complex) -> None:
        self.direc = direc
        self.pos = pos
        self.traversed = set()
        self.nx = None
        self.complete = False

    def __repr__(self) -> str:
        return f"dir: {self.direc}\tpos: {self.pos}\ntraversed: {self.traversed}"

    def check_complete(self, max_x, max_y):
        self.nx = self.direc + self.pos
        if self.nx in self.traversed or not (
            0 <= self.nx.real < max_x and 0 <= self.nx.imag < max_y
        ):
            # loop; within bounds
            self.complete = True

    def traverse(self, grid, max_x, max_y):
        """
        Update dir and pos based on next tile
        Returns another Beam if split

        """
        # calc and validate
        self.nx = self.direc + self.pos
        if self.nx in self.traversed or not (
            0 <= self.nx.real < max_x and 0 <= self.nx.imag < max_y
        ):
            # loop or outside bounds
            self.complete = True
        else:
            # update beam pos
            self.pos = self.nx
            # store traversed tiles if inside bounds
            self.traversed.add(self.pos)
            # update dir based on prior dir and new tile
            tile = grid[int(self.nx.imag)][int(self.nx.real)]
            # Beam obj
            if split_dir := self.update_dir(tile):
                return Beam(split_dir, self.pos)

    def update_dir(self, tile) -> complex:
        split_dir = None
        logger.debug(f"entry: {self.direc}\ttile: {tile}")
        match tile:
            # case '.':
            case "/":
                self.direc = complex(-self.direc.imag, -self.direc.real)
            case "\\":
                self.direc = complex(self.direc.imag, self.direc.real)
            case "-":
                if self.direc not in [-1, 1]:
                    # split
                    self.direc = 1 + 0j
                    split_dir = -1 + 0j
            case "|":
                if self.direc not in [-1j, 1j]:
                    # split
                    self.direc = 1j
                    split_dir = -1j
        logger.debug(f"nxdir: {self.direc}\tsplitdir: {split_dir}")
        return split_dir


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


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
    tstart = time_ns()

    max_x = len(grid[0])
    max_y = len(grid)
    logger.debug(f"size: {max_y} rows x {max_x} cols")
    for line in grid:
        logger.debug(f"{line}")

    travelled = set()
    origin = Beam(direc=1 + 0j, pos=-1 + 0j)
    beams = [origin]
    # stop when all beams reach boundary or loop;
    for beam in beams:
        t0 = time_ns()
        while not beam.complete:
            logger.debug(f'{30*"-"}\n{repr(beam)}')
            split_beam = beam.traverse(grid, max_x, max_y)
            if split_beam and split_beam.pos not in travelled:
                logger.debug(f"new beam: {repr(split_beam)}")
                # handle split beam
                beams.append(split_beam)
        t1 = time_ns()
        logger.info(f"beam time: {(t1-t0)/1e6} ms")
        logger.debug(f"beam complete: {beam}")
        logger.debug(f"num of beams: {len(beams)}")
        travelled.update(beam.traversed)
        # f = input()

    logger.info(f"energized tiles: {len(travelled)}")
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
