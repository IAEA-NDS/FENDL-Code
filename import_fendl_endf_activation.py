############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2020/10/29
# Institution:  IAEA
#
# This script reads the activation ENDF files from the FENDL
# library and copies them to a repository folder
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
#
# [1]: https://handbook.datalad.org/en/latest/basics/101-127-yoda.html
#
############################################################

import os
import sys
import shutil
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
    #  copy activation files to repository
    ##################################################

    activ_lib_outdir = os.path.join(outdir, 'activation')
    activ_libs = ['neutron-activ', 'proton-activ',
                  'deuteron-activ', 'deuteron-activ-renorm']

    # define where the ENDF files of the libraries are located
    activ_lib_inpdirs = {}
    activ_lib_outdirs = {}
    for curlib in activ_libs:
        # all activation libraries have gendf and pendf
        # neutron-activ has in addition endf
        basedirs = ['gendf', 'pendf']
        if curlib == 'neutron-activ':
            basedirs.append('endf')
        curinpdirs = {k: os.path.join(inpdir, curlib, k)
                      for k in basedirs}
        activ_lib_inpdirs.update({
            v: curlib for k, v in curinpdirs.items()
        })
        activ_lib_outdirs.update({
            v: os.path.join(activ_lib_outdir, curlib, k)
            for k, v in curinpdirs.items()
        })

    # check that all required input directories are available
    check_if_dirs_exist(activ_lib_inpdirs)
    # clean existing output directories
    shutil.rmtree(activ_lib_outdir, ignore_errors=True)

    # create the output directories
    os.mkdir(activ_lib_outdir)
    for k, curpath in activ_lib_outdirs.items():
        os.makedirs(curpath)

    # traverse input dirs and transfer endf files
    # to output directories in repository
    for cur_inpdir, cur_outdir in activ_lib_outdirs.items():
        copy_endf_files(cur_inpdir, cur_outdir,
            name_template='[fbase]_[proj]_[matcode]_[fullsym].endf')


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
