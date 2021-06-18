#!/bin/bash
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/03/25
# Institution:  IAEA
#
# Prepares the data part of the FENDL website by copying
# over the ENDF and derived files from the git-annex
# repository to the FENDL website data folder. Additionally,
# creates zip files of the ENDF, ACE, etc. files for the
# sublibraries.
#
# Usage:
#     update_website_endf.sh
#
#     These environment variables must be set:
#       FENDL_DATA_DIR - path to data directory of FENDL website
#       FENDL_REPO_DIR - path to FENDL repository
#
############################################################

# read environment variables
website_data_dir="$FENDL_DATA_DIR"
repo_dir="$FENDL_REPO_DIR"

# delete all data from FENDL website data directory
delete_data=1

# copy all ENDF and derived files from repository to FENDL website data diretory
copy_files=1

# make zip files for the sublibraries
make_zips=1


# ACTIONS START HERE

if [ ! -d "$website_data_dir" ]; then
    echo "ERROR: environment variable FENDL_DATA_DIR does not contain an"
    echo "        existing directory. This variable must point to the"
    echo "        data directory of the FENDL website."
    exit 1
fi

if [ -d "$website_data_dir/.git" ]; then
    echo "ERROR: this folder is a git repository, which is strange."
    echo "       It will not be deleted and the scripts exits now."
    exit 1
fi

if [ ! -d "$repo_dir" ]; then
    echo "ERROR: enviroment variable FENDL_REPO_DIR does not contain an"
    echo "       existing directory. This directory must point to the"
    echo "       FENDL-ENDF repository"
    exit 1
fi
    

curwd=$(pwd)
if [ "$delete_data" -eq "1" ]; then
    echo "INFO: Deleting content of $website_data_dir"
    rm -rf $website_data_dir/*
    if [ ! $? -eq 0 ]; then
        echo "ERROR: could not delete files in website data directory [$website_data_dir]"
        echo "       does it exist?"
    fi
fi

if [ "$copy_files" -eq "1" ]; then
    echo "INFO: Creating directories in $FENDL_DATA_DIR"
    # create directory structure
    cd "$website_data_dir"
    mkdir neutron
    mkdir neutron/endf \
          neutron/ace \
          neutron/group \
          neutron/njoy \
          neutron/plot
    mkdir proton
    mkdir proton/endf \
          proton/ace \
          proton/njoy \
          proton/plot
    mkdir deuteron
    mkdir deuteron/endf \
          deuteron/ace
    mkdir atom
    mkdir atom/endf \
          atom/group
    cd "$curwd"
          
    echo "INFO: Copying files from $FENDL_REPO_DIR to $FENDL_DATA_DIR"
    # copy over the files
    repo_data_dir="$repo_dir/fendl-endf/general-purpose"
    rsync -L --dirs --delete "$repo_data_dir/neutron/" "$website_data_dir/neutron/endf"
    rsync -L --dirs --delete "$repo_data_dir/atom/" "$website_data_dir/atom/endf"
    rsync -L --dirs --delete "$repo_data_dir/proton/" "$website_data_dir/proton/endf"
    rsync -L --dirs --delete "$repo_data_dir/deuteron/" "$website_data_dir/deuteron/endf"

    # now deal with derived files (ace, mxs, etc.)
    repo_data_dir="$repo_dir/general-purpose"
    rsync -L --dirs --delete "$repo_data_dir/neutron/ace/" "$website_data_dir/neutron/ace"
    rsync -L --dirs --delete "$repo_data_dir/neutron/group/" "$website_data_dir/neutron/group"
    rsync -L --dirs --delete "$repo_data_dir/neutron/njoy/" "$website_data_dir/neutron/njoy"
    rsync -L --dirs --delete "$repo_data_dir/neutron/plot/" "$website_data_dir/neutron/plot"

    rsync -L --dirs --delete "$repo_data_dir/proton/ace/" "$website_data_dir/proton/ace"
    rsync -L --dirs --delete "$repo_data_dir/proton/njoy/" "$website_data_dir/proton/njoy"
    rsync -L --dirs --delete "$repo_data_dir/proton/plot/" "$website_data_dir/proton/plot"

    rsync -L --dirs --delete "$repo_data_dir/deuteron/ace/" "$website_data_dir/deuteron/ace"

    rsync -L --dirs --delete "$repo_data_dir/atom/group/" "$website_data_dir/atom/group"
fi

# create zip files of sublibraries

if [ "$make_zips" -eq "1" ]; then
    echo "INFO: Creating zip files for the ENDF and derived files of the sublibraries"
    cd "$website_data_dir"

    # make all the endf zips
    for sublib in neutron proton deuteron atom; do
        zip -r "fendl32-$sublib-endf.zip" "$sublib/endf" \
            && mv "fendl32-$sublib-endf.zip" "$sublib"
    done

    # make all the ace files
    for sublib in neutron proton deuteron; do
        zip -r "fendl32-$sublib-ace.zip" "$sublib/ace" \
            && mv "fendl32-$sublib-ace.zip" "$sublib"
    done

    # assemble neutron gendf files (including photo-atomic gam files)
    # collect .gam files from atom/group and .g files from neutron/group
    workdir=$(mktemp -d -p "$website_data_dir")
    mkdir -p "$workdir/neutron/group"
    cat <( find neutron/group -type f -name "*.g" ) \
        <(find atom/group -type f -name "*.gam") \
        | sort | xargs -Ifiles cp files "$workdir/neutron/group"
    cd "$workdir"
    zip -r fendl32-neutron-gendf.zip neutron/group \
        && mv fendl32-neutron-gendf.zip "$website_data_dir/neutron"
    cd "$website_data_dir"
    rm -rf "$workdir"

    # bundle matxs files
    workdir=$(mktemp -d -p "$website_data_dir")
    mkdir -p "$workdir/neutron/group"
    cat <( find neutron/group -type f -name "*.m" ) \
        | sort | xargs -Ifiles cp files "$workdir/neutron/group"
    cd "$workdir"
    zip -r fendl32-neutron-matxs.zip neutron/group \
        && mv fendl32-neutron-matxs.zip "$website_data_dir/neutron"
    cd "$website_data_dir"
    rm -rf "$workdir"

    cd $website_data_dir
    zip -r fendl32-atom-gendf.zip atom/group && mv fendl32-atom-gendf.zip atom
fi
