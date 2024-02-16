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


def count_common_num(line: str):
    """ """
    try:
        card_id, nums = line.split(":")
    except ValueError:
        logger.error(f"problem line: {line}")
        return None
    card_id = int(card_id[5:])
    set1, set2 = nums.split("|")
    # default .split() separator is any whitespace
    # alt using map: set_1 = set(map(int, set1.split()))
    set1 = set([int(num) for num in set1.split()])
    set2 = set([int(num) for num in set2.split()])
    common_num = set1.intersection(set2)
    # logger.debug(f'line: {line}')
    # logger.debug(f'common: {common_num}')

    return card_id, len(common_num)


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

    if part_two:
        # match_dict = {
        #     cid: dict(matches=num_common, count=1)
        #     for cid, num_common in
        #     [count_common_num(line) for line in read_line(fp)]
        # }

        # the additional generator exp result for result... allows filtering for None
        # returned by count_common_num if ValueError (blank line) arises
        match_dict = {
            cid: dict(matches=num_common, count=1)
            for cid, num_common in (
                result
                for result in (count_common_num(line) for line in read_line(fp))
                if result is not None
            )
        }

        # iterate over each card to get match
        for card in match_dict:
            logger.debug(f"card: {card}")
            # since 3.7 dicts are ordered by default
            for cid in range(card + 1, card + match_dict[card]["matches"] + 1):
                match_dict[cid]["count"] += match_dict[card]["count"]

            logger.debug(match_dict)

        total = sum([match_dict[card]["count"] for card in match_dict])
    else:
        # part one
        total = sum(
            [
                2 ** (num_common - 1)
                for line in read_line(fp)
                if line and (_, num_common := count_common_num(line))
            ]
        )

    logger.info(f"total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
