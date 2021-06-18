#!/bin/bash

diffmode="$1"
if [ "$diffmode" != "onlynames" ] && [ "$diffmode" != "full" ] \
    && [ "$diffmode" != "header" ] && [ "$diffmode" != "test" ]; then
    echo "ERROR: first argument must be either 'onlynames' or 'full'"
    exit 1
fi

relfilepath="$2"
reffile1="$3"
reffile2="$4"

if [ -d "$reffile1" ]; then
    exit
fi
if [ -d "$reffile2" ]; then
    exit
fi

filepath="$GIT_WORK_TREE/$relfilepath"
dirpath="$(dirname $filepath)"

if [ "$reffile1" != "/dev/null" ]; then
    rawpath1=$(cat $reffile1)
    truefile1="$dirpath/$rawpath1"
fi

if [ "$reffile2" != "/dev/null" ]; then
    rawpath2=$(cat $reffile2)
    truefile2="$dirpath/$rawpath2"
fi

if [ "$reffile1" != "/dev/null" ]; then
    cmpfile1="$(mktemp)"
    if [ "$diffmode" = "header" ]; then
        head -n20 "$truefile1" | cut -c-75 -- > "$cmpfile1"
    else
        cut -c-75 "$truefile1" > "$cmpfile1"
    fi
    dos2unix --quiet "$cmpfile1"
fi

if [ "$reffile2" != "/dev/null" ]; then
    cmpfile2=$(mktemp)
    if [ "$diffmode" = "header" ]; then
        head -n20 "$truefile2" | cut -c-75 -- > "$cmpfile2"
    else
        cut -c-75 "$truefile2" > "$cmpfile2"
    fi
    dos2unix --quiet "$cmpfile2"
fi

if [ "$diffmode" = "onlynames" ]; then

    if [ "$reffile1" = "/dev/null" ]; then
        echo "only in #2: $relfilepath"
    elif [ "$reffile2" = "/dev/null" ]; then
        echo "only in #1: $relfilepath"
    else
        diff -q "$cmpfile1" "$cmpfile2" > /dev/null
        if [ "$?" -ne 0 ]; then
            echo "different in #1 and #2: $relfilepath"
        fi
    fi

elif [ "$diffmode" = "full" ]; then

    vimdiff "$cmpfile1" "$cmpfile2"

elif [ "$diffmode" = "header" ]; then

    echo '################################################################################################################################################################'
    echo '################################################################################################################################################################'
    echo
    echo "FILE: $relfilepath"
    echo
    if [ "$reffile1" = "/dev/null" ]; then
        echo "only in #2"
    elif [ "$reffile2" = "/dev/null" ]; then
        echo "only in #1"
    else
        diff -y "$cmpfile1" "$cmpfile2"
    fi
    echo

elif [ "$diffmode" = "test" ]; then

    if [ ! -d "diffdir" ]; then
        echo 'ERROR: diffdir does not exist'
        exit
    fi
    difffile="diffdir/$relfilepath.diff"
    locdiffdir="diffdir/$(dirname $relfilepath)"
    mkdir -p "$locdiffdir"
    delta --light --side-by-side --width=200 n_0125_1-H-1.endf n_0128_1-H-2.endf | ansi2html --white | sed 's/<head>/<head><meta charset="UTF-8" \/>/' > "$difffile"
fi
    
if [ "$reffile1" != "/dev/null" ]; then
    rm "$cmpfile1"
fi

if [ "$reffile2" != "/dev/null" ]; then
    rm "$cmpfile2"
fi
