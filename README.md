# Advent of code 2023

## day 1

### day 1 p1

check if each char is numeric from left to right; break once we find it.

To find the last one, reverse the char order in the line

### day 1 p2

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
- small but important distinction on our adjacency check:

```py
adj_part = [
    int(num.group(0))
    for num in nums
    if (num.start() - 1 <= gear.start() <= num.end())
]
```

- checks whether our singular `*` is within the adjacency bounds of our numbers instead

## day 4

### d4 part 1

simple parsing and list comprehension

### d4 part 2

the puzzle description is a trip.

- number of matches in a card now generates that same number of cards, following the card number
- we now want to calculate total number of cards we end up with
    - no longer need to take `power(2, num_common)`
- count matches per card, same as part 1
    - keep a dict: `{card_id: num_common}`
- key is `card_id`
- given the `match_dict`, iterate through each card_id,
- add `match_dict[new_card]` to total count for each `new_card` won
- update based on card count

```py
# nested comprehension with unpacking assignment
match_dict = {
    cid: dict(matches=num_common, count=1)
    for cid, num_common in
    [count_common_num(line) for line in read_line(fp)]
}

# alt that checks for None from count
match_dict = {
    cid: dict(matches=num_common, count=1)
    for cid, num_common in
    (result for result in (count_common_num(line)
    for line in read_line(fp)) if result is not None)
}
```

## day 5

### d5 part 1

problem description is also wild.

Begin with a list of seeds

Input includes a series of maps describing where to plant the seeds. The last of the series arrive at `location`

Each map is a list of 3-tuples: (`dest_start`, `src_start`, `len`). Given `seed-to-soil` of `50 98 2', this maps seeds `98, 99` to soil `50, 51`. Once we decipher all the maps, we start with our initial seed numbers and follow through the maze. If any `src` numbers were not mapped to a `dest`, it remains the same number

Find the lowest location number corresponding to *any* of the initial seed numbers.

So we could iterate through the maps and create a single map with which to look up our initial seed numbers:

- take a map
- note the `src` and `dest` in map names
- populate a `dict={src_loc: dest_loc}` based on each entry in the map
- combine dicts from each line for an overall dict representing the map
- in parallel, create a linked list in a dict representing the direction of the maps, i.e. `map_link = {seed: soil, soil: fertilizer, fertilizer: water, ...}`
    - aka a directed acyclic graph
- for each subsequent map, update the `dest_loc` if `dest_loc` shows up in the new map's `src_loc`
    - does this require reverse lookup?
    -
- alt. jump through each dicts for each seed
- `seed-to-soil` dict be a nested dict:

    ```py
    seed_map['seed'] = {'dest': 'soil', 'path': {src0: dest0, src1: dest1, ..., srcn: destn}}
    ```
- lookup for each initial seed will look like

    ```py
    seed_loc = [s0, s1, ..., sn]
    for seed in seed_loc:
        new_loc = loc if (loc := seed_map['seed'].get(seed)) else seed

### non-naive approach

let's apply some basic heuristics

given `src = 98`, `dest = 50`, `rng = 2`, and a seed of `99`, we might do the following

- check if our seed falls within range of `[src, src + rng)` (notice the incl/excl bracket/parenthesis)
- if no, we do not apply mapping
- if yes, apply mapping
    - define `mapping = dest - src`, then `new_loc = loc + mapping`
    - `new_loc = 99 + 50 - 98 = 51`
- do we need to keep track of remapped location that are initially not used?
    - no we only need to know where our seeds are

#### Algorithm

- parse seeds
- skip all lines that are not map entries
- for each `map_entry`, iterate through seeds to get new loc

I missed the part where each record for "map" is unique, in that I should only apply the mapping once for `src-to-dest` map. I should not apply all the mappings to each seed in a single map.

- collect all the entries for a given map
- send to `apply_mapping` as a collection of entries
- check which entries are applicable to our seeds before relocating

### part 2

- Consider seed start and range
- consider each mapping
- if mapping applies, move the start
- depending on the mapping and range, break off new seed start/range to check against mapping
- repeat for each mapping
- repeat for each seed
- repeat for each set of map

#### solution

we're working with ranges now for seeds as well. Difference is that we have to check which parts of the seed range apply to which entry in the mapping

