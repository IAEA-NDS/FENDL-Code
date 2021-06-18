############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2021/06/01
# Institution:  IAEA
#
# Utility functions to retrieve the information of ENDF
# files stored in their header or to retrieve the same
# information from a html website with a table of a particle
# sublibrary, and functions to compare these differences.
# 
#
# Usage:
#     <command-call>
#
#     <parameter>: <description>
#
############################################################


from utils import rename_endf, endf_metadata
from bs4 import BeautifulSoup
import html5lib
import re
import os
import argparse


def get_fendl_sublib_table_from_dir(endf_dir):
    file_list = []
    for root, dirs, files in os.walk(endf_dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    isolist = {}
    for file in file_list:
        meta_data = endf_metadata.get_endf_metadata(file)
        if file.endswith('_.txt'):
            continue
        if meta_data is None:
            print('problem with ' + str(file))
        else:
            isolist[meta_data['MAT']] = {
                'FILE': os.path.basename(file),
                'MAT': meta_data['MAT'],
                'ZSYMAM': meta_data['ZSYMAM'],
                'ALAB': meta_data['ALAB'],
                'EDATE': meta_data['EDATE'],
                'AUTH': meta_data['AUTH'].replace(' and ',',').replace(' ',''),
                'HSUB_LIB': meta_data['HSUB_LIB'],
                'EMAX': '{:e}'.format(float(meta_data['EMAX']))
            }
    return isolist


def get_fendl_sublib_table_from_htmlfile(endf_table_file):
    with open(endf_table_file) as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html5lib')
    tbody_el = soup.find('tbody')
    tr_els = tbody_el.find_all('tr', {'bgcolor': re.compile(r'.*')})
    isolist = {} 
    for tr_el in tr_els:
        td_els = tr_el.find_all('td')
        cur_info = {}
        for idx, td_el in enumerate(td_els):
            if idx == 1:
                cur_info['MAT'] = td_el.text.strip()
            elif idx == 2:
                cur_info['ZSYMAM'] = td_el.text.strip()
            elif idx == 3:
                cur_info['ALAB'] = td_el.text.strip()
            elif idx == 4:
                cur_info['EDATE'] = td_el.text.strip()
            elif idx == 5:
                cur_info['AUTH'] = td_el.text.strip().replace(' and ',',').replace(' ','')
            elif idx == 6:
                cur_info['HSUB_LIB'] = td_el.text.strip()
            elif idx == 7:
                cur_info['EMAX'] = '{:e}'.format(float(td_el.text.strip()))
        isolist[cur_info['MAT']] = cur_info
    return isolist


def compare_table(table1, table2):
    for curiso in table1:
        iso1 = table1[curiso]
        if curiso in table2:
            iso2 = table2[curiso]
            # do the comparison
            printed_header = False
            found_diffs = False
            for keyname in iso2:
                if iso1[keyname] != iso2[keyname]:
                    found_diffs = True
                    if not printed_header:
                        print('Difference in ' + str(curiso) +
                              ' (' + iso1['ZSYMAM'] + ')')
                        #print('[filename: ' + str(iso1['FILE']) + ']')
                        printed_header = True
                    print(keyname + ' differs: (file) ' +
                          str(iso1[keyname]) + ' != ' + str(iso2[keyname]) +
                          ' (table)')
            if found_diffs:
                print('--------------------------')
    print('########################################')
    print('       MAT numbers only in #1           ')
    print('########################################')
    for curiso in table1:
        iso1 = table1[curiso]
        if curiso not in table2:
            print('MAT: ' + curiso + ' - ' + iso1['ZSYMAM'] + ' - ' + iso1['EDATE'] +
                  ' - ' + iso1['ALAB'] + ' - ' + iso1['AUTH'] + ' - ' + iso1['HSUB_LIB'])
    print('########################################')
    print('       MAT numbers only in #2           ')
    print('########################################')
    for curiso in table2:
        iso2 = table2[curiso]
        if curiso not in table1:
            print('MAT: ' + curiso + ' - ' + iso2['ZSYMAM'] + ' - ' + iso2['EDATE'] +
                  ' - ' + iso2['ALAB'] + ' - ' + iso2['AUTH'] + ' - ' + iso2['HSUB_LIB'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare ENDF directories and sublib tables')
    parser.add_argument('dir1', help='directory with ENDF file or path to html file with table', type=str)
    parser.add_argument('dir2', help='directory with ENDF file or path to html file with table', type=str)
    args = parser.parse_args()
    dir1 = args.dir1
    dir2 = args.dir2
