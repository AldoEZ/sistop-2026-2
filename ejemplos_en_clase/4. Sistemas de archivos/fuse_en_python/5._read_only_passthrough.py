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

class ReadOnlyPassthroughFS(Fuse):
    """Beginning FUSE, example 5: Read-only passthrough filesystem

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

    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.src_dir = '.'

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

        entries = ['.', '..']
        entries.extend([i.name for i in os.scandir(self.src_dir + path)])

        for item in entries:
            yield fuse.Direntry(item)


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

        filename = self.src_dir + '/' + path[1:]
        if os.path.exists(filename):
            real_st = os.stat(filename)
            st.st_mode = real_st.st_mode & 0o777555
            st.st_dev = real_st.st_dev
            st.st_nlink = real_st.st_nlink
            st.st_uid = real_st.st_uid
            st.st_gid = real_st.st_gid
            st.st_size = real_st.st_size
            st.st_atime = real_st.st_atime
            st.st_mtime = real_st.st_mtime
            st.st_ctime = real_st.st_ctime
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
        fh = None
        filename = self.src_dir + '/' + path[1:]

        if os.path.isfile(filename):
            found=True
            fh = open(filename, 'rb')
            if not fh.readable():
                return -errno.EACCES

        # Could not find the requested file
        if not found:
            return -errno.ENOENT

        fh.seek(offset)
        return fh.read(size)

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = 'Example 4: Overlaid, read-only filesystem'
    descr = ("Presents an overlaid filesystem, with a read-only view\n" +
             "of the directory from where it is called")

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = ReadOnlyPassthroughFS(version="%prog " + fuse.__version__,
                               usage=usage,
                               dash_s_do='setsingle')

    server.parser.add_option(
        mountopt = 'src_dir',
        metavar = 'SRCDIR',
        default = '.',
        help="Real directory to pass through (defaults to '%default')"
    )

    server.parse(values=server, errex=1)

    # If the source directory is not absolute, resolve it.
    if server.src_dir[0] != '/':
        server.src_dir = os.path.abspath(server.src_dir)

    server.main()

if __name__ == '__main__':
    main()
