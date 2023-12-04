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
