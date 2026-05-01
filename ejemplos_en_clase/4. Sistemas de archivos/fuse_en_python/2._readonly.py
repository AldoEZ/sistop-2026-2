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

# This dictionary contains the filesystem data. Note that values *must
# be* of type `bytes`, not regular strings.
file_data = {
    "a_file": bytes("""My first file's contents.

Aren't they great? 😉
""", 'utf-8'),
    "second": bytes("Just some more stuff.", 'utf-8'),
    }

class ReadOnlyFS(Fuse):
    """Beginning FUSE, example 2: Read-only filesystem

    In this class we define all of the system calls our filesystem will
    support. For the most basic filesystem, we will implement only three
    system calls:

    readdir(path, offset)
        Iterates over the contents of the specified directory.

    getattr(path)
        Gets the attributes of the directory entry specified by "path"

    read(path, size, offset)
        Reads up to "size" bytes from file specified by "path", starting
        at byte "offset".
    """

    def readdir(self, path: str, offset: int):
        """Iterates over the contents of the specified directory.

        Yields (one by one) the name of each directory entry. In a
        "real" implementation, it should consider whether "path" refers
        to a real directory; for this toy implementation, the root
        directory is assumed.

        """

        for r in [ '.', '..' ] + list(file_data.keys()):
            yield fuse.Direntry(r)


    def getattr(self, path: str) -> fuse.Stat:
        """Gets the attributes of the directory entry specified by "path"

        For this toy implementation, path "/" will return enough
        permissions to enter and read a directory (0o555), and pathnames
        matching our defined files will return permission to be read
        (0o444). Creation/modification/access dates and other details
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

        for filename in file_data.keys():
            if path == "/" + filename:
                st.st_mode = stat.S_IFREG | 0o444
                st.st_nlink = 1
                st.st_size = len(file_data[filename])
                return st

        # Path does not match any known file objects
        return -errno.ENOENT

    def read(self, path: str, size: int, offset: int) -> bytes:
        """ Reads up to "size" bytes from file specified by "path"

        Parameters
        ----------
        path : str
            The name (path) of the requested file.

        size : int
            The maximum number of bytes this function will return.
            Defaults to reading to the end of the file.

        offset : int
            The number of bytes to skip from the beginning of the
            file. Defaults to 0.
        """
        found = False
        contents = None
        for filename in file_data.keys():
            if path == '/' + filename:
                found = True
                contents = file_data[filename]

        # Could not find the requested file
        if not found:
            return -errno.ENOENT

        slen = len(contents)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = contents[offset:offset+size]
        else:
            # If reading beyond the end of the file, return an empty byte
            # string.
            buf = b''

        return buf

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = 'Example 2: Static filesystem'
    descr = ("Presents a static filename with a couple of static \n" +
             "(immutable) files in it.")

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = ReadOnlyFS(version="%prog " + fuse.__version__,
                        usage=usage,
                        dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
