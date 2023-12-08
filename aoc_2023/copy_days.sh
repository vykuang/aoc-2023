#!/usr/bin/env bash
for day in day{6..25}
do
    echo "day: $day"
    mkdir -p $day
    cp "./day_x.py" "$day/$day.py"
done
