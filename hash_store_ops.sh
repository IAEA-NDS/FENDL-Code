#!/bin/bash
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/01/11
# Institution:  IAEA
#
# This script can do two things:

# (1) It can store a file in a directory
#     with its name changed to the sha256 cryptographic
#     hash of its content. The destination directory can
#     function as a content-addressable storage.
#     The file in the source directory is not altered.
#
# (2) It can associate a symbolic link in a git-annex
#     repository with a weburl that points to a directory
#     with files as created in (1).
#
# Usage:
#     ./hash_store_ops.sh store <hashstore-dir> <filepath>
#     ./hash_store_ops.sh associate <weburl> <filepath>
#
#     <hashstore-dir>: directory to be used as hashstore
#     <weburl>: url pointing to a directory with a hashstore
#     <filepath>: if mode 'store', path to the file that
#                 should be stored in the hashstore.
#                 if mode 'associate', path to the symbolic
#                 link that should be associated with the
#                 corresponding weburl
#
############################################################

mode=$1
hashdir="$2"
filepath="$3"

if [ "$mode" == "store" ]; then 

    filename=$(basename $filepath)
    filehash="sha256-$(sha256sum $filepath | cut -d' ' -f1)"
    outfilepath="$hashdir/$filehash"
    outlogfile="$hashdir/hashinfo.txt"

    if [ -f "$outfilepath" ]; then
        existhash="sha256-$(sha256sum $outfilepath | cut -d' ' -f1)"
        if [ "$existhash" != "$filehash" ]; then
            echo "FATAL ERROR: Inconsistent file $existhash in hashstore"
            exit 2
        else
            echo $filehash $filename >> $outlogfile
            echo "skipped '$outfilepath' because already in hashstore"
            exit 0
        fi
    fi

    cp $filepath $outfilepath && \
      echo $filehash $filename >> $outlogfile

    retcode="$?"

    chmod 444 $outfilepath

    if [ "$retcode" -eq 0 ]; then
        echo "stored '$filepath' as $filehash"  
    else
        echo "error: could not store $filepath"
    fi
    exit $retcode


elif [ "$mode" == "associate" ]; then

    filehash="sha256-$(ls -la $filepath | sed -e 's/^.*--\([0-9a-f]*\).*$/\1/')"
    url="${hashdir}${filehash}"
    curdir=`pwd`
    filename="$(basename $filepath)"
    cd $(dirname $filepath)
    git annex addurl --file="$filename" "$url"
    cd $curdir


elif [ "$mode" == "print_association" ]; then

    filehash="sha256-$(ls -la $filepath | sed -e 's/^.*--\([0-9a-f]*\).*$/\1/')"
    url="${hashdir}${filehash}"
    echo $url $filepath


else
    echo "ERROR: Unsupported mode $mode".
    echo "       Use either 'store' or 'associate'"
    exit 1
fi
