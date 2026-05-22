#!/usr/bin/python3
#
# Heavily based on Andrew Straw's (<strawman@astraw.com>) code from 2006.
#
# Distributed under the terms of the GNU LGPL 2.1 or, at your option,
# any newer

import os, stat, errno, fuse, sys
from fuse import Fuse

# We need to declare the FUSE API Python compliance version. (0, 2) is
# defined in fuse.FUSE_PYTHON_API_VERSION.
fuse.fuse_python_api = (0, 2)


class EmptyFS(Fuse):
    """0. Empty filesystem

    As a very very very first example, lets begin with the most minimal
    correct filesystem we can think of: One that can be validly mounted,
    and that holds the special '.' and '..' directory entries.

    For the most basic filesystem, we will implement only two
    system calls:

    readdir(path, offset)
        Iterates over the contents of the specified directory.

    getattr(path)
        Gets the attributes of the directory entry specified by "path".

    """

    def readdir(self, path: str, offset: int):
        """Iterates over the contents of the specified directory.

        So far, this only means the empty directories needed by any
        filesystem, «.» (current directory) and «..» (parent directory).

        """

        for r in [ '.', '..' ]:
            yield fuse.Direntry(r)


    def getattr(self, path: str) -> fuse.Stat:
        """Gets the attributes of the directory entry specified by "path"

        For this toy implementation, path "/" will return enough
        permissions to enter and read a directory
        (0o555). Creation/modification/access dates and other details
        are left at 0 (at the beginning of the Unix Epoch).

        Do note that any received `path` argument will be rooted (will
        be preceded by “/”) at our filesystem's root.

        """

        # Note we will be getting the default (empty, zero) values for Stat()
        st = fuse.Stat()

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        # Path does not match any known file objects
        return -errno.ENOENT

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = 'Example 1: Empty filesystem'
    descr = """Presents an empty filesystem that cannot be read from or
written to, but exists. Of course, this is just the very first step."""

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = EmptyFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
