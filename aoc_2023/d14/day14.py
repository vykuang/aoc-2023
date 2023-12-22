#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import sys
from operator import attrgetter
import time

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def make_map(line_iter, rock="O", cube="#", space="."):
    """ """
    #  node_map = {}
    #  for i, line in enumerate(line_iter):
    #      logger.debug(f'line: {line}')
    #      for j, ch in enumerate(line):
    #          if (ch == rock) | (ch == cube):
    #              logger.debug(f'{ch} found at {i}, {j}')
    #              node_map |= {complex(i, j): ch}
    node_map = {
        complex(j, i): ch
        for i, line in enumerate(line_iter)
        for j, ch in enumerate(line)
        if (ch == rock or ch == cube)
    }
    node_map = {i: {"pos": k, "node": v} for i, (k, v) in enumerate(node_map.items())}
    return node_map


def calc_load(node_map: dict, nrows: int, rock="O") -> int:
    """ """
    rocks = [node["pos"] for node in node_map.values() if node["node"] == rock]
    load = 0
    for r in rocks:
        logger.debug(f"rock: {r}")
        load += nrows - r.imag

    return load


def main(sample: bool, part_two: bool, loglevel: str, rock="O", cube="#"):
    """ """
    logger.setLevel(loglevel)
    if not sample:
        fp = "input.txt"
    else:
        fp = "sample.txt"
    logger.debug(f"loglevel: {loglevel}")
    logger.info(f'Using {fp} for {"part 2" if part_two else "part 1"}')

    # timing
    tstart = time.time_ns()
    # read into mem
    lines = list(read_line(fp))
    nrows = len(lines)
    logger.debug(f"nrows: {nrows}")
    node_map = make_map(lines)
    logger.debug(f"map:\n{node_map}")

    # at each rock, check north
    nodes_sorted = sorted(node_map.items(), key=lambda node: node[1]["pos"].imag)
    logger.debug(f"nodes_sorted: {nodes_sorted[:5]}")
    for idx, node_dict in nodes_sorted:
        pos = node_dict["pos"]
        node = node_dict["node"]
        # check north
        logger.debug(f"idx: {idx}\npos: {pos}\tnode: {node}")
        if node == rock:
            logger.debug(f"checking rock at {pos}")
            # node_map is updated if we find a moveable rock
            # edge = [pos_e for pos_e, node_e in node_map.items() if pos_e.real == pos.real and pos_e.imag < pos.imag].sort(key=attrgetter('imag'))[-1]
            edges = [
                n["pos"]
                for n in node_map.values()
                if n["pos"].real == pos.real and n["pos"].imag < pos.imag
            ]
            logger.debug(f"edges: {edges}")
            if edges:
                # check collision
                edge = sorted(edges, key=attrgetter("imag"))[-1]
                logger.debug(f"edge: {edge}")
                tilted = edge.imag + 1 if edge.imag < pos.imag - 1 else pos.imag
            else:
                # go to array boundary
                tilted = 0

            # update original node_map
            pos_new = complex(pos.real, tilted)
            logger.debug(f"node pos updated to {pos_new}")
            node_map[idx] = {"pos": pos_new, "node": node}

    load = calc_load(node_map, nrows)
    logger.info(f"load: {load}")
    tstop = time.time_ns()
    runtime = (tstop - tstart) / 1e3
    logger.info(f"runtime: {runtime} us")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    opt("--loglevel", "-l", type=str.upper, default="info")
    args = parser.parse_args()
    main(args.sample, args.part_two, args.loglevel)