for one seed, we check that one loc against all the entries of a map. For a range of seeds we compare a range against a range. e.g. given (79, 14), and a map range of (70, 20), only seed locs from 79-89 will be affected.
    - determine relevant range using intersections of `[start, start+len)`
        - `[i_start, i_rng) = if (rng_start <= seed_start < rng_start + rng):
    - calculate the new range first:
        - i_start = max(s_start, start)
        - i_end = min(s_end, end)
    - if `i_start > i_end`, then the intersection does not actually exist and we do not apply this mapping
    - if not, intersection exists and we apply to `[i_start, i_end]
    - if there are remaining seed blocks, we treat this as another set of seeds, since they have been separated from the earlier block.
        - append this block to the end of our seed list, and check for mappings accordingly
- side note, approaching this problem from reverse doesn't seem that feasible given not all the mappings always apply; following mappings backwards will miss seeds where no mappings were applicable

## day 6

### part 1
- number of different scenarios: however much time we're allotted, plus 1:
    - given sample time of 7 ms, we have 8 scenarios, one for each duration of time we charge the boat, including zero
- realistically we don't consider those times since the boat will not move for either, so we have n_realistic = t_alloted - 1
- given t_alloted, if we charge for `t_charge`, the boat will travel at `v = t_charge` for `t_allotted - t_charge`
- `d = v * t = t_charge * (t_allotted - t_charge) = t_a * t_c - t_c^2`- as suspected we have a downward parabola
- given the distance to beat is `9`, question can be framed as how many `t_charge` satisfies `t_a * t_c - t_c^2 > d_record` or `-t_c^2 + t_a * t_c - d > 0`?
- solve the quadratic roots. given roots `x0`, `x1`, then `n_soln = abs(x1 - x0) - 1`
- in the example, we solve for the quadratic $-t^2 + 7t - 9 = 0$- $t^2 - 7t + 9 = 0$
- if any roots are perfect integers, subtract our `n_soln` by 2, since those integer values will perfectly match the distance to beat, and so will not count as solutions that beat the time

### part 2

turns out instead of multiple races, there's just one race. one time, and one distance to beat. take out the spaces between the supposed *different* races.

Bigger number, but our approach still works.

## day 7 - poker hands

given a column of poker hands, along with a column of bid amounts, find the rank of those hands, 1 being lowest, multiply by their bid, then sum to find the answer

### problem considerations

- how to compare between `A` and `9`, or `A` and `K`?
    - use custom func for comparison?
- how to compare different poker hands?
    - first, define the poker hands
    - count the char in hands
    - iterate through the hand, and collect cards as dict keys, count as values
    - better yet use `collections.Counter`, subclass of dict
    - `Counter('22333')` already counts everything
    - check for `.values()`
        - if len(c.keys()) == 2, check for 4-of-a-kind or full house
            - 4: if 4 in c.values()
            - else: full house
        - elif 3 in c.values(): 3-of-a-kind
        - elif len(c.keys()) == 3: 2 pairs
        - elif len(c.keys()) == 4: 1 pair
        - else: high card
- sort
    - after defining hand type and card type, we need to sort all the hands to get the overall hand rank
    - define a func that returns 1, 0, or -1 depending on a > b, a = b, or a < b
    - use `functools.cmp_to_key` and `sorted`

### part 2 - jokers

`J` now act as wild cards that act as whichever card makes the strongest hands. Individually they act as the weakest, lower than 2

This changes the following

- hand eval: `J` now counts towards whichever card has the highest counter
    - in case of two pairs, it doesn't matter which one, since the tie-breaker will go to individual card comparison
    - in case `J` is the most common, donate to the next most common
    - `del hand['J']` afterwards
- card eval: change `J` to `1`
- edge case: if all cards are jokers, do not change the hand

If we considered all poker hands, i.e. straights, flushes, etc. this would be much more tedious

## day 8

### part 1 - left-right pathfinding

So the directions are already listed at the top of the input; we're meant to follow them, starting with `AAA`. To follow the nodes, we look at the two nodes after `=`, and select the left or the right one

use `itertools.cycle` to create an indefinite loop over the finite `dirs` given

```py
dirs = 'LRL'
dir_cycle = cycle(dirs)
while True:
    new_dir = next(dir_cycle)
```

### part 2 - ghosts

start from all nodes that end with `A`, and stop when all nodes end with `Z`

For each node that starts with `A`, count how many cycles it takes to land on something with `Z`. Given the cycles for all nodes, find the LCM to determine number of cycles it takes for *all* routes to end on `Z`s

This assumes perhaps very naively that all routes encounter only one node that end with `Z`

## day 9 - nth differences

### polynomial

