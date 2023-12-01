from pathlib import Path


def read_line(fpath: str):
    """Reads the input and yields each line"""
    fpath = Path(fpath)
    with open(fpath) as f:
        yield from f


if __name__ == "__main__":
    # for line in read_input("../tests/sample.txt"):
    #     print(line)
    foo = [line.rstrip() for line in read_line("../tests/sample.txt")]
    print(foo)
