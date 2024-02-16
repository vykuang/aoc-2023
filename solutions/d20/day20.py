#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from collections import deque, namedtuple, defaultdict
from time import time_ns
from functools import reduce

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

Pulse = namedtuple("Pulse", "input state dest")


class Module:
    """
    Basic pulse transmitting module
    """

    # shared amongst modules
    queue = deque()

    def __init__(self, name: str = None, inputs: list = [], dests: list = []) -> None:
        self.name = name
        self.inputs = inputs
        self.dests = dests

    def process_pulse(self, name, pulse: bool, *args, **kwargs):
        """
        Basic process re-emits the same pulse
        """
        Module.queue.extend([Pulse(name, pulse, dest) for dest in self.dests])

    def __repr__(self) -> str:
        return f"inputs: {self.inputs}\tdests: {self.dests}"


class Flip(Module):
    """
    Only process LO pulses, which toggles module state,
    and sends out module state
    ignores HI pulse
    Denoted by %
    """

    def __init__(self, name: str = None, inputs: list = [], dests: list = []) -> None:
        super().__init__(name, inputs, dests)
        self.state = False

    def process_pulse(self, name, pulse, *args, **kwargs):
        if not pulse:
            # only handle LO
            # flip state
            self.state = not self.state
            super().process_pulse(name, self.state)


class Conjunction(Module):
    """
    Holds last pulse from each input module
    If last pulse from ALL inputs are HI, output LO
    otherwise, HI
    Denoted by &
    """

    def __init__(self, name: str = None, inputs: list = [], dests: list = []) -> None:
        super().__init__(name, inputs, dests)
        self._last_inputs = {}

    def add_input(self, inp: str):
        """
        Append to our list of inputs, *and* initialize them in _last_inputs dict
        """
        self.inputs.append(inp)
        self._last_inputs[inp] = 0

    def process_pulse(self, name, pulse, inp):
        # update last inputs
        if inp in self.inputs:
            self._last_inputs[inp] = pulse
        # logger.debug(f'Conj module {name} last inputs: {self._last_inputs}')
        # check if all HI > send HI; else LO
        pulse = 0 if all(self._last_inputs.values()) else 1
        super().process_pulse(name, pulse)


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def main(sample: bool, part_two: bool, loglevel: str, n_cycles: int = 1000):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
        target = "rx"
    else:
        fp = "sample2.txt"
        target = "output"
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
            if dest in network and isinstance(network[dest], Conjunction):
                network[dest].add_input(m)

    # part 2 target inputs are the 4 conj
    # that send to the conjunction before target; last needs to send LO
    # if all *those* inputs are ON then
    target_inputs = ["mp", "qt", "qb", "ng"]
    # target_inputs = ['dx', 'ck', 'cs', 'jh']
    # execute
    tstart = time_ns()

    src = Pulse("button", 0, "broadcaster")
    n_lo = 0
    n_hi = 0
    n_cycles = 0
    target_cycles = []
    while target_inputs:
        if not Module.queue:
            Module.queue.append(src)
            n_cycles += 1
            logger.debug(f"cycle {n_cycles}")
        pulse = Module.queue.popleft()
        logger.debug(f"pulse: {pulse}")
        if pulse.state:
            n_hi += 1
        else:
            n_lo += 1
            if pulse.dest in target_inputs:
                logger.info(
                    f"{pulse.input} -{pulse.state}-> {pulse.dest} at cycle {n_cycles}"
                )
                target_cycles.append(n_cycles)
                target_inputs.remove(pulse.dest)
        network[pulse.dest].process_pulse(pulse.dest, pulse.state, pulse.input)

    # output
    if part_two:
        target_cycle = reduce(lambda x, y: x * y, target_cycles, 1)
        logger.info(f"target cycle: {target_cycle}")
    else:
        logger.info(f"lo: {n_lo}\thi: {n_hi}\tprod: {n_lo * n_hi}")

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