Each line is a series of points on some nth degree polynomial curve. Using those points, determine the next point

### part 2 - predicting the past?!

instead of the *next* point, determine the value *prior to the first*

## day 10 - find the farthest point

find 'S' pos. pipes could only connect n/e/s/w, so check the 4 adj squares

- `-`: `-` on east/west; `F`, `L` on west only, `7`, `J` on east only
- `|`: `|` on north/south; `J`, `L` on south only, `7`, `F` on north only
- `F`: east/south; `-`, `7`, `J` on east, `J`, `L` on south
- `7`: south/west; `-`, `F`, `L` west, `J`, `L` south
- `J`: north/west; `-`, `F`, `L` west, `7`, `F` north
- `L`: north/east; `-`, `7`, `J` on east, `7`, `F` north
- `S`:
    - north: `|`, `7`, `F`
    - east: `-`, `7`, `J`
    - south: `|`, `J`, `L`
    - west: `-`, `F`, `L`

Use these characteristics to group pipes

- open dirs
- pipes which fit in that dir

e.g. `-` is open on east and west. so for east, we check whether that pipe is any one that accepts *west* as entry:
- `-`
- `7`
- `J`

so we have `dict` for each pipe that provides a list of open dirs:

```py
# replace - and | with letters since they're operators in python
pipe_open = dict(
    h=[1, -1],
    v=[-1j, 1j]
)
```

Use imaginary `j` to denote coordinates

Plus another dict for each `dir` containing compatible pipe shapes

To find the furthest point, follow any of the two paths from `S` until it returns to origin, count number of steps, and divide that by two; the number will be even.

- start at S
- evaluate each dir to see that node is a compatible pipe
    - there will be two paths that start from S
    - follow the first starting from north
- return the pipe shape and pos
- increment step counter
- is the new pipe shape `S`?
    - if yes, return step counter
    - if not, return to step 2
    - remember which direction we came from, so we don't check that direction, and end up in infinite loop

### part two - enclosed area

How to determine if a point is inside our loop?

- shoelace algorithm
- count the number of borders; whether the next node counts as in or out depends on if that number is even or odd
- expand the resolution so that the gaps can be computed
    - ???

Let's go with 2 since that one is more intuitively understood.

- Start with our bounding box by taking the min/max of x and y
    - we start each loop potentially on the border pipe
- odd number of pipe triggers the count
- even turns off the count

This requires our initial pathfinding to record the `pos` of each pipe, which is trivial. It also requires us to scan both vertically *and* horizontally. This means recording all the hits from one scan, and cross-reference it with the other, perhaps using `set()` and then taking `len()`

Not really working the way I expected.

## day 11

- `.` is empty space
- `#` is a galaxy
- shortest path between *every pair* of galaxies
    - e.g. with 9 galaxies we have 36 unique pairs
    - find the shortest path between each unique pair
- space expands
- *only some space* expands: col/rows with no `#` are actually twice is large
    - twice is large = doubled rows or doubled cols
    - row expands downward
    - col expands rightward
- use manhattan distance
    - up/down/left/right
- sample soln: 374 for all 36 pairs

### path finding??

Given we know the coordinates of start/end, we do not need to use actual path finding to determine the distance. First take care of the empty space expansion

### part two - bigger empties

each empty is actually one million times larger instead of just double. Easy modification to how I expand the rows/columns. I did get tripped up by the -1. The `mult` in part 1 was actually `2` but because I forgot to -1, it still worked when I left `mult=1`

### insights

`itertools.chain.from_iterable()` to flatten one level of iterables, and `itertools.product` to generate permutations of pairs

## day 12 - damaged springs

- `?` - unknown
- `.` - operational
- `#` - rosak
- sequence of numbers: size of each contiguous group of damaged springs
    - e.g. 1,1,3
    - three groups, 1, 1, and 3
    - each surrounded by at least 1 `.`
    - those surrounding `.` may overlap with other groups'
- for each row, find how many possible arrangements exist, given the sequence and diagram

### brute-force

- there is a finite number of combinations the `?` could be
- substitute one with `.`, and also with `#`; collect all combinations
- check how many are valid based on the conditions

### line validation

- inputs: sequence of `.` and `#`, and list of `int`s indicating contiguous groups of `#`, *in that order*

### returning unnested flat list from recursion

- base case: `return [item]`
- else: `return new_list.extend(recursive_func(args))`

### part 2 - unfolding

ok.

## day 13 - reflections and more `.` and `#`

