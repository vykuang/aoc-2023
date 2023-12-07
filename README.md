# Advent of code 2023

## day 1 p1

check if each char is numeric from left to right; break once we find it.

To find the last one, reverse the char order in the line

## day 1 p2

Wholesale replacement is invalidated by `eightwothree`; the order in which we replace the string becomes critical, and wholesale replacement cannot account for that.

I considered some arrangement that took into account possible overlaps, e.g. `eight` must be replaced before `two`, but `one` makes the ordering irreconcilable. If `eight` is before `two`, then `one` must be before `eight`, however `two` must be replaced before `one`.

Try `re.search`; note that `re.match` only looks at *beginning of string*

```py
import re

inp = 'eightwothree'
p = re.compile('two')
r = p.match(inp)
r.span()[0] # 4
```

Obtaining the `start` allows us to replace the *first* and *last* occurring string digit

Missing calibration: `sevenine`, if that is the whole string, should parse to `79`. This means using **positive lookahead** assertion, so that our tokens are not consumed during match; we need to save the `n` for `nine` to be captured as well.

Use this regex pattern: `?=(one|two|...|nine)`

## day 2

- bag with cubes
    - r/g/b
- find number of cubes, after the elf hides a secret number
- `game id: a blue, b red; c red, d green, e blue; f green`
- three sets are revealed in that game record
- each set is semicolon separated
- given list of game records, and known number of cubes of each colour, find which games are possible
- sum the game IDs of possible games

Contraints:

- 12 red
- 13 green
- 14 blue

### d2 part 1

Check each set vs our constraint?

- for each game
- for each set
- parse each set to get the number of r/g/b
- compare with our constraint
- if any one set does not match, mark as not possible
- else add game ID to total

Compare with constraints:

- collect counts by color for each game_id
- compare the max with our constraint
- if none surpass constraint, then add game_id to total

### d2 part 2

what is the *fewest number of cubes of each color* that make the games possible?

- collect the max for each set, from each game
- get the product of the maximums
- sum the products

## day 3

Given a schematic of numbers, periods, and symbols, find all numbers adjacent (even diagonally) to a symbol, not including periods. Sum those numbers

- Rolling window of 3 rows; for each row, consider also the one above and below, if applicable
- scan each line
- look for `\d+`
- detection of numbers triggers scanning for symbols
    - e.g. when 467 is found on row 0 col 0, with `re.finditer` so that it also returns the position, as opposed to `re.findall` which only returns the string, we get `span=(0, 3)`
    - using this span, we look for symbols in this range:
    - row n-1: -1 to 3
    - row n: -1 **and** 3
    - row n+1 -1 to 3
- symbol detection will collect the range, and search for all symbols
- handle first line as edge case
    - use current as the *look ahead*
- how to handle last line?

Or would it be easier to search for symbols instead, then check for numbers surrounding the symbol? This ensure all numbers found are valid, but requires uniqueness check

*OR*

- sum all numbers
- find all numbers only surrounded by periods, i.e. *not adjacent to any symbols*
- subtract that from total sum to get the answer

### d3 part 2

- gear: any `*` adjacent to exactly two part numbers
- ratio: prod of those two numbers
- find the sum of all gear ratios

this necessitates switching our approach to look for symbols instead of searching for symbols around numbers

- keep using a 3-line rolling window, with empty newline appended to input
- search for `*`
- use the same principles but now we check the start/stop of the numbers vs the position of our `*`
    - given a `*` at position `c` on row `r`, check the following
    - any `\d+` with start *or* stop between `c-1` and `c+1`, in rows `r - 1` and `r + 1`
    - any `\d+` with stop at `c-1` or start at `c+1`
- multiply the two if found
