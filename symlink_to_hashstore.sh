#!/bin/sh
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/08
# Institution:  IAEA
#
# Replace a file by a symbolic link pointing to
# its content in a hashstore. The symbolic link
# will be relative. Backups of the original files
# are created as well (.bak) ending.
# 
# Usage:
#     symlink_to_hashstore.sh <hashstore> <filename>
#
#     <hashstore>: directory with files of the form
#                  sha256-<sha256hash>
#     <filename>:  file that should be replaced by a
#                  symbolic link pointing to the hashstore.
#
############################################################

hashstore="$1"
fpath="$2"
fname=$(basename $fpath)
fdir=$(dirname $fpath)
sha256hash=$(sha256sum $fpath | cut -d' ' -f1)

hashfile="${hashstore}/sha256-${sha256hash}"
if [ -f "$hashfile" ]; then
    echo "link to hashfile: $fpath"
    linktar=$(realpath --relative-to=$fdir $hashfile) 
    cd $fdir
    mv $fname $fname.bak
    ln -s $linktar $fname 
else
    echo "no hashfile found for: $fpath"
fi