Find the point of reflection in each pattern; patterns are 2D arrays separated by newlines.

- start row-wise
- check if current row, `r` is same as prev row, `r-1`
- if yes, iterate to `r+1`, and then compare that to `r-2`
- continue either one end runs out, or one of the pairs do not equate
- transpose array and go through row-wise again to find reflecting column

### part 1 - 2d arrays with complex coordinates

Given `list[str]`, how do we *transpose* the array?

```py
def transpose(pattern: list[str]) -> list[str]:
    """
    The "".join() keeps it as a list of str
    """
    return ["".join([row[i] for row in pattern]) for i in range(len(pattern[0]))]
```

### part 2 - smudge

Find the `.` or `#` that when flipped, produces a *different* reflection line. This means that instead of checking each pattern once, we're checking it for potentially as many nodes per pattern

## day 14 - total load

More 2D arrays.

- `O` - rollable rocks
- `#` - barriers
- `.` - empty space

Given puzzle input, tilt the array north, so that all `O` moves north until it's either stopped by the edge, a barrier, or another rock. Calculate load, as determined by distance from bottom row. If array has 10 rows, then each `O` on top row
has `load = 10`; bottom row `O` has `load = 1`

- Since we're tilting north, consider row by row, starting from the *second* row
- then consider node by node, and keep moving north until blocked by edge, barrier, or another rock

### part 2 - spin cycle

- north -> east -> south -> west is one cycle
- spin for 1e9 cycles
- calculate load
- **cycle detection**
- encapsulate the *tilt* into a function
- write `transpose`, then feed into `tilt`
    - what does transpose look like?
    - not much of a transpose, more of a `rotate`
    - what does `rotate` look like?
    - should I integrate that into `tilt` instead?
- how does `tilt` with direction look like?
    - default pulls north
    - for `rock`, look for any barriers/rocks *north*, and return the new coordinate at the edge
    - north: new col, move up
    - south: new row, move down
    - okay let's rotate instead
- rotate
    - take node map, size of grid, e.g. 4 rows x 5 cols, and the rotation target
    - east: rotate CW 3x; south: 2x; west: 1x
    - since we're doing east first, we should rotate CCW
    - given row 4, col 3: `2+3j` in a 4 x 5 grid:
        - CCW 1: `3 + (nrows-2)j = 3 + (4-2)j = 3 + 2j`
            - new grid size: 5 rows x 4 cols
        - CCW 2: `2 + (nrows-3)j = 2 + (5-3)j = 2 + 2j`
            - new grid size: 4 rows x 5 cols, again
        - CCW 3: `2 + (nrows - 2)j = 2 + (4-2)j = 2 + 2j`
            - new grid size: 5 rows x 4 cols
        - CCW 4: `2 + (nrows - 2) = 2 + (5-2)j = 2 + 3j
    - `ccw_coord = pos.imag + (nrows - pos.real)j`
    - sorry, *west* first, so rotate CW; given same point and grid:
        - CW1: `0+2j = (nrows - 3 - 1) + 5j = (nrows - pos.imag - 1) + pos.real * 1j`
            - ncol = nrows = 4
            - nrows = ncols = 5
        - CW2: `(nrows - 2 - 1) + 0j = 5 - 2 - 1 + 0j = 2 + 0j`
    - switch nrow/col after each change
- after each spin, cache the north beam load?
    - or cache the *hash* of our node map, to be used for cycle detection
    - avoid calculating load unnecessarily
- `dict` is not hashable; not compatible with `@cache`
    - switch to namedtuple?
    - `frozenset` to not reinvent the wheel
    - `list` to `tuples`
    - point is *immutability*

### immutable namedtuples

- `node_map` becomes tuple of namedtuple
- each node has these attr:
    - idx
        - not needed
    - shape
    - pos
- updating: convert to list, remove original, add new

### `@cache`

not seeing real gains from sample input, from 10 - 10000 cycles: 26 - 20872 ms. Need to implement cycle detection

### cycle detection

Save the load from each cycle and wait for a repeat

Takes 5 minutes to calculate 100 cycles.

### optimiztions

since we're moving rocks north, we should iterate on each column instead, and keep track of the *next available slot*

## day 15 - HASH

- get ascii code lookup
    - use `ord()` built-in func to retrieve ascii code
- start at 0
- increase by char's ascii
- mult 17
- mod 256
- input is comma separated
- sum the HASH for each entry

### part ii - focusing power

this one is a doozy
