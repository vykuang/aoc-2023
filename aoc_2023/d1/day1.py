#!/usr/bin/env python3
from pathlib import Path
import argparse


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def main(use_sample: bool, part_two: bool):
    if use_sample and not part_two:
        fp = "sample1.txt"
    elif use_sample and part_two:
        fp = "sample2.txt"
    else:
        fp = "input.txt"

    print(f"using file {fp}")
    total = 0
    # part 2
    digits_str = [
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    ]
    digits_dict = {s: str(i + 1) for i, s in enumerate(digits_str)}
    for line in read_line(fp):
        print(f"original line: {line}")
        if part_two:
            # determine the first and last occurring string digit

            for d in digits_dict:
                line = line.replace(d, digits_dict[d])
            print(f"edited line: {line}")

        for ch in line:
            if ch.isnumeric():
                digit1 = int(ch)
                break
        for ch in line[::-1]:
            if ch.isnumeric():
                digit2 = int(ch)
                break
        cal = digit1 * 10 + digit2
        if use_sample:
            print(cal)
        total += cal

    print(f"total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--use_sample", "-s", action="store_true", default=False)
    opt("--part_two", action="store_true", default=False)
    args = parser.parse_args()
    main(args.use_sample, args.part_two)
