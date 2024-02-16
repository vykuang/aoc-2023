#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Mapping = namedtuple("Mapping", ["dest_start", "src_start", "rng"])
Seed = namedtuple("Seed", ["start", "rng"])


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


def apply_mapping(mappings, seed):
    """
    given src, dest, rng, and seed, return the new seed loc, if changed
    """
    for m in mappings:
        if m.src_start <= seed < m.src_start + m.rng:
            return seed + m.dest_start - m.src_start
    # unchanged if no mappings match
    return seed


def apply_range_mapping(mappings: dict, seeds: set[namedtuple]):
    """ """
    new_seeds = set()
    # while loop allows appending to `seeds`
    while seeds:
        seed = seeds.pop()
        matching_mapping = None
        logger.debug(f"seed_start: {seed.start}\trange: {seed.rng}")
        for m in mappings:
            logger.debug(f"eval mapping: {m}")
            # process until exhausted, since new seeds are added
            i_start = max(m.src_start, seed.start)
            # i_end = i_start + rng; not part of actual range
            i_end = min(m.src_start + m.rng, seed.start + seed.rng)
            logger.debug(f"istart: {i_start}\tiend: {i_end}")
            if i_start < i_end:
                # intersection exists; process the applicable seeds
                logger.debug(f"intersection: [{i_start}, {i_end})")
                new_start = i_start + m.dest_start - m.src_start
                new_rng = i_end - i_start
                new_seeds.add(Seed(new_start, new_rng))
                # append remaining block that was not processed
                # alt block:
                # if seed.start < i_start or seed.start + seed.rng > i_end:
                #     new_rng = seed.start + seed.rng - (i_end if i_start > seed.start else i_start)
                #     seeds.add(Seed(i_end if i_start > seed.start else seed.start, new_rng))

                if seed.start >= i_start and seed.start + seed.rng <= i_end:
                    # seed entirely within map range
                    logger.debug("seed within map; no new seed blocks")
                    next
                elif i_start > seed.start:
                    # break off lower portion for map recheck
                    new_rng = i_start - seed.start - 1
                    seeds.add(Seed(seed.start, new_rng))
                    logger.debug(
                        f"lower portion added to set: ({seed.start}, {new_rng})"
                    )
                else:
                    # break off higher portion
                    new_rng = seed.start + seed.rng - i_end
                    seeds.add(Seed(i_end, new_rng))
                    logger.debug(f"upper portion added to set: ({i_end}, {new_rng})")
                # no longer need to check other mapping; move onto next seed
                matching_mapping = m
                break
        if not matching_mapping:
            # no intersection; add back to seeds list as is
            new_seeds.add(seed)
    return new_seeds


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

    mappings = []
    for line in read_line(fp):
        logger.debug(f"line: {line}")
        match line.split():
            case ["seeds:", *seeds]:
                seeds = [int(seed_loc) for seed_loc in seeds]
                logger.debug(f"int seeds: {seeds}")
                if part_two:
                    # make into pairs of (start, range)
                    # s_rngs = [rng for i, rng in enumerate(seeds) if (i % 2)]
                    # s_starts = [seed for i, seed in enumerate(seeds) if not (i % 2)]
                    # seeds = set([Seed(start, rng) for start, rng in zip(s_starts, s_rngs)])
                    seeds = {
                        Seed(seeds[i], seeds[i + 1]) for i in range(0, len(seeds), 2)
                    }
                logger.debug(f"inits: {seeds}")
            case [map_ids, "map:"]:
                # apply mappings for previous map, if exists
                if mappings:
                    logger.info(f"applying map from {map_src} to {map_dest}")
                    # if part_two:
                    #     seeds = apply_range_mapping(mappings, seeds)
                    # else:
                    #     seeds = [apply_mapping(mappings, seed) for seed in seeds]
                    seeds = (
                        apply_range_mapping(mappings, seeds)
                        if part_two
                        else [apply_mapping(mappings, seed) for seed in seeds]
                    )

                # reset our mapping
                map_src, _, map_dest = map_ids.split("-")
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
                mappings.append(m)
    # handle last case
    if part_two:
        seeds = apply_range_mapping(mappings, seeds)
    else:
        seeds = [apply_mapping(mappings, seed) for seed in seeds]
    logger.info(f"new locs: {seeds}")
    logger.info(f"minimum: {min(seeds, key=lambda s: s[0])}")
    # pprint(seed_map)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
