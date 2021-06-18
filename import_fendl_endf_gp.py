############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/03/07
# Institution:  IAEA
#
# This script reads the general purpose ENDF files from the
# FENDL library and copies them to a repository folder
# changing the hierarchical structure of the
# directories for compliance with YODA principles [1].
#
# Usage:
#     python import_endf.py <inp-dir> <out-dir>
#
#     <inp-dir>: path to data directory of FENDL library
#     <out-dir>: path to data directory of FENDL repository
#
# NOTE:
#     This script in its current form is not useful
#     to persons outside the IAEA because of the lack
#     of access to the FENDL library directory.
#     It is provided to increase traceability as it
#     can be seen, e.g., which files were excluded
#     and how the migration process worked in general.
#     It is also *only* used to import FENDL data from
#     the legacy directory structure and will not be used
#     for future FENDL library updates.
#
# [1]: https://handbook.datalad.org/en/latest/basics/101-127-yoda.html
#
############################################################

import os
import sys
import shutil
import re
from utils.endf_metadata import is_endf_file
from utils.import_endf_files import copy_endf_files

def main():

    if (len(sys.argv) < 3):
        raise ValueError

    inpdir = os.path.normpath(sys.argv[1])
    outdir = os.path.normpath(sys.argv[2])

    if inpdir == outdir:
        print('input and output directory cannot be the same')
        raise ValueError

    # store tuples of source and destionation paths
    copy_log = []

    ##################################################
    #  copy general purpose endf files to repository
    ##################################################

    gp_lib_outdir = os.path.join(outdir, 'general-purpose')

    # define the libraries
    gp_libs = ['atom', 'neutron', 'proton', 'deuteron', 'neutron-shadow']

    # define where the ENDF files of the libraries are located
    gp_lib_inpdirs = {os.path.join(inpdir, k, 'endf'): k for k in gp_libs}

    # define to which directories the ENDF files in the input
    # directory should be copied
    gp_lib_outdirs = {k: os.path.join(gp_lib_outdir, v)
                      for k, v in gp_lib_inpdirs.items()}

    # check that all required input directories are available
    check_if_dirs_exist(gp_lib_inpdirs)
    # clean existing output directories
    shutil.rmtree(gp_lib_outdir, ignore_errors=True)

    # create the output directories
    os.mkdir(gp_lib_outdir)
    for k, curpath in gp_lib_outdirs.items():
        os.mkdir(curpath)

    # traverse input dirs and transfer endf files
    # to output directories in repository
    # only include endf files whose filename matches pattern
    for cur_inpdir, cur_outdir in gp_lib_outdirs.items():
        print(cur_inpdir + '  ' + cur_outdir)
        copy_endf_files(cur_inpdir, cur_outdir,
                r'(n|p|d|ph)_[0-9]+_[0-9]+-[a-zA-Z]+(-[0-9]+[MmGg]?)?(\.|$)',
                name_template='[proj]_[matcode]_[fullsym].endf')


##################################################
#  useful utility functions
##################################################

def check_if_dirs_exist(dirs):
    """Check if the directories given as iterable exist"""
    for curpath in dirs:
        if not os.path.isdir(curpath):
            print('The path ' + curpath + ' does not exist')
            raise ValueError


##################################################
#  start up
##################################################

if __name__ == '__main__':
    main()
