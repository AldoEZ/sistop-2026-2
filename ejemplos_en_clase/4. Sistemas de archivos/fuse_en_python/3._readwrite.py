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

class ReadWriteExistingFS(Fuse):
    """Beginning FUSE, example 3: Read-and-modify-only (no
    directory-level operations) filesystem

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
        permissions to enter, read and write a directory (0o555), and
        pathnames matching our defined files will return permission to be
        read and modified (0o644). Creation/modification/access dates and
        other details are left at 0 (at the beginning of the Unix Epoch).

        """

        # Note we will be getting the default (empty, zero) values for Stat()
        st = fuse.Stat()

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        for filename in file_data.keys():
            if path == "/" + filename:
                st.st_mode = stat.S_IFREG | 0o644
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
        filesize = len(file_data[filename])

        if filesize < length:
            # Add as many \x00 bytes as needed to grow the string
            file_data[filename] += bytearray(b'\x00' * (length - filesize))
        else:
            # Truncate to the requested size
            file_data[filename] = file_data[filename][0:length]

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
        contents = file_data[filename]
        dest = b''

        if offset > 0:
            dest += contents[0:offset]
        dest += body
        if len(contents) > offset + len(body):
            dest += contents[(offset+len(body)):]

        file_data[filename] = dest

        return len(body)

def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    title = 'Example 3: Static filenames, modifiable contents'
    descr = ("Presents a static set of filenames, but their contents\n" +
             "can be modified.")

    usage = ("\n\nBeginning FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = ReadWriteExistingFS(version="%prog " + fuse.__version__,
                                 usage=usage,
                                 dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
