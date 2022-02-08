############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/06/29
# Institution:  IAEA
#
# Takes a directory that contains a changes.txt file and
# difference files with names <endf-file>.diff.html.
# The file changes.txt contains the output of
# 'git diff --name-status commit1 commit2', thus the first
# column contains the modification type ((A)dded, (M)odified, (D)eleted)
# and the second column the <endf-file> names relative to the root
# of the fendl-endf repository. This result of this script is an
# output file diff.html with an html-table with links to the 
# <endf-file>.diff.html files.
# 
# Usage:
#     python create_sublib_difftable.py <dir>
#
#     <dir>: directory with changes.txt and differences files 
#
#     Following environment variables must be set:
#
#       FENDL_TEMPLATE_DIR - folder with html templates
#       FENDL_VERSION - version of FENDL library
#       FENDL_OLD_VERSION - previous version of FENDL library
#
############################################################

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import sys
import os

# path to data directory of FENDL website
if len(sys.argv) != 2:
    raise ValueError('Please provide path to diffdir')

fendl_version = os.environ['FENDL_VERSION']
fendl_old_version = os.environ['FENDL_OLD_VERSION']

diffdir = sys.argv[1]
# path to folder with jinja html templates
env = Environment(loader=FileSystemLoader(os.environ['FENDL_TEMPLATE_DIR']))
tmpl = env.get_template('diff_table.jinja')

diff_inpfile = os.path.join(diffdir, 'changes.txt')
html_outfile = os.path.join(diffdir, 'diff.html')

diff_table = pd.read_table(diff_inpfile, header=None)
diff_table.columns = ['status', 'filename']
diff_table['status'] = diff_table['status'].replace({'A': 'added', 'M': 'modified', 'D': 'deleted'})
diff_table['link'] = [os.path.basename(fname) + '.diff.html' for fname in diff_table['filename']]
print(diff_table)

html_output = tmpl.render(change_df=diff_table,
        fendl_version=fendl_version, fendl_old_version=fendl_old_version)
with open(html_outfile, 'w+') as f:
    f.write(html_output)
