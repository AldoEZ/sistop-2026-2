#!/usr/bin/python3
#
# Heavily based on Andrew Straw's (<strawman@astraw.com>) code from 2006.
#
# Distributed under the terms of the GNU LGPL 2.1 or, at your option,
# any newer

import os, stat, errno, fuse, sys, DNS
from fuse import Fuse

# We need to declare the FUSE API Python compliance version. (0, 2) is
# defined in fuse.FUSE_PYTHON_API_VERSION.
fuse.fuse_python_api = (0, 2)

class DNSFS(Fuse):
    """Beginning FUSE, "useful" example: DNS Filesystem

    This example is derived from the example 2 (Read-only filesystem)

    In this class we define all of the system calls our filesystem will
    support. This is a filesystem that allows querying DNS, so the
    information it provides is inherently read-only. Thus, it implements
    only the three following syscalls:

    readdir(path, offset)
        Iterates over the contents of the specified directory.

    getattr(path)
        Gets the attributes of the directory entry specified by "path"

    read(path, size, offset)
        Reads up to "size" bytes from file specified by "path", starting
        at byte "offset".

    """

    def _qry_types(self):
        """List of query types this module performs

        There are many other query types¹, but we chose to suport only
        the most common six ones.

        ¹ https://en.wikipedia.org/wiki/List_of_DNS_record_types

        """

        return ['A', 'AAAA', 'CNAME', 'MX', 'PTR', 'TXT']

    def _lookup(self, qry: str, qry_type: str):
        """Perform the actual DNS lookup, return it as a bytes object

        Will return one answer per line (separated by "\n", utf-8
        encoded as bytes). Returns an empty object if no answers are
        found for the query.

        Parameters
        ----------
        qry : str
            The object to query DNS for

        qry_type : str
            The type of query to perform. Must be one of the types
            returned by self._qry_types().
        """

        if not qry_type in self._qry_types():
            return b''

        data = DNS.dnslookup(qry, qry_type)
        # dnslookup returns an array. Lets make results less ugly ;-)
        if len(data) == 0:
            # Zero-elements answer should yield an empty file
            return b''
        else:
            # Answers should be stringified, one item per line
            res = ''
            for item in data:
                res += item.__str__() + "\n"

        return bytes(res, 'utf-8')

    def _readme(self):
        return bytes("""DNS Filesystem
--------------

In this directory, You will find this README plus several
directories. Each directory stands for a supported DNS record type (A
for IPv4 name resolution, AAAA for IPv6, etc.)

The directories are empty. But don't let that discourage you! Do a query
by reading the file matching the record type you want to retrieve. For
example:

    $ cat A/linux.org
    104.26.14.72
    104.26.15.72
    172.67.73.26

Of course, the values returned might have changed.

This filesystem is provided as a toy project, aiming to teach some ideas
about writing modules in FUSE. Go learn from its source! 😉

   - Gunnar Wolf <gwolf@gwolf.org>
""", 'utf-8')

    def readdir(self, path: str, offset: int):
        """Iterates over the contents of the specified directory.

        Yields (one by one) the name of each directory entry. In a
        "real" implementation, it should consider whether "path" refers
        to a real directory; for this toy implementation, the root
        directory is assumed.

        Parameters
        ----------
        path : str
            The full path (from the filesystem root) for the directory
            to be queried

        offset : int
            Ignored in the current implementation
        """
        contents = [ '.', '..' ]
        if path == '/':
            contents.append('README')
            contents.extend(self._qry_types())

        # Direntries' data are handled by getattr()
        for r in contents:
            yield fuse.Direntry(r)

    def getattr(self, path: str) -> fuse.Stat:
        """Gets the attributes of the directory entry specified by "path"

        All predefined files, as well as the directories, are taken to
        be immutable. Queries inside the lookup directories can be made,
        and even if the files are not part of the directory yielded by
        self.readdir():

            $ ls -hl mnt/A/python.org
            -r--r--r-- 1 root root 512 Dec 31  1969 mnt/A/python.org

        File attributes are not meaningful: ctime/atime/mtime are at the
        beginning of the epoch; file size is 512 bytes (the limit for
        UDP DNS packets).

        Parameters
        ----------
        path : str
            The full file path (from the filesystem root) being
            queried for
        """

        # Note we will be getting the default (empty, zero) values for Stat()
        st = fuse.Stat()

        dirs = [ '/%s' % i for i in self._qry_types() ]
        dirs.extend('/')
        if path in dirs:
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        if path == '/README':
            st.st_mode = stat.S_IFREG | 0o444
            st.st_nlink = 1
            st.st_size = len(self._readme())
            return st

        try:
            # extract query type and query from the path: Drop the first
            # character ('/' for the filesystem root), find the index
            # for the next '/', and split the string
            idx = path[1:].index('/')
            qry_type = path[1:idx+1]
            if qry_type in self._qry_types():
                st.st_mode = stat.S_IFREG | 0o444
                st.st_nlink = 1
                st.st_size = 512
                return st
        except ValueError:
            return -errno.ENOENT

        # Path does not match any known file objects
        return -errno.ENOENT

    def read(self, path: str, size: int, offset: int) -> bytes:
        """ Reads up to "size" bytes from file specified by "path"

        Parameters
        ----------
        path : str
            The name (path) of the requested file.

        size : int
            Ignored in this implementation (whole entry will be returned)

        offset : int
            Ignored in this implementation (whole entry will be returned)
        """

        if path == '/README':
            return self._readme()

        try:
            idx = path[1:].index('/')
            qry_type = path[1:idx+1]
            qry = path[idx+2:]
            return self._lookup(qry, qry_type)
        except ValueError:
            return -errno.ENOENT

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = '"Useful" example 1: DNS Filesystem'
    descr = """Presents a filesystem for resolving DNS queries.

Derived from the "2._readonly.py" filesystem example as the first
useful and non-obvious FUSE example.

For further information, mount it and read the README file!
"""
    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = DNSFS(version="%prog " + fuse.__version__,
                        usage=usage,
                        dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
