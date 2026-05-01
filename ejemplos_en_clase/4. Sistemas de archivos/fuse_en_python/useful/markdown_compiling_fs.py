#!/usr/bin/python3
#
# Heavily based on Andrew Straw's (<strawman@astraw.com>) code from 2006.
#
# Distributed under the terms of the GNU LGPL 2.1 or, at your option,
# any newer

import os, stat, errno, fuse, sys, subprocess
from fuse import Fuse

# We need to declare the FUSE API Python compliance version. (0, 2) is
# defined in fuse.FUSE_PYTHON_API_VERSION.
fuse.fuse_python_api = (0, 2)

class MarkdownCompilingFS(Fuse):
    """Beginning FUSE, "useful" example: Markdown compiling filesystem

    This example is derived from the example 5 (read-only passthrough).

    In this class we define all of the system calls our filesystem will
    support. This filesystem is implemented as a pass-through; it still
    requires only the three following system calls:

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

        If a Markdown file is found (`*.md`), an additional matching
        HTML file is presented.

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
            if item[-3:] == '.md':
                yield fuse.Direntry(item[:-3] + '.html')
            yield fuse.Direntry(item)


    def getattr(self, path: str) -> fuse.Stat:
        """Gets the attributes of the directory entry specified by "path"

        All of the attributes will be passed through from the underlying
        filesystem.  Extra entries  will be  created for  `*.html` files
        for which there is a matching `*.md` file in the filesystem.

        Do note that any received `path` argument will be rooted (will
        be preceded by “/”) at our filesystem's root.

        Parameters
        ----------
        path : str
            The full file path (from the filesystem root) being
            queried for
        """

        # Note we will be getting the default (empty, zero) values for Stat()
        st = fuse.Stat()

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        filename = self.src_dir + '/' + path[1:]
        compiling = False

        if filename[-5:] == '.html' and not os.path.exists(filename):
            compiling = True
            filename = filename[:-5] + '.md'

        if os.path.exists(filename):
            real_st = os.stat(filename)
            st.st_mode = real_st.st_mode & 0o777555
            st.st_dev = real_st.st_dev
            st.st_nlink = real_st.st_nlink
            st.st_uid = real_st.st_uid
            st.st_gid = real_st.st_gid
            if compiling:
                # Will almost certainly be less than double, but this
                # avoids stopping with a short-read
                st.st_size = real_st.st_size * 2
            else:
                st.st_size = real_st.st_size
            st.st_atime = real_st.st_atime
            st.st_mtime = real_st.st_mtime
            st.st_ctime = real_st.st_ctime
            return st

        # Path does not match any known file objects
        return -errno.ENOENT

    def read(self, path: str, size: int, offset: int) -> bytes:
        """Reads up to "size" bytes from file specified by "path"

        If the compiled `*.html` file for a matching `*.md` file is
        requested, it will be compiled each time it is `read()`.

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

        if filename[-5:] == '.html' and os.path.exists(filename[:-5] + '.md'):
            mdfile = filename[:-5] + '.md'
            data = subprocess.check_output(['markdown', mdfile])

            return data

        # Could not find the requested file
        if not found:
            return -errno.ENOENT

        fh.seek(offset)
        return fh.read(size)

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = ('"Useful" example 2: Markdown-compiling, overlaid, ' +
             'read-only filesystem')
    descr = ("Presents an overlaid filesystem, with a read-only view\n" +
             "of the directory from where it is called. Compiled \n" +
             "`*.html` files will be presented for existing `*.md` \n" +
             "(Markdown) files.")

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = MarkdownCompilingFS(version="%prog " + fuse.__version__,
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
