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
# This script makes use of the command line tools
# sed and dos2unix. The script can be
# run either as a stand-alone utility or imported
# into other Python scripts.
#
# Usage:
#     python import_endf_files.py <inp-dir> <out-dir>
#
#     <inp-dir>: path to data directory of FENDL library
#     <out-dir>: path to data directory of FENDL repository
#
############################################################

import os
import sys
import subprocess
import shutil
import re
from utils.endf_metadata import is_endf_file
from utils.rename_endf import rename_endf_files


def copy_endf_files(inpdir, outdir, pattern='.*',
                    name_template='[proj]_[matcode]_[fullsym].endf',
                    dry_run=False):
    """Copy endf files from inpdir to outdir and make transformations"""

    if inpdir == outdir:
        print('input and output directory cannot be the same')
        raise ValueError

    for curfile in os.listdir(inpdir):
        fpath = os.path.join(inpdir, curfile)
        # skip not maching filenames
        is_match = re.match(pattern, curfile)
        if not is_match:
            continue
        # skip directories
        if not os.path.isfile(fpath):
            continue
        elif not is_endf_file(fpath):
            print('skipping ' + fpath + ' because not ENDF file')
            continue
        # copy the endf file to the appropriate location
        # in the destination repository
        try:
            fname_out = rename_endf_files([fpath], name_template=name_template, name_only=True)
        except:
            print('could not rename ' + fpath)
            continue

        fpath_out = os.path.join(outdir, fname_out)
        print('copying ' + fpath + ' to ' + fpath_out)
        if not dry_run: 
            if os.path.islink(fpath_out):
                os.unlink(fpath_out)
            shutil.copy(fpath, fpath_out, follow_symlinks=False)
            subprocess.run(['dos2unix', fpath_out])
            print('removing empty lines from ' + fpath_out)
            subprocess.run(['sed', '-i', '/^[[:space:]]*$/d', fpath_out])
