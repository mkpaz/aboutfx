#!/usr/bin/env bash

# Runs cloc (Counts Line of Code, https://github.com/AlDanial/cloc) for every
# commit in the Git log. The script isn't polished, just a quick and dirty solution.
# ./cloc.sh <repo_relative_path> <grep_filter> <output_path>
# e.g. ./cloc.sh jfx.git '|2022' cloc_2022.json

SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
REPO="$1"
QUERY="$2"
OUTPUT="$3"

cd "$SCRIPT_DIR/$REPO"

IFS=$'\n'

echo "[" > "$OUTPUT"
for line in $(git log --pretty="format:%H|%ad|%d" --date=short --tags --no-walk | grep "$QUERY" | sed 's/[() ]//g;s/tag://g'); do
    hash=$(echo $line | cut -f1 -d '|')
    date=$(echo $line | cut -f2 -d '|')
    tag=$(echo $line | cut -f3 -d '|')

    stat=$(cloc --json --quiet --processes=16 --git "$hash")
    echo "{ \"hash\": \"$hash\", \"date\": \"$date\", \"tag\": \"$tag\", \"cloc\": $stat }," >> "$OUTPUT"
done

echo "]" >> "$OUTPUT"
