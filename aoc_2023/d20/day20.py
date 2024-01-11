#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import deque, namedtuple, defaultdict
from time import time_ns

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Pulse = namedtuple("Pulse", "input state dest")


class Module:
    """
    Basic pulse transmitting module
    """

    # shared amongst modules
    queue = deque()

    def __init__(self, inputs: list = [], dests: list = []) -> None:
        self.inputs = inputs
        self.dests = dests

    def process_pulse(self, pulse: bool, *args, **kwargs):
        """
        Basic process re-emits the same pulse
        """
        Module.queue.extend([Pulse(self.name, pulse, dest) for dest in self.dests])

    def __repr__(self) -> str:
        return f"inputs: {self.inputs}\tdests: {self.dests}"


class Flip(Module):
    """
    Only process LO pulses, which toggles module state,
    and sends out module state
    ignores HI pulse
    Denoted by %
    """

    def __init__(self, inputs: list = [], dests: list = []) -> None:
        super().__init__(inputs, dests)
        self.state = False

    def process_pulse(self, pulse, *args, **kwargs):
        if not pulse:
            # only handle LO
            # flip state
            self.state = not self.state
            super().process_pulse(self.state)


class Conjunction(Module):
    """
    Holds last pulse from each input module
    If last pulse from ALL inputs are HI, output LO
    otherwise, HI
    Denoted by &
    """

    def __init__(self, inputs: list = [], dests: list = []) -> None:
        super().__init__(inputs, dests)
        self._last_inputs = {}

    def process_pulse(self, pulse, inp):
        # update last inputs
        self._last_inputs[inp] = pulse
        # check if all HI > send HI; else LO
        pulse = 1 if all(self._last_inputs.values()) else 0
        super().process_pulse(pulse)


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

    # read input
    network = defaultdict(Module)
    for line in read_line(fp):
        parser = line.strip().replace(",", "").split()
        line_id = parser[0]
        dests = parser[2:]
        match [*line_id]:
            case ["%", *name]:
                new_module = Flip(dests=dests)
            case ["&", *name]:
                new_module = Conjunction(dests=dests)
            case _:
                new_module = Module(dests=dests)
                name = line_id

        network["".join(name)] = new_module

    # update inputs for each conj
    for m in network:
        # append m to input for each dest
        for dest in network[m].dests:
            if isinstance(network[dest], Conjunction):
                network[dest].inputs.append(m)

    logger.debug(f"{network}")
    # execute
    tstart = time_ns()

    src = Pulse("button", False, "broadcaster")
    n_lo = 0
    n_hi = 0
    Module.queue.append(src)
    while Module.queue:
        pulse = Module.queue.popleft()
        if pulse.state:
            n_hi += 1
        else:
            n_lo += 1
        network[pulse.dest].process_pulse(pulse.state, pulse.input)

    # output
    logger.info(f"lo: {n_lo}\thi: {n_hi}")

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
