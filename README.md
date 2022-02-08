# Codes for FENDL

This repository contains bash and Python scripts that
are used to maintain and update the FENDL library.
Some of the scripts may be useful to users outside the
IAEA but the primary intention of publishing this repository
is to make the FENDL library more traceable
also in terms of codes and procedures.

The scripts are provided under the MIT license, which
means in a nutshell that no guarantees are given regarding
their proper functioning and no responsibility is taken
for damage that may occur in connection with their use.
Likewise, no guarantees are given for software and products
referenced in this document and if you use any of those,
it is at your own risk in accordance with the license
provided by the respective copyright owner.

## Philosophy to ensure traceability

The FENDL library is hosted at the [IAEA-NDS website][fendl-website].
The website visitor can browse through the different versions
of the library, read summaries of effected updates
and retrieve relevant documents.
ENDF and derived files are presented in tables and can be downloaded
individually or in bulk as zip files.

While this approach to publishing is historically established
and convenient for many users, it may not be the best approach to
track changes at a technical level. Reports convey a lot of
valuable information and also describe effected updates,
but a technical solution that enables the tracing
of changes directly at the file level may be preferred by
some users and helps establishing a less error-prone library
update process.

[Git][git-website] is a well-established tool to keep track of changes
in software development projects but is not ideal for
tracking a large number of large files. Several solutions
exist to extend Git to improve its handling of large files.
Among freely available ones is [git-annex][git-annex-website].

Git-annex enables the separation of tracking and content.
Large files are replaced by symbolic links pointing to
files in a [content-addressable storage][cas-info-url] which is stored
along with the tracking information maintained by git.
Importantly, it is also possible to register external
locations, e.g., url addresses, that provide the full
file associated with a symbolic link. The target of
the symbolic link contains a [cryptograhpic hash][hash-wiki-url]
and it is therefore always possible to verify if a given file
is really the correct target of a symbolic link.
This aspect is also important
for future-proofing: If git-annex won't be supported or
distributed anymore in the future, the amount of work
to implement an analogous solution on the basis of
symbolic links with cryptographic hashes to identify
their targets is well manageable.

Git-annex is the chosen approach to set up
the [FENDL-ENDF repository][fendl-endf-repo] containing the ENDF files
of the FENDL library and the [FENDL-Processed repository][fendl-proc-repo]
containing thereof derived files, such as ace files and plots.
The basic functionality of git without any additional
tool already allows to get an idea of what has changed
at the level of files. Git-annex offers the additional capability
to retrieve files of the FENDL library in a git-like fashion.
This retrieval may be performed transparently from any external location
registered within the git-annex repository, hence
the user does not need to be concerned
about the file location so long as the file is stored at a place
where it is accessible by git-annex.


## How to use git-annex to interact with the FENDL library

Installation instructions for git-annex are available [here][git-annex-install-url].
Noteworthy, at the time of writing Windows is not as well supported as Linux and MacOS.
Also [git][git-website] must be available on the system.
The following instructions work on Linux and MacOS.

In order to retrieve the FENDL library repository,
one can invoke
```
git clone https://github.com/iaea-nds/FENDL-Processed.git --recursive
```
The option `--recursive` is necessary to clone also the FENDL-ENDF submodule
containing the ENDF files.

For instance, we can inspect the general-purpose neutron sublibrary by
changing into its directory and listing the contained files
```
cd FENDL-Processed/fendl-endf/general-purpose/neutron
ls -la
```
There are only symbolic links, which appear as being broken because
the files are not available in the local content-addressable storage.

In order to retrieve the content of a file, we can use `git-annex-get`, e.g.,
```
git annex get n_2634_26-Fe-57.endf
```
After this operation, the link will not be broken anymore.
To retrieve all files in a directory, use
`git annex get .`


## Functionality of the scripts in this repository

This section contains an incomplete account of the functionality
of some of the scripts in this repository. Most scripts have
a header with further information on their purpose and how
to use them.

### Importing ENDF files

ENDF files of collaborators are
sometimes provided using different naming conventions and
their filenames need to be homogenized before the
inclusion into the FENDL library. The Python script
`import_endf_files.py` allows to copy ENDF files from one
folder to another one, automatically renaming them in the destination folder
according to the information in the header of the ENDF files.
The exact naming convention is defined as a template string on the
command line.
For example, the call
```
python import_endf_files.py --pat '.*\.endf' --template '[proj]_[fullsym].endf' inpdir outdir
```
copies all files that end in `.endf` from the directory `inpdir` to the directory
`outdir` where they are renamed according to the template specification, e.g.,
`n_50-Sn-124.endf` in this example.

