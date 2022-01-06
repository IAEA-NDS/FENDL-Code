#!/bin/bash

diffmode="$1"
if [ "$diffmode" != "onlynames" ] && [ "$diffmode" != "full" ] \
    && [ "$diffmode" != "header" ] && [ "$diffmode" != "difffile" ]; then
    echo "ERROR: first argument must be either onlynames, full, header or difffile"
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


if [ "$diffmode" = "onlynames" ]; then
    # for some reason: git diff --name-only ...
    # is MUCH faster than this approach

    if [ "$reffile1" = "/dev/null" ]; then
        echo "only in #2: $relfilepath"
    elif [ "$reffile2" = "/dev/null" ]; then
        echo "only in #1: $relfilepath"
    else
        if [ "$truefile1" != "$truefile2" ]; then
            echo "different in #1 and #2: $relfilepath"
        fi
    fi
    exit
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


if [ "$diffmode" = "full" ]; then

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

elif [ "$diffmode" = "difffile" ]; then

    if [ ! -d "diffdir" ]; then
        echo 'ERROR: diffdir does not exist'
        exit
    fi
    if [ "$reffile1" = "/dev/null" ]; then
        echo "only in #2"
    elif [ "$reffile2" = "/dev/null" ]; then
        echo "only in #1"
    else
        echo "working on $relfilepath"
        difffile="diffdir/$relfilepath.diff.html"
        locdiffdir="diffdir/$(dirname $relfilepath)"
        mkdir -p "$locdiffdir"
        dtwdiff "$cmpfile1" "$cmpfile2" | ansi2html --white | sed 's/<head>/<head><meta charset="UTF-8" \/>/' > "$difffile"
    fi
fi
    
if [ "$reffile1" != "/dev/null" ]; then
    rm "$cmpfile1"
fi

if [ "$reffile2" != "/dev/null" ]; then
    rm "$cmpfile2"
fi
