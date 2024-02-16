#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import deque, Counter
from functools import cmp_to_key, partial

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

# class Hand:
#    def __init__(self, cards: str):
#        self.cards = cards
#
#    def __repr__(self):
#        return self.cards
#
#    def __eq__(self, other):
#        return self.cards == other.cards
#
#    def __ne__(self, other):
#        return self.cards != other.cards
#
#    def __gt


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def get_card_val(c: str, part_two: bool = False) -> int:
    """
    returns the poker card value in int, e.g. K -> 13
    """
    if c.isnumeric():
        return int(c)
    elif c == "T":
        return 10
    elif c == "J":
        if part_two:
            return 1
        else:
            return 11
    elif c == "Q":
        return 12
    elif c == "K":
        return 13
    elif c == "A":
        return 14
    else:
        logger.error(f"not valid card: {c}")
        raise ValueError(f"Not a valid card: {c}")


def is_a_higher_than_b(a, b, part_two: bool = False) -> int:
    """compares them as if they were poker cards"""
    # both are numbers
    a_val = get_card_val(a, part_two)
    b_val = get_card_val(b, part_two)
    try:
        if a_val > b_val:
            return 1
        elif a_val < b_val:
            return -1
        else:
            return 0
    except TypeError as e:
        logger.error(f"problem values: {a}: {a_val} and {b}: {b_val}")


def get_hand_val(hand: str, part_two: bool = False):
    """
    Determines what type of poker hand
    and returns a numeric value (??); stronger hand has higher value
    Assumes hand is str of len 5
    """
    c = Counter(hand)
    if part_two and "J" in c.keys():
        c = use_joker(c)
    if len(c.keys()) == 1:
        # 5-k
        return 7
    elif len(c.keys()) == 2:
        # check for 4-k or FH
        if 4 in c.values():
            return 6
        else:  # FH
            return 5
    elif 3 in c.values():  # 3-k
        return 4
    elif len(c.keys()) == 3:  # 2 pairs
        return 3
    elif len(c.keys()) == 4:  # 1 pair
        return 2
    elif len(c.keys()) == 5:  # high card
        return 1
    else:
        raise ValueError(f"not a valid hand: {hand}")


def compare_hands(a: str, b: str, part_two: bool = False) -> int:
    """Compares to poker hands
    Returns -1 for a < b, 0 for a = b, 1 for a > b
    Used in conjunction with built-in sorted()
    and the functools.cmp_to_key util
    """
    logger.debug(f"compare hands part two: {part_two}")
    val_a = get_hand_val(a, part_two)
    val_b = get_hand_val(b, part_two)
    logger.debug(f"a: {a}\tval: {val_a}")
    logger.debug(f"b: {b}\tval: {val_b}")
    if val_a > val_b:
        return 1
    elif val_a < val_b:
        return -1
    else:
        # same type; compare card by card in order
        logger.debug("equal hand type; check for cards")
        a = deque(a)
        b = deque(b)
        cmp = 0
        while a and b and not cmp:
            card_a = a.popleft()
            card_b = b.popleft()
            cmp = is_a_higher_than_b(card_a, card_b, part_two)
            logger.debug(f"card a: {card_a}\tcard b: {card_b}\tresult: {cmp}")
        return cmp


def use_joker(hand: Counter) -> Counter:
    """
    Modifies to hand so that "J" counts toward whichever
    card is already the most frequent
    Assumes "J" is part of the hand
    """
    mosts = hand.most_common(2)
    if len(mosts) > 1:
        c, n = mosts[0] if mosts[0][0] != "J" else mosts[1]
        hand[c] += hand["J"]
        del hand["J"]
        return hand
    else:
        # all jokers
        return hand


def main(sample: bool, part_two: bool, loglevel: str):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')
    # for line in read_line(fp):
    #    tokens = line.split()
    #    hand = tokens[0]
    #    bid = int(tokens[1])

    all_hands = {
        tokens[0]: int(tokens[1]) for line in read_line(fp) if (tokens := line.split())
    }
    logger.debug(f"hands: {all_hands}")
    if part_two:
        hands = sorted(
            all_hands.keys(), key=cmp_to_key(partial(compare_hands, part_two=part_two))
        )
    else:
        hands = sorted(all_hands.keys(), key=cmp_to_key(compare_hands))
    winnings = sum(all_hands[hand] * (i + 1) for i, hand in enumerate(hands))
    logger.info(f"winnings: {winnings}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