### Copying files from the repository to the website data directory

ENDF files are stored in the FENDL-ENDF repository using a specific directory
layout. The derived files are stored in the FENDL-Processed repository.
The latter repository also includes the FENDL-ENDF repo
as a submodule. In order to comply with [YODA principles][yoda-url], the
directory structure inside the repository is different from the directory
structure followed traditionally on the IAEA-NDS website. The bash script
`update_website_endf.sh` copies the data files (ENDF and derived files)
present in the repository to another directory using a changed directory
layout mirroring that of the FENDL library on the IAEA-NDS website.
An environment variable `FENDL_REPO_DIR` must be set to point to the
root directory of the FENDL-Processed repository. Another environment
variable `FENDL_DATA_DIR` must be set to point to an empty directory
where the data files are copied to. The environment variables
`FENDL_VERSION` should contain the version number and is used to 
define the name of some zip files.
In practice, this script has been
used in the following way: A specific commit of the FENDL-Processed
repo is checked out. A new data directory to be associated with
this commit is created on the webserver. Then, `update_website_endf.sh`
is used to transfer the data from the repository to the directory on
the webserver.

### Registering weburls in the git-annex repository

Following the transfer of data to the webserver as described in the
previous section, the symbolic links in the git repo augmented
by git-annex must be associated with the web urls of the files.
The bash script `add_fendl_weburls.sh` can be run
in the root directory of the FENDL-Processed repository to register
the web urls as source locations of the files.


### Copying files from the repository to a hashstore

