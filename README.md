# ldv
Light Data Versioning

Ldv is a tool for version tracking big files on a remote storage and storing digest files together with code that uses the big files.
A digest file is a small file containing information about the file to version track. The information includes file size in bytes, timestamp of version, hexdigest (the version number), and local and remote filepaths.

Ldv can be run from the command line or from code, using the APIs of the package.

Ldv has no external dependencies on other programs, e.g. Git.
