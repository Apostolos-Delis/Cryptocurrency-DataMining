#!/usr/bin/env bash

##########################################################################
# Description
#    o Script that will search all files with code for TODO
#    o Run ./todo.sh --help for more information
#
##########################################################################

errormsg(){
    >&2 echo -e "\e[31m$1\e[0m"
}

if_exists(){ 

    if [ ! -e "$1" ];
    then
        errormsg "ERROR: $1  doesn't exist!" 
        exit 
    fi
}

grep_todo(){
    local file="$1"
    local DIR="$2"

    # Shift in case of extra args passed in to grep
    shift
    shift

    binary_check='Binary file (standard input) matches'
    
    if_exists "$file"
    output=$(cat "$file" | grep "TODO")
    if [[ ! -z $output ]] && [ "$output" != "$binary_check" ]
    then
        #Make path relative
        rel_path=${DIR#"$RELATIVE_PATH/"}
        echo "$rel_path$file"
        echo =============
        cat "$file" | grep --color="always" --line-number $@ "TODO"
		echo
    fi
}

ls_files(){
    local FILES=$1
    local DIR=$2
    
    cd "$DIR" 
    for file in $FILES
    do 
        #Only allow for files, no symlinks or directories
        #will be processed
        if [[ -f "$DIR$file" ]]
        then 
            grep_todo "$file" "$DIR"
        fi
    done
}

ls_files_recursively(){
    local FILES=$1
    local DIR="$2"
    #echo "RECURSIVE: DIR: $DIR"

    cd "$DIR" 2>/dev/null 
    # This is to prevent recursive bugs
    local saved_dir="$DIR"


    for file in $FILES
    do
        if [[ -d $file ]]
        then
            cd "$saved_dir"
            local DIR="$saved_dir$file/"
            cd "$DIR"
            local FILES=$(ls $ls_flags $search 2>/dev/null)
            ls_files_recursively "$FILES" "$DIR"
            cd "$saved_dir"
        elif [[ -f $file ]]
        then
            grep_todo "$file" "$saved_dir" 
        fi 
     done 
}

VERSION="1.2"

search=""
recursive=false
ls_flags=""
search_python=false
search_dot_files=false


RELATIVE_PATH="$PWD"
DIR="../src/"

while test $# -gt 0
do 
    case "$1" in 
        -h|--help)
            echo "Script to locate all the TODOs in a project directory
Version: $VERSION
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
        --version)
            echo "todo version $VERSION"
            exit 0
            ;;
        *)
            break
            ;;
    esac 
done 

#Define what files will be searched through 
if [ $search_python = true ]
then 
    search="*.py"
fi

#Define file array
if [ "$recursive" = false ] && [ "$DIR" != "" ]
then 
    search="$DIR$search"
fi 

if [ $recursive = true ]
then 
    if [ "$DIR" != "" ]
    then
        cd "$DIR"
    fi
    DIR=$PWD
    
    FILES=$(ls $ls_flags $search 2>/dev/null)

    ls_files_recursively "$FILES" "$DIR/"
else
    FILES=$(ls $ls_flags $search 2>/dev/null)
    ls_files "$FILES" "$PWD/$DIR"
fi 

