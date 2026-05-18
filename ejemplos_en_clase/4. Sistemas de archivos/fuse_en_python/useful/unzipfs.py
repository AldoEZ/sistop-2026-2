#!/usr/bin/python3
#
# Heavily based on Andrew Straw's (<strawman@astraw.com>) code from 2006.
#
# Distributed under the terms of the GNU LGPL 2.1 or, at your option,
# any newer

import os, stat, errno, fuse, sys
from fuse import Fuse
from datetime import datetime
from zipfile import ZipFile

# We need to declare the FUSE API Python compliance version. (0, 2) is
# defined in fuse.FUSE_PYTHON_API_VERSION.
fuse.fuse_python_api = (0, 2)

class UnzipFS(Fuse):
    """Beginning FUSE, "useful" example: Unzipping filesystem

    This example derives from the example 5 (read-only passthrough).

    In this class we define all of the system calls our filesystem will
    support. We need to implement read-only access, so we only implement
    the following system calls:

    readdir(path, offset)
        Iterates over the contents of the specified directory.

    getattr(path)
        Gets the attributes of the directory entry specified by "path"

    read(path, size, offset)
        Reads up to "size" bytes from file specified by "path", starting
        at byte "offset".
    """

    def __init__(self, *args, **kw):
        # The UnzipFS object gets initialized _before_ we have a chance to parse
        # the command line (that happens only until after parse() gets called on
        # the constructed object from the caller. We cannot do any sanity
        # validations at this point.
        fuse.Fuse.__init__(self, *args, **kw)

    def __archive_initialized__(self):
        if hasattr(self, 'zip'):
            return True
        self.zip = ZipFile(self.zip_file)

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
        self.__archive_initialized__()

        entries = ['.', '..']

        # Strip the leading '/' from the request
        path = path[1:]
        for filename in [i.filename for i in self.zip.filelist]:
            if len(path) > 0:
                # A subdirectory is being requested. Filter the filelist
                # accordingly.
                if not filename[0:len(path)+1] == (path + '/'):
                    continue
                else:
                    filename = filename[len(path)+1:]
                    if len(filename) == 0:
                        # Ignore the now-empty bare directory name.
                        continue

            # The filelist will include all directories. Include only the
            # relevant filenames for this directory.
            if '/' in filename:
                # If an entry includes a '/', check if it's the final
                # character. If so, report it, as it is a directory.
                if filename.index('/') == len(filename) - 1:
                    entries.append(filename[:-1])
                else:
                    #If it's midway through the filename, omit it, as it is
                    #deeper in the hierarchy.
                    pass
            else:
                # No '/' ? Good, this is a regular file.
                entries.append(filename)

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
        self.__archive_initialized__()

        # Note we will be getting the default (empty, zero) values for Stat()
        st = fuse.Stat()

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        try:
            filename = path[1:] # Strip the leading '/'
            now = float(datetime.now().strftime('%s'))
            try:
                info = self.zip.getinfo(filename)
                st.st_mode = stat.S_IFREG | 0o444
            except KeyError:
                # Maybe this is a directory? Add a trailing '/'. Otherwise, a
                # KeyError exception will be raised again, and catched further
                # down.
                info = self.zip.getinfo(filename + '/')
                st.st_mode = stat.S_IFDIR | 0o555
            st.st_dev = 0
            st.st_nlink = 1
            st.st_uid = os.getuid()
            st.st_gid = os.getuid()
            st.st_size = info.file_size
            st.st_atime = now
            st.st_mtime = now
            st.st_ctime = now
            return st

        except KeyError:
            return -errno.ENOENT

        # Path does not match any known file objects
        return -errno.ENOENT

    def read(self, path: str, size:int = -1, offset:int = 0) -> bytes:
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
        self.__archive_initialized__()

        if path[0] == '/':
            path = path[1:]

        return self.zip.read(path)

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = '"Useful" example 3: Unzipping filesystem'
    descr = ("Allows users to interact with the contents of a compressed\n" +
             "archive, without fully decompressing it (only retrieving the\n" +
             "required files on demand).")

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = UnzipFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parser.add_option(mountopt='zip_file',
                             metavar='ZIPFILE',
                             help='Zip file to mount (required)')

    args = server.parse(values=server, errex=1)

    # Zip file is a required argument
    try:
        filename = server.zip_file
    except AttributeError:
        sys.stderr.write("You must provide the 'zip_file' option via '-o'\n")
        exit(1)

    server.main()

if __name__ == '__main__':
    main()
