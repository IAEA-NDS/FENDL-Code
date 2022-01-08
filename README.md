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
the symbolic link contains a cryptograhpic hash and it
is therefore always possible to verify if a given file
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
about the file location so long as the file is stored somewhere.


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
cd FENDL-Processed/fendl-endf/general-purpose/neutron`.
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
An environment variables `FENDL_REPO_DIR` must be set to point to the
root directory of the FENDL-Processed repository. Another environment
variable `FENDL_DATA_DIR` must be set to point to an empty directory
where the data files are copied to. In practice, this script has been
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

[fendl-website]: https://www-nds.iaea.org/fendl/
[git-website]: https://git-scm.com/
[git-annex-website]: https://git-annex.branchable.com/
[cas-info-url]: https://en.wikipedia.org/wiki/Content-addressable_storage
[fendl-endf-repo]: https://github.com/IAEA-NDS/FENDL-ENDF
[fendl-proc-repo]: https://github.com/IAEA-NDS/FENDL-Processed
[yoda-url]: https://handbook.datalad.org/en/latest/basics/101-127-yoda.html
[git-annex-install-url]: https://git-annex.branchable.com/install/
[git-difftool-url]: https://git-scm.com/docs/git-difftool