The workflow discussed in
[the section](#copying-files-from-the-repository-to-the-website-data-directory)
on copying to the website data directory exhibits the disadvantage
that potentially a lot of storage is wasted. If only a single file
were changed in a new commit, all other files would still be copied
over to the website data directory associated with this commit.
Consequently, this solution is not employed for every commit but only
those that represent milestones, such as the release of a new major
library version that is also presented as a website.

To avoid the duplication of data, another option is to scan the
git-annex repository for all distinct files that existed
in the history of the repository and store them in a
directory where they are named according to the sha256 hash
of their content. We call this new directory a hashstore.
If the hashstore is made available on a
webserver, all symbolic links in the git-annex repository can be
associated with the files in the hashstore on the webserver.
The script `hash_store_ops.sh` helps to store files in the
hashstore and to associate symbolic links in a git-annex repository
with the hashstore on a webserver.

To store all distinct files of a git-annex repository that are
represented by symbolic links, we can execute at the root directory
of the repo
```
find .git/annex/objects -type f -exec \
  <path-to-fendl-code>/hash_store_ops.sh store <path-to-hashstore> '{}' \;
```

If the hashstore is exposed on a webserver, symbolic links in a
git-annex repository can be associated with the urls of the files
in the hashstore. Being at the root of the repository, execute
```
find . -not -path '*/.git/*' -type l -exec \
  <path-to-fendl-code>/hash_store_ops.sh associate <hashstore-url> '{}' \;
```

### Comparison of ENDF and derived files

It is pertinent to list files that are different between
different versions (or commits) of the library.
The names of files that changed can be listed by
```
git diff --name-only <EARLIER-COMMIT> <LATER-COMMIT>
```
where `<EARLIER-COMMIT>` and `<LATER-COMMIT>` can be
git commit ids or the names of tags.

Due to the fact that only symbolic links are present
in the repository, it is not possible to show
differences in file content using `git-diff`
because only the changed link targets would be
displayed.

The bash script `annexdiff.sh` can be registered
as an external [git difftool][git-difftool-url] to
compare the file content.
This script assumes that some programs are available,
such as `vim` or `dos2unix`.
The script can be registered as an external difftool by
```
git config --global difftool.annexdiff.cmd '<PATH-TO-ANNEXDIFF>/annexdiff.sh full $BASE $LOCAL $REMOTE'
```
with `<PATH-TO-ANNEXDIFF>` being the absolute path of the script file.

Given that the files to be compared are
locally available, i.e., by using `git annex get` before,
the different versions can be compared by
```
git difftool -y -t annexdiff <EARLIER-COMMIT> <LATER-COMMIT> -- <FILEPATH>
```

### Preparing html tables

The [FENDL library website][fendl-website] contains for each sublibrary an
index.html file with a table listing the available target nuclides along with
meta information extracted from the headers of the ENDF files.
The index.html of each sublibrary also includes a link to another html file
showing a table summarizing the differences to a previous library release.
Clicking on an entry in the latter table opens a side-by-side comparison
of the file contents generated by the [endf-dtwdiff][endf-dtwdiff-url] tool.
The following paragraphs explain how these html files have been generated
using the scripts of this repository.
For all the following, please define an environment variable `FENDL_VERSION`
with the version number and `FENDL_OLD_VERSION` with the previous version.
This environment variables are used to display the proper version numbers
on the website.

#### Creating html files showing differences in ENDF files

First, for each ENDF file in the FENDL-ENDF repository, an html file can be
generated showing how the file content changed from one library version to
another one.
This can be achieved by executing `annexdiff.sh` in a specific mode.
Register this comparison mode as a difftool for git:
```
git config --global difftool.annexdiff.cmd '<PATH-TO-ANNEXDIFF>/annexdiff.sh difffile $BASE $LOCAL $REMOTE'
```
with `<PATH-TO-ANNEXDIFF>` being the absolute path of the script file.
Further, make sure that the command line tool [dtwdiff][endf-dtwdiff-url]
is available by appending its directory to your `PATH` variable.

Change into the root directory of the FENDL-ENDF repo.
From there run the instructions
```
mkdir diffdir
git difftool -t annexdiff <EARLIER-COMMIT> <LATER-COMMIT>
```
This command recreates the directory structure of the FENDL-ENDF repo inside
the `diffdir` directory. For each ENDF file in the repository, an html file
showing differences is created at the corresponding location inside the
`diffdir`. Please note that the creation of all diff files may take a while
(maybe about an hour).

#### Creating html files with summary tables

Next, an html file with a summary table of differences can be created for each
sublibrary. This table also contains the links to the diff files created
in the previous step. The following instructions have to be carried out for
each sublibrary individually and are only outlined for the neutron
sublibrary here.
Store the absolute path to the `FENDL-Code` directory in the environment
variable `FENDL_CODE_DIR`.
Being in the root directory of the FENDL-ENDF repo, execute
```
sublib=neutron
earliercommit=<EARLIER-COMMIT>
latercommit=<LATER-COMMIT>
cd general-purpose/$sublib
git diff --name-status $earliercommit $latercommit -- . > changes.txt
mv changes.txt ../../diffdir/general-purpose/$sublib/
cd ../..
export FENDL_TEMPLATE_DIR="$FENDL_CODE_DIR/templates"
python $FENDL_CODE_DIR/create_sublib_difftable.py diffdir/general-purpose/$sublib
```
Please note that the created html files are based on the
templates in the `templates` directory, which make use of the environment
variables `FENDL_VERSION` and `FENDL_OLD_VERSION` to display the version numbers.
It is important 

The content of the `diffdir` directory is now complete.
You can move this directory to a subfolder of the directory
given in the environment variable `FENDL_DATA_DIR` mentiond in
[the section](#copying-files-from-the-repository-to-the-website-data-directory)
on copying to the website data directory.
For the following, we assume that `diffdir` is a subfolder of `FENDL_DATA_DIR`.

Finally, the index.html files of the sublibraries can be created,
each listing the available target nuclides for a specific sublibrary.
Make sure that the environment variables `FENDL_DATA_DIR`,
`FENDL_TEMPLATE_DIR` are set. The environment variable `FENDL_DIFF_DIR`
must be set up to contain the path to `diffdir` relative to the path stored in
`FENDL_DATA_DIR`, i.e.,
```
export FENDL_DIFF_DIR='diffdir'
```
Now the index.html files of the sublibraries can be created by
```
python $FENDL_CODE/create_sublib_table_websites.py
```
Again, some strings in the templates need to be changed
to denote the correct library version.


[fendl-website]: https://www-nds.iaea.org/fendl/
[git-website]: https://git-scm.com/
[git-annex-website]: https://git-annex.branchable.com/
[cas-info-url]: https://en.wikipedia.org/wiki/Content-addressable_storage
[fendl-endf-repo]: https://github.com/IAEA-NDS/FENDL-ENDF
[fendl-proc-repo]: https://github.com/IAEA-NDS/FENDL-Processed
[yoda-url]: https://handbook.datalad.org/en/latest/basics/101-127-yoda.html
[git-annex-install-url]: https://git-annex.branchable.com/install/
[git-difftool-url]: https://git-scm.com/docs/git-difftool
[endf-dtwdiff-url]: https://github.com/gschnabel/endf-dtwdiff
[hash-wiki-url]: https://en.wikipedia.org/wiki/Cryptographic_hash_function

