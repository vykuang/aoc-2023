from pathlib import Path
import argparse


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


def main(use_sample: bool, part_two: bool):
    if use_sample:
        fp = "sample.txt"
    else:
        fp = "input.txt"
    total = 0
    # part 1
    for line in read_line(fp):
        if not part_two:
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
        else:
            # look for each letter
            # if a letter does not match the first of any of these,
            #   skip the next 2
            # at the same time, look for ints; if it appears in the first 3 char,
            # automatically take that
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
            cand1 = cand2 = None
            for i, ch in enumerate(line):
                if ch.isnumeric() and not cand1:
                    if i < 3:
                        digit1 = int(ch)
                    else:
                        cand1 = int(ch)
                # if [ch == digit_str[0] for digit_str in digits_str].any():
                # match ch:
                #     case ['o']

    print(f"total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt("--use_sample", "-s", action="store_true", default=False)
    opt("--part_two", action="store_true")
    args = parser.parse_args()
    main(args.use_sample, args.part_two)
