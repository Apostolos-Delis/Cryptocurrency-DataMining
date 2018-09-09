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
output=$(cat "pull_tweets.py" | grep "TODO")
if [[ ! -z $output ]];
then
    echo pull_tweets.py
    echo =============
    cat "pull_tweets.py" | grep --color="always" --line-number "TODO"
fi

if_exists "mkdirectories.py"
output=$(cat "mkdirectories.py" | grep "TODO")
if [[ ! -z $output ]];
then 
    echo mkdirectories.py
    echo =============
    cat "mkdirectories.py" | grep --color="always" --line-number "TODO"
fi

if_exists "json_parser.py"
output=$(cat "json_parser.py" | grep "TODO")
if [[ ! -z $output ]];
then 
    echo json_parser.py
    echo =============
    cat "json_parser.py" | grep --color="always" --line-number "TODO"
fi

if_exists "constants.py"
output=$(cat "constants.py" | grep "TODO")
if [[ ! -z $output ]];
then
    echo constants.py
    echo =============
    cat "constants.py" | grep --color="always" --line-number "TODO"
fi

