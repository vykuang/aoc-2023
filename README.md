# Advent of code 2023

## day 1

### day 1p1

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

--- Day 6: Wait For It ---

The ferry quickly brings you across Island Island. After asking around, you discover that there is indeed normally a large pile of sand somewhere near here, but you don't see anything besides lots of water and the small island where the ferry has docked.

As you try to figure out what to do next, you notice a poster on a wall near the ferry dock. "Boat races! Open to the public! Grand prize is an all-expenses-paid trip to Desert Island!" That must be where the sand comes from! Best of all, the boat races are starting in just a few minutes.

You manage to sign up as a competitor in the boat races just in time. The organizer explains that it's not really a traditional race - instead, you will get a fixed amount of time during which your boat has to travel as far as it can, and you win if your boat goes the farthest.

As part of signing up, you get a sheet of paper (your puzzle input) that lists the time allowed for each race and also the best distance ever recorded in that race. To guarantee you win the grand prize, you need to make sure you go farther in each race than the current record holder.

The organizer brings you over to the area where the boat races are held. The boats are much smaller than you expected - they're actually toy boats, each with a big button on top. Holding down the button charges the boat, and releasing the button allows the boat to move. Boats move faster if their button was held longer, but time spent holding the button counts against the total race time. You can only hold the button at the start of the race, and boats don't move until the button is released.

For example:

Time:      7  15   30
Distance:  9  40  200

This document describes three races:

    The first race lasts 7 milliseconds. The record distance in this race is 9 millimeters.
    The second race lasts 15 milliseconds. The record distance in this race is 40 millimeters.
    The third race lasts 30 milliseconds. The record distance in this race is 200 millimeters.

Your toy boat has a starting speed of zero millimeters per millisecond. For each whole millisecond you spend at the beginning of the race holding down the button, the boat's speed increases by one millimeter per millisecond.

So, because the first race lasts 7 milliseconds, you only have a few options:

    Don't hold the button at all (that is, hold it for 0 milliseconds) at the start of the race. The boat won't move; it will have traveled 0 millimeters by the end of the race.
    Hold the button for 1 millisecond at the start of the race. Then, the boat will travel at a speed of 1 millimeter per millisecond for 6 milliseconds, reaching a total distance traveled of 6 millimeters.
    Hold the button for 2 milliseconds, giving the boat a speed of 2 millimeters per millisecond. It will then get 5 milliseconds to move, reaching a total distance of 10 millimeters.
    Hold the button for 3 milliseconds. After its remaining 4 milliseconds of travel time, the boat will have gone 12 millimeters.
    Hold the button for 4 milliseconds. After its remaining 3 milliseconds of travel time, the boat will have gone 12 millimeters.
    Hold the button for 5 milliseconds, causing the boat to travel a total of 10 millimeters.
    Hold the button for 6 milliseconds, causing the boat to travel a total of 6 millimeters.
    Hold the button for 7 milliseconds. That's the entire duration of the race. You never let go of the button. The boat can't move until you let go of the button. Please make sure you let go of the button so the boat gets to move. 0 millimeters.

Since the current record for this race is 9 millimeters, there are actually 4 different ways you could win: you could hold the button for 2, 3, 4, or 5 milliseconds at the start of the race.

In the second race, you could hold the button for at least 4 milliseconds and at most 11 milliseconds and beat the record, a total of 8 different ways to win.

In the third race, you could hold the button for at least 11 milliseconds and no more than 19 milliseconds and still beat the record, a total of 9 ways you could win.

To see how much margin of error you have, determine the number of ways you can beat the record in each race; in this example, if you multiply these values together, you get 288 (4 * 8 * 9).

Determine the number of ways you could beat the record in each race. What do you get if you multiply these numbers together?

### input

Time:        53     71     78     80
Distance:   275   1181   1215   1524
