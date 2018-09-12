#!/usr/bin/env bash

# Script that will search all files with code for TODO
# run ./todo.sh -h for more information

if_exists(){ 

    if [ ! -e "$1" ];
    then
        >&2 echo "ERROR: $1  doesn't exist!" 
        exit 
    fi
}

grep_todo(){
    file="$1"
    binary_check='Binary file (standard input) matches'
    shift
    if_exists "$file"
    output=$(cat "$file" | grep "TODO")
    if [[ ! -z $output ]] && [ "$output" != "$binary_check" ]
    then
        echo "$file"
        echo =============
        cat "$file" | grep --color="always" --line-number $@ "TODO"
    fi
}

search=""
recursive=false
ls_flags=""
search_python=false

DIR="../src"

while test $# -gt 0
do 
    case "$1" in 
        -h|--help)
            echo "Script to locate all the TODOs in a project directory
Version: 1.2

USAGE: ./todo.sh [OPTIONS] 

Options: 
    -h, --help          Show this help message 
    -p, --python        Only process python files 
    -r, --recursive     Process all subdirectories recursively
    -a, --dot-files     Search through dotfiles as well (similar to ls -A)
    -d, --dir <DIR>     Search through a given base directory"

            exit 0
            ;;
        -p|--python)
            search_python=true
            shift 
            ;;
        -r|--recursive)
            recursive=true
            ls_flags="$ls_flags -R"
            shift
            ;;
        -a|--dot-files)
            ls_flags="$ls_flags -A"
            shift
            ;;
        -d|--dir)
            shift 
            DIR="$1"       
            shift 
            ;;
        *)
            break
            ;;
    esac 
done 


#Define what files will be searched through 
if [ $recursive = true ]
then 
    if [ $search_python = true ]
    then 
        search="$search $DIR/*.py $DIR/**/*.py"
    else
        search="$search $DIR/* $DIR/**/*"
    fi
elif [ $search_python = true ]
then 
    search="$search $DIR/*.py"
else 
    search="$search $DIR/*"
fi

#Define file array
echo "ls $ls_flags $search"
FILES=$(ls $ls_flags $search)

for file in $FILES
do 
    #Only allow for files, no symlinks or directories
    #will be processed
    if [[ -f $file ]]
    then 
        grep_todo $file
    fi
done
    
