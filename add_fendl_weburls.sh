############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/06/28
# Institution:  IAEA
#
# Scans through the files in the git-annex repository 
# FENDL-Processed and its submodule FENDL-ENDF and associates
# them with their storage location on the IAEA-NDS webserver.
#
# Usage:
#     ./add_fendl_weburls.sh PREFIX COMMIT-ID
#
#     PREFIX:   the prefix of the directory associated with
#               a specific git commit, e.g., fendl32-2021-06-24-
#
#     COMMIT-ID:    the commit id of FENDL-Processed whose
#                   files should be associated with the
#                   corresponding urls on the webserver
#                   
############################################################
#!/bin/bash

urlprefix="$1"
commitid="$2"

urlbase="https://www-nds.iaea.org/fendl_library/data/commits/${urlprefix}${commitid}"

if [ -z "$commitid" ]; then
    echo "ERROR: Need to specify a commit id as argument"
fi

gitroot=$(git rev-parse --show-toplevel)

if [ ! "$(pwd)" = "$gitroot" ]; then
    echo "ERROR: Execute this command from the FENDL git root directory"
fi

git checkout $commitid
if [ ! "$?" -eq 0 ]; then
    echo "ERROR: Checking out $commitid failed"
fi

git submodule update --init --recursive
if [ ! "$?" -eq 0 ]; then
    echo "ERROR: Updating submodules failed"
fi

scandirs=(
    # atom
    "fendl-endf/general-purpose/atom"
    "general-purpose/atom/group"
    # neutron
    "fendl-endf/general-purpose/neutron"
    "general-purpose/neutron/ace"
    "general-purpose/neutron/group"
    "general-purpose/neutron/njoy"
    "general-purpose/neutron/plot"
    # deuteron
    "fendl-endf/general-purpose/deuteron"
    "general-purpose/deuteron/ace"
    # proton
    "fendl-endf/general-purpose/proton"
    "general-purpose/proton/ace"
    "general-purpose/proton/njoy"
    "general-purpose/proton/plot"
)

scanurls=(
    # atom
    "atom/endf"
    "atom/group"
    # neutron
    "neutron/endf"
    "neutron/ace"
    "neutron/group"
    "neutron/njoy"
    "neutron/plot"
    # deuteron
    "deuteron/endf"
    "deuteron/ace"
    # proton
    "proton/endf"
    "proton/ace"
    "proton/njoy"
    "proton/plot"
)


for cidx in $(seq "${#scandirs[@]}"); do
    let "idx=cidx-1"
    curdir="${scandirs[$idx]}"
    curdir2="${scanurls[$idx]}"

    cd "$gitroot"
    cd "$curdir"

    for curfile in $(ls); do
        cururl="$urlbase/$curdir2/$curfile"
        git annex addurl --file="$curfile" "$cururl"
    done
done
