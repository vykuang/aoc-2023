#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
import time
from collections import defaultdict, namedtuple
import re

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Lens = namedtuple("Lens", "label, focal")
Box = namedtuple("Box", "labels, focals", defaults=([], []))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def aoc_hash(step) -> int:
    """
    add ascii val
    mult 17
    mod 256
    Returns the box number
    """
    val = 0
    for ch in step:
        val += ord(ch)
        val *= 17
        val %= 256
    # logger.debug(f"hash val: {val}")
    return val


def remove_lens(boxes, box_num, label):
    """
    Remove lens with the label from specified box
    if exists
    """
    if label in (labels := boxes[box_num].labels):
        logger.debug(f"removing {label} from box {box_num}")
        idx_lens = labels.index(label)
        del boxes[box_num].labels[idx_lens]
        del boxes[box_num].focals[idx_lens]
    else:
        logger.debug(f"label {label} not found in box {box_num}")


def add_lens(boxes, box_num, label, focal):
    """
    Add lens of that label and focal length
    to specified box
    If a lens of same length exists, replace with new label
    """
    logger.debug(f"adding {label}={focal} to box {box_num}")
    if focal in (focals := boxes[box_num].focals):
        logger.debug(f"duplicate focal {focal}; changing labels")
        idx_lens = focals.index(focal)
        boxes[box_num].labels[idx_lens] = label
    else:
        # new lens
        logger.debug("new lens added")
        boxes[box_num].labels.append(label)
        boxes[box_num].focals.append(focal)


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    steps = next(read_line(fp)).strip().split(",")

    tstart = time.time_ns()

    if part_two:
        # aoc_hash gets the box num
        # all steps are formatted as <label><op>[focal length]
        # only `=` op will include focal length
        pattern = re.compile(r"(.*)([-=])(\d{0,1})")
        boxes = defaultdict(Box)
        # iterate through steps
        for step in steps:
            logger.debug(f"step: {step}")
            parts = pattern.search(step)
            label = parts.group(1)
            box_num = aoc_hash(label)
            if parts.group(2) == "-":
                remove_lens(boxes, box_num, label)
            else:
                focal = int(parts.group(3))
                add_lens(boxes, box_num, label, focal)

        # iterate through boxes to find sum
        powers = []
        for box_num, lenses in boxes.items():
            for idx_lens, focal in enumerate(lenses.focals):
                # list of Lens namedtuple
                power = (1 + box_num) * (1 + idx_lens) * focal
                powers.append(power)
        logger.debug(f"boxes: \n{boxes}")
        logger.info(f"sum focal powers: {sum(powers)}")
    else:
        hashes = [aoc_hash(step) for step in steps]

        logger.info(f"sum: {sum(hashes)}")
    tstop = time.time_ns()
    logger.info(f"runtime: {(tstop-tstart)/1e6} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
