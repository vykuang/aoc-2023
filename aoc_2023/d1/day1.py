#!/usr/bin/env python3
from pathlib import Path
import argparse
import re

def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f

def find_first_digit(line: str) -> int:
    for ch in line:
        if ch.isnumeric():
            return int(ch)


def find_str_digit(
        line: str,
        pattern: re.Pattern,
        ) -> list:
    """Find the first and last word from list of re.Patterns
    eightwone should translate to 8wo1; look for first and last valid
    string digits
    note that a line of "sevenine" should parse to 79, and "eighthree" to 83
    This invalidates a 1-to-1 replacement approach, even after taking into
    account ordering
    Need something called "positive lookahead" when scanning regex,
    so that our tokens are not consumed as during the matching process,
    i.e. twone when matched with 'two', the 'o' is not consumed, thus
    giving 'one' the chance to match
    """
    #for p in patterns:
    #    m = p.search(line)
    #    matches.append((m.re, m.start()))
    matches = [(m.re, m.start()) for p in digits_dict.keys() if (m := p.search(line))]
    matches.sort(key=lambda m: m[1])
    # could be None
    match len(matches):
        case 0:
            return None
        case 1:
            return [matches[0][0],]
        case _:
            return matches[0][0], matches[-1][0]


def main(sample: bool, part_two: bool):
    if sample and not part_two:
        fp = "sample1.txt"
    elif sample and part_two:
        fp = "sample2.txt"
    else:
        fp = "input.txt"

    print(f"using file {fp}")
    total = 0
    # part 2
    # oneight -> 1ight, eightwo -> 8wo
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
    # replace with one with 'o1e' to keep the ends
    # this allows 1-1 replacement; sevenine -> s7nn9e;
    # interfaces nicely with solution from part 1
    digits_dict = {s: f"{s[0]}{i + 1}{s[-1]}"
            for i, s in enumerate(digits_str)}
    # the ?=(...) allows positive lookahead; eightwo returns 'eight' and 'two'
    pattern = r'(?=(one|two|three|four|five|six|seven|eight|nine))'

    
    for line in read_line(fp):
        if part_two:
            # determine the first and last occurring string digit
            hits = re.findall(pattern, line)
            for hit in hits:
                line = line.replace(hit, digits_dict[hit])
            
        if sample:
            print(f"original line: {line}")
        #    print(f"edited line: {line}")
            print(hits)
        digit1 = find_first_digit(line)
        digit2 = find_first_digit(line[::-1])
        cal = digit1 * 10 + digit2
        if sample:
            print(cal)
        total += cal

    print(f"total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--sample", "-s", action="store_true", default=False)
    opt("--part_two", "-t", action="store_true", default=False)
    args = parser.parse_args()
    main(args.sample, args.part_two)
