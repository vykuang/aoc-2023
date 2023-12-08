#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def gen_seed_map(fpath: str):
    """
    Proved to be hilariously impractical after looking at the real input
    """
    seed_map = {}
    for line in read_line(fp):
        match line.split():
            case ["seeds:", *seeds]:
                inits = [int(seed) for seed in seeds]
                logger.debug(f"inits: {inits}")
            case [mapdir, "map:"]:
                # start looking for records in this map
                # update src and dest
                src, _, dest = mapdir.split("-")
                seed_map[src] = {"dest": dest}

                logger.debug(f"src: {src}\tdest: {dest}")
            case []:
                logger.debug("empty line")
                next
            case _:
                logger.debug(f"map entry line: {line}")
                dest_start, src_start, rng = [int(num) for num in line.split()]
                logger.debug(f"{dest_start}, {src_start}, {rng}")
                map_entry = {
                    src: dest
                    for src, dest in zip(
                        range(src_start, src_start + rng),
                        range(dest_start, dest_start + rng),
                    )
                }
                logger.debug(f"new map entry: {map_entry}")
                seed_map[src].update(map_entry)
    return seed_map


def apply_mapping(mappings, seed):
    """
    given src, dest, rng, and seed, return the new seed loc, if changed
    """
    for m in mappings:
        if m.src_start <= seed < m.src_start + m.rng:
            return seed + m.dest_start - m.src_start
    # unchanged if no mappings match
    return seed


def seed_loc_traverse(
    inits: list[int], seed_map: dict, src: str = "seed", end: str = "location"
):
    """
    requires the impractical seed_map
    """
    seeds = inits
    while src != end:
        # update the locations based on seed map
        # logger.debug(f'seeds: {seeds}')
        new_locs = [loc if (loc := seed_map[src].get(seed)) else seed for seed in seeds]
        # update the source to prior destination
        seeds = new_locs
        src = seed_map[src]["dest"]
    return seeds


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    elif sample and part_two:
        fp = "sample2.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    Mapping = namedtuple("Mapping", ["dest_start", "src_start", "rng"])
    mappings = []
    for line in read_line(fp):
        match line.split():
            case ["seeds:", *seeds]:
                seeds = [int(seed) for seed in seeds]
                logger.debug(f"inits: {seeds}")
            case [_, "map:"]:
                # apply mappings for previous map, if exists
                if mappings:
                    seeds = [apply_mapping(mappings, seed) for seed in seeds]
                # reset our mapping
                mappings = []
            case []:
                #     # needed to use two different 'case' to match either `map:`
                #     # or empty line, since the alt. did not bind any names
                # soln: don't bind any names, and only look for literals
                next
            case _:
                logger.debug(f"map entry line: {line}")
                # dest, src, rng
                m = Mapping(*[int(num) for num in line.split()])
                logger.debug(f"mapping: {m}")
                mappings.append(m)
                # seeds = [apply_mapping(src_start, dest_start, rng, seed) for seed in seeds]
    # handle last case
    seeds = [apply_mapping(mappings, seed) for seed in seeds]
    logger.info(f"new locs: {seeds}")
    logger.info(f"minimum: {min(seeds)}")
    # pprint(seed_map)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
