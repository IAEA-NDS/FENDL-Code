############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/03/24
# Institution:  IAEA
#
# This script scans the ENDF files of the FENDL library
# (which are in <website>/data/<sublib>/endf) and creates
# an html index file with a table showing all ENDF files,
# their metadata, and links to derived files. This script
# makes use of jinja templates for the html files.
#
# Usage:
#     python create_sublib_table_websites.py
#
#     Following environment variables must be set:
#
#       FENDL_DATA_DIR - data directory of the FENDL website
#       FENDL_TEMPLATE_DIR - folder with html templates
#
############################################################

from utils.endf_metadata import get_endf_metadata
from utils.rename_endf import rename_endf_files

from jinja2 import Environment, FileSystemLoader
from os import walk, environ
from os.path import join, isfile, basename, dirname
import glob

# path to data directory of FENDL website
data_dir = environ['FENDL_DATA_DIR']
# path to folder with jinja html templates
env = Environment(loader=FileSystemLoader(environ['FENDL_TEMPLATE_DIR']))

# input and output files
sublib_dic = {
    'neutron': {
        'endf_dir': join(data_dir, 'neutron/endf'),
        'html_dir': join(data_dir, 'neutron'),
        'template': env.get_template('index_neutron.jinja'),
        'derived_files': {
            'ace': 'ace/[iaeasym]',
            'xsd': 'ace/[iaeasym].xsd',
            'gendf': 'group/[iaeasym].g',
            'matxs': 'group/[iaeasym].m',
            'ace_plot': 'plot/[iaeasym]_ace.pdf',
            'htr_plot': 'plot/[iaeasym]_htr.pdf',
            'njoy_inp': 'njoy/[iaeasym].nji',
            'njoy_out': 'njoy/[iaeasym].out'
        }
    },
    'proton': {
        'endf_dir': join(data_dir, 'proton/endf'),
        'html_dir': join(data_dir, 'proton'),
        'template': env.get_template('index_proton.jinja'),
        'derived_files': {
            'ace': 'ace/[iaeasym].ace',
            'xdr': 'ace/[iaeasym].xdr',
            'ace_plot': 'plot/[iaeasym]_ace.ps',
            'njoy_inp': 'njoy/[iaeasym].nji',
            'njoy_out': 'njoy/[iaeasym].out'
        }
    },
    'deuteron': {
        'endf_dir': join(data_dir, 'deuteron/endf'),
        'html_dir': join(data_dir, 'deuteron'),
        'template': env.get_template('index_deuteron.jinja'),
        'derived_files': {
            'ace': 'ace/[iaeasym].ace',
            'xdr': 'ace/[iaeasym].xdr'
        }
    },
    'atom': {
        'endf_dir': join(data_dir, 'atom/endf'),
        'html_dir': join(data_dir, 'atom'),
        'template': env.get_template('index_atom.jinja'),
        'derived_files': {
            'gendf_files': 'group/[iaeasym_nomass]*.gam'
        }
    }
}


# utility functions

def create_sublib_html(sublib_spec):
    """take a dic with paths and create html file"""
    endf_dir = sublib_spec['endf_dir']
    template = sublib_spec['template']
    html_dir = sublib_spec['html_dir']
    html_outfile = html_dir + '/index.html'
    # get all endf files
    endf_file_paths = []
    endf_metadata_list = []
    for (dirpath, dirnames, filenames) in walk(endf_dir):
        endf_file_paths.extend(filenames)
        break
    # get the metadata
    endf_metadata_list = []
    for curf in endf_file_paths:
        curpath = join(endf_dir, curf)
        cur_metadata = get_endf_metadata(curpath)
        cur_metadata['filename'] = curf
        # find associated derived files
        if 'derived_files' in sublib_spec:
            cur_metadata['derived_files'] = {}
            dfiles = cur_metadata['derived_files']
            for ftype, fpat in sublib_spec['derived_files'].items():
                fapp_path = rename_endf_files([curpath], name_template=fpat,
                                              name_only=True)
                if '?' in fapp_path or '*' in fapp_path:
                    dfiles[ftype] = get_gendf_gam_list(html_dir, fapp_path)
                elif isfile(join(html_dir, fapp_path)):
                    dfiles[ftype] = fapp_path
                else:
                    print('WARNING: could not find ' + join(html_dir, fapp_path))

        endf_metadata_list.append(cur_metadata)

    # sort the list for output
    def custom_int(x):
        try:
            val = int(x)
        except Exception:
            val = 9999
        return val

    endf_metadata_list = sorted(endf_metadata_list, key=lambda x: custom_int(x['MAT']))
    for idx, metadata_el in enumerate(endf_metadata_list):
        metadata_el['idx'] = idx
        metadata_el['EMAX_STR'] = '{:.2e}'.format(metadata_el['EMAX'])

    html_output = template.render(endf_metadata_list=endf_metadata_list)
    with open(html_outfile, 'w+') as f:
        f.write(html_output)


def get_gendf_gam_list(dir, template):
    """Get isotopes of photo-atomic library"""
    subdir = dirname(template)
    full_template = join(dir, template)
    fpaths = glob.glob(full_template)
    fpaths = sorted(fpaths)
    items = [
        {
          'name': basename(p)[4:7],
          'link': join(subdir, basename(p))
        }
        for p in fpaths 
    ]
    return items


# main routine
if __name__ == '__main__':

    for sublib in sublib_dic:
        create_sublib_html(sublib_dic[sublib])
