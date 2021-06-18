############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/03/02
# Institution:  IAEA
#
# Renames ENDF files according to the information provided
# in their headers. The output format is
# [incident particle]_[material number]_[charge]-[symbol]-[mass].endf
#
# Usage:
#     python rename_endf.py FILE1 [FILE2 ...]
#
############################################################
import subprocess
import os
import sys
import re
from utils.endf_metadata import get_endf_metadata

# library dictionary
NLIB_DIC = {
        0:  'ENDF-B',
        1:  'ENDF-A',
        2:  'JEFF',
        3:  'EFF',
        4:  'ENDF/B',
        5:  'CENDL',
        6:  'JENDL',
        9:  'EAF',
        21: 'SG-23',
        31: 'INDL-V',
        32: 'INDL-A',
        33: 'FENDL',
        34: 'IRDF',
        35: 'BROND',
        36: 'INGDB-90',
        37: 'FENDL/A',
        41: 'BROND'
}


def rename_endf_files(filenames,
                      name_template='[proj]_[matcode]_[fullsym].endf',
                      name_only=False):

    """Rename one or more endf files according to metadata."""
    for orig_fpath in filenames:
        meta_data = get_endf_metadata(orig_fpath)

        orig_fdir, orig_fname = os.path.split(orig_fpath)
        orig_fname_noext, orig_ext = os.path.splitext(orig_fname)

        # get material code
        m = re.search('([0-9]+)', meta_data['HSUB_MAT'])
        if m:
            mat_code = int(m.group(1))
            mat_code_str = f'{mat_code:04}'
        else:
            raise ValueError('ERROR: Material number not found')

        # get isotope string
        sym_name = meta_data['ZSYMAM']
        sym_comps = sym_name.split('-')
        sym_comps[1] = sym_comps[1].capitalize()
        sym_name = '-'.join(sym_comps)

        elem = sym_comps[1]
        charge = sym_comps[0]
        if len(sym_comps) >=3:
            mass = sym_comps[2].lower()
        else:
            mass = ''

        # create symbol name with IAEA (Daniel) naming convention
        sym_name_iaea_nomass = str(charge).rjust(2, '0') + \
                        str(elem).ljust(2, '_')
        sym_name_iaea = sym_name_iaea_nomass + \
                        str(mass).rjust(3, '0')

        # get library abbreviation
        NLIB = meta_data['NLIB']
        if NLIB not in NLIB_DIC:
            print('WARNING: Unknown library identifier (NLIB=' +
                  str(NLIB) + ')')
            libname = 'NA'
        else:
            libname = NLIB_DIC[NLIB]

        # get incident particle
        NSUB = meta_data['NSUB']
        if NSUB == 10:
            # incident neutron data
            inc_part = 'n'
        elif NSUB == 10010:
            # incident proton data
            inc_part = 'p'
        elif NSUB == 10020:
            # incident deuteron data
            inc_part = 'd'
        elif NSUB == 3:
            # photo-atomic interaction data
            inc_part = 'ph'
        else:
            raise ValueError('ERROR: Unknown sublibrary type (NSUB=' + str(NSUB) + ')')

        # create filename from template
        new_fname = name_template.replace('[fullsym]', sym_name)
        new_fname = new_fname.replace('[iaeasym]', sym_name_iaea)
        new_fname = new_fname.replace('[iaeasym_nomass]', sym_name_iaea_nomass)
        new_fname = new_fname.replace('[elem]', elem)
        new_fname = new_fname.replace('[charge]', charge)
        new_fname = new_fname.replace('[mass]', mass)
        new_fname = new_fname.replace('[proj]', inc_part)
        new_fname = new_fname.replace('[matcode]', mat_code_str)
        new_fname = new_fname.replace('[filename]', orig_fname)
        new_fname = new_fname.replace('[ext]', orig_ext)
        new_fname = new_fname.replace('[fbase]', orig_fname_noext)
        new_fname = new_fname.replace('[libname]', libname)

        if name_only:
            return new_fname
        else:
            pass
            # new_fpath = os.path.join(orig_fdir, new_fname)
            # os.rename(orig_fpath, new_fpath)
            # print('renaming ' + orig_fname + ' to ' + new_fname)
            # return new_fname


if __name__ == "__main__":

    if (len(sys.argv) < 2):
        raise ValueError('ERROR: Expecting at least one filename')

    filenames = sys.argv[1:]
    rename_endf_files(filenames)
