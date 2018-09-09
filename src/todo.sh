#!/usr/bin/env bash

# Script that will search all files with code for TODO

if_exists(){ 

    if [ ! -e "$1" ];
    then
        >&2 echo "ERROR: $1  doesn't exist!" 
        exit 
    fi
}

if_exists "pull_tweets.py"
echo pull_tweets.py
echo =============
cat "pull_tweets.py" | grep --color="always" --line-number "TODO"

if_exists "mkdirectories.py"
echo mkdirectories.py
echo =============
cat "mkdirectories.py" | grep --color="always" --line-number "TODO"

if_exists "json_parser.py"
echo json_parser.py
echo =============
cat "json_parser.py" | grep --color="always" --line-number "TODO"


if_exists "constants.py"
echo constants.py
echo =============
cat "constants.py" | grep --color="always" --line-number "TODO"


