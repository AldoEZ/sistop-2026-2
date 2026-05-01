#!/usr/bin/python3
#
# Heavily based on Andrew Straw's (<strawman@astraw.com>) code from 2006.
#
# Distributed under the terms of the GNU LGPL 2.1 or, at your option,
# any newer

import os, stat, errno, fuse, sys
from datetime import datetime
from fuse import Fuse

# We need to declare the FUSE API Python compliance version. (0, 2) is
# defined in fuse.FUSE_PYTHON_API_VERSION.
fuse.fuse_python_api = (0, 2)

class FileData():
    """Holds the full information (data+metadata) for a file

    This structure holds all of the information for any of the given
    files in the filesystem. File metadata ("FileStat" entries) is
    available via the "stat" method, and file contents are available via
    the "contents" method.

    """
    def __init__(self, contents:bytes = b''):
        """Build a FileData object.

        Parameters
        ----------

        contents : bytes
            File contents. Must be of type "bytes" (not string!).
        """
        self.contents = contents
        self.stat = FileStat()
        self.stat.st_size = len(contents)
        self.stat.st_ctime = FileStat.epoch_now()
        self.stat.st_mtime = FileStat.epoch_now()

    def upd_access(self):
        """Updates the last access time for the file to now()"""
        self.stat.st_atime = FileStat.epoch_now()

    def upd_modif(self):
        """Updates the last modification time for the file to now()"""
        self.stat.st_mtime = FileStat.epoch_now()

class FileStat(fuse.Stat):
    """Represents the "stat" filesystem structure

    Files' metadata is represented in the "stat" structure; please check
    the documentation for understanding "stat()" results:

    https://docs.python.org/3/library/stat.html

    Entries instantiated by this class are set with "st_uid" and
    "st_gid" to the user running this process, and "st_ctime",
    "st_mtime" and "st_ctime" to the instance creation timestamp.

    """
    @classmethod
    def epoch_now(cls):
        return float(datetime.now().strftime('%s'))

    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = os.getuid()
        self.st_gid = os.getgid()
        self.st_size = 0
        self.st_atime = FileStat.epoch_now()
        self.st_mtime = FileStat.epoch_now()
        self.st_ctime = FileStat.epoch_now()

class WithDateHandlingFS(Fuse):
    """Read-and-modify-only filesystem with basic stat() handling

    In this class we define all of the system calls our filesystem will
    support. We now implement five system calls:

    readdir(path, offset)
        Iterates over the contents of the specified directory.

    getattr(path)
        Gets the attributes of the directory entry specified by "path"

    read(path, size, offset)
        Reads up to "size" bytes from file specified by "path", starting
        at byte "offset".

    truncate(path, length)
        Truncates the specified file to the given length (this might
        also mean growing it!)

    write(path, body, offset)
        Writes the given body to the file. It can be written at
        arbitrary positions of the file, using "offset".
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
        matching our defined files will return permission to be read and
        modified (0o644). Creation/modification/access dates and other
        details are left at 0 (at the beginning of the Unix Epoch).

        """

        # '/' is special-cased: It is not part of the filesystem's objects, but
        # it must have some stats
        if path == '/':
            st = FileStat()
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        for filename in file_data.keys():
            if path == "/" + filename:
                st = file_data[filename].stat
                st.st_mode = stat.S_IFREG | 0o644
                st.st_nlink = 1
                st.st_size = len(file_data[filename].contents)
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
        filename = path[1:] # drop leading "/"
        found = False
        contents = None

        # Update atime
        file_data[filename].upd_access

        for filename in file_data.keys():
            if path == '/' + filename:
                found = True
                contents = file_data[filename].contents

        # Could not find the requested file
        if not found:
            return -errno.ENOENT

        slen = len(contents)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = contents[offset:offset+size]
        else:
            # If reading beyond the end of the file, return an empty
            # byte string.
            buf = b''

        return buf

    def truncate(self, path: str, length: int):
        """Truncates the specified file to the given length.

        This function will adjust the file's size to whatever is
        specified via 'length'; the name "truncate" comes from Unix
        tradition, but it can also be used to very quickly grow a file
        to the desired size. If the destination length is smaller than
        the starting one, the contents will be truncated to fit; if it
        is larger, the file will be padded with as many times of
        character 0 (\x00) are needed.

        Parameters
        ----------
        path : str
            The name (path) of the file to truncate

        length : int
            The destination file size to set.

        """

        filename = path[1:] # drop leading "/"
        filesize = file_data[filename].stat.st_size
        contents = file_data[filename].contents

        if filesize < length:
            # Add as many \x00 bytes as needed to grow the string
            contents += bytearray(b'\x00' * (length - filesize))
        else:
            # Truncate to the requested size
            contents = file_data[filename].contents[0:length]

        file_data[filename].contents = contents
        file_data[filename].stat.fs_size = len(contents)
        file_data[filename].upd_modif()

    def write(self, path: str, body: bytes, offset: int):
        """Writes the given body to the specified file.

        The bytes received as "body" are replaced in the specified file.
        If an offset is specified, the new contents will happen starting
        at the indicated position.

        The original file length will not be modified unless the body
        length plus the offset are longer than it.

        Parameters
        ----------
        path : str
            The name (path) of the file to write to

        body : bytes
            The string of bytes to write

        offset : int
            The position of the file to start writing a

        """

        filename = path[1:] # drop leading "/"
        contents = file_data[filename].contents
        dest = b''
        if offset > 0:
            dest += contents[0:offset]
        dest += body
        if len(contents) > offset + len(body):
            dest += contents[(offset+len(body)):]

        file_data[filename].contents = dest
        file_data[filename].stat.st_size = len(dest)
        file_data[filename].upd_modif()

        return len(body)

file_data = {
    "a_file": FileData(bytes("""My first file's contents.

Aren't they great? 😉
""", 'utf-8')),
    "second": FileData(bytes("Just some more stuff.", 'utf-8')),
    }

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = 'Example 4: Now stat() makes sense!'
    descr = ("Presents a static set filenames, with modifiable \n" +
             "contents, and with file information in stat() that \n" +
             "actually makes sense.")

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = WithDateHandlingFS(version="%prog " + fuse.__version__,
                                usage=usage,
                                dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
