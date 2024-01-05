#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from time import time_ns

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


class Beam:
    # shared attributes between all Beams
    # access with Beam.traversed
    traversed = set()

    def __init__(self, direc: complex, pos: complex) -> None:
        self.direc = direc
        self.pos = pos
        self.nx = None
        self.complete = False

    def __repr__(self) -> str:
        return f"dir: {self.direc}\tpos: {self.pos}\ntraversed: {self.traversed}"

    def traverse(self, grid, max_x, max_y):
        """
        Update dir and pos based on next tile
        Returns another Beam if split
        """
        # calc and validate
        self.nx = self.direc + self.pos
        if (self.direc, self.nx) in Beam.traversed or not (
            0 <= self.nx.real < max_x and 0 <= self.nx.imag < max_y
        ):
            # loop or outside bounds
            self.complete = True
        else:
            # update beam pos
            self.pos = self.nx
            # store traversed tiles
            Beam.traversed.add((self.direc, self.nx))
            # update dir based on prior dir and new tile
            tile = grid[int(self.nx.imag)][int(self.nx.real)]
            # Beam obj
            if split_dir := self.update_dir(tile):
                return Beam(split_dir, self.pos)

    def update_dir(self, tile) -> complex:
        split_dir = None
        # logger.debug(f"entry: {self.direc}\ttile: {tile}")
        match tile:
            case "/":
                self.direc = -1j / self.direc
            case "\\":
                self.direc = 1j / self.direc
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
        # if logger.isEnabledFor(logging.DEBUG):
        #     logger.debug(f"nxdir: {self.direc}\tsplitdir: {split_dir}")
        return split_dir


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def count_energized(entry_beam, grid, max_x, max_y):
    """
    Given an arbitrary entry beam located at the edge,
    count energized tiles
    """
    # beams = [Beam(entry_dir, entry_pos)]
    beams = [entry_beam]
    for beam in beams:
        while not beam.complete:
            # logger.debug(f'{30*"-"}\n{repr(beam)}')
            # moves beam by one tile; returns split if encountered
            split_beam = beam.traverse(grid, max_x, max_y)
            if split_beam:
                # logger.debug(f'list of splits: {splits}')
                # logger.debug(f"new splits: {repr(split_beam)}")
                # handle split beam
                beams.append(split_beam)
    #     logger.debug("beam complete")
    #     logger.debug(f"num of beams: {len(beams)}")

    # node[1] selects `pos`
    energized = set([node[1] for node in Beam.traversed])
    n_energized = len(energized)
    logger.debug(f"energized tiles: {n_energized}")
    # clear the shared traversed set
    Beam.traversed.clear()
    return n_energized


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

    if part_two:
        # construct list of candidates
        energized = []
        # for col in range(0, max_x):
        #     energized.append((count_energized(Beam(1j, col - 1j), grid, max_x, max_y), col - 1j))
        #     energized.append((count_energized(Beam(-1j, col + max_y * 1j), grid, max_x, max_y), col + max_y * 1j))
        energized = [
            (count_energized(Beam(1j, col - 1j), grid, max_x, max_y), col - 1j)
            for col in range(0, max_x)
        ]
        energized += [
            (
                count_energized(Beam(-1j, col + max_y * 1j), grid, max_x, max_y),
                col + max_y * 1j,
            )
            for col in range(0, max_x)
        ]
        energized += [
            (
                count_energized(Beam(1 + 0j, -1 + row * 1j), grid, max_x, max_y),
                -1 + row * 1j,
            )
            for row in range(0, max_y)
        ]
        energized += [
            (
                count_energized(Beam(-1 + 0j, max_x + row * 1j), grid, max_x, max_y),
                max_x + row * 1j,
            )
            for row in range(0, max_y)
        ]
        # for row in range(0, max_y):
        #     energized.append((count_energized(Beam(1+0j, -1 + row * 1j), grid, max_x, max_y), -1 + row * 1j))
        #     energized.append((count_energized(Beam(-1+0j, max_x + row * 1j), grid, max_x, max_y), max_x + row * 1j))

        most_energy = max(energized, key=lambda b: b[0])
        max_entry = most_energy[1]
        logger.info(f"max: {most_energy[0]}\tentry: {max_entry}")

    else:
        origin = Beam(1 + 0j, -1 + 0j)
        n_energized = count_energized(origin, grid, max_x, max_y)
        logger.info(f"energized tiles: {n_energized}")

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
