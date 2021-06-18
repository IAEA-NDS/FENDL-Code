############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/03/07
# Institution:  IAEA
#
# This script takes an input directory with ENDF files
# and copies them to a destination directory.
# It does  a minimal  test to check  wheter a file is
# indeed an ENDF file and only copies files that pass
# the test. It also does the following actions on the
# copied files:
#
#   * Rename ENDF files according to ENDF header
#   * Remove empty lines
#   * Convert line endings to Unix-style (LF)
#
# This script is a wrapper around import_fendl_endf.py
# in the utils package in order to be able to use the
#  renaming functionality from the command line..
#
# Usage:
#     python import_endf_files.py <inp-dir> <out-dir>
#
#     <inp-dir>: path to data directory of FENDL library
#     <out-dir>: path to data directory of FENDL repository
#
############################################################

import argparse
import os
from utils.import_endf_files import copy_endf_files

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Import ENDF files from directory')
    parser.add_argument('inpdir', help='input directory', type=str)
    parser.add_argument('outdir', help='output directory', type=str)
    parser.add_argument('--pat', help='regex to match files in input directory',
                        type=str, nargs='?', default=r'.*')
    parser.add_argument('--template', help='template for new names of ENDF files in output directory',
                        nargs='?', type=str, default='[proj]_[matcode]_[fullsym].endf')
    parser.add_argument('-n', help='print information without copying', action='store_true')
    args = parser.parse_args()

    inpdir = args.inpdir
    outdir = args.outdir
    template = args.template
    pattern = args.pat
    dry_run = args.n

    copy_endf_files(inpdir, outdir, pattern=pattern,
            name_template=template, dry_run=dry_run)
