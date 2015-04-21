from os import path
import os
import io
import re
import zipfile, tarfile
import functools
from StringIO import StringIO
import urllib

class GreenplumDistributed(object):
    @staticmethod
    def from_source(installer_path, tmp_dir=None):
        """Create a GreenplumDistributed from a source path.

        installer_path -- Path to the distributed zip archive.
        tmp_dir -- Temporary directory to store the archive if it needs to be downloaded from a URL.  Optional.

        The installer_path can be either a local filepath or URL (one which can be downloaded by urllib).
        """

        if tmp_dir == None:
            import tempfile
            tmp_dir = tempfile.mkdtemp()

        # Attempt to locate locallay
        if path.exists(installer_path):
            return GreenplumDistributed(installer_path)

        # Attempt to download URL
        try:
            tmp_path = path.join(tmp_dir, 'greenplum-db.zip')
            urllib.urlretrieve(installer_path, tmp_path)

            return GreenplumDistributed(tmp_path)
        except IOError:
            pass

        # Default to erroring if none of the above retrieval methods were successful.
        raise LookupError('Could not find greenplum installer at %s' % installer_path)

    def __init__(self, path):
        self.__path = path
        self.__archive = None

    def __enter__(self):
        # Open and cache installer archive handler.
        return self.get_installer()

    def __exit__(self):
        self.close()

    def __del__(self):
        self.close()

    def get_installer(self):
        installer_file = GreenplumInstaller.find_installer_name(map(lambda fileinfo: fileinfo.filename, self.__get_archive().infolist()))

        if len(installer_file) != 1:
            raise StandardError('Incorrect number of installer scripts found in referenced greenplum installation archive.  Found %s, expected 1.  Scripts found: ' % (len(installer_file), ", ".join(installer_file)))

        installer_file = installer_file[0]

        return GreenplumInstaller(installer_file, self.__get_archive().read(installer_file))

    def close(self):
        if self.__archive != None:
            self.__archive.close()

    def __get_archive(self):
        if self.__archive == None:
            self.__archive = zipfile.ZipFile(self.__path, 'r')

        return self.__archive

class GreenplumInstaller(object):
    INSTALLER_SCRIPT_FILE_REGEX = re.compile(r"greenplum-db-(?P<version>[0-9\.]+)[^/]+\.bin$")

    @classmethod
    def find_installer_name(cls, filelist):
        """Given a list of filenames, return the ones which would install greenplum."""

        return filter(functools.partial(lambda cls, filename: cls.INSTALLER_SCRIPT_FILE_REGEX.search(filename) != None, cls), filelist)

    def __init__(self, filename, file_contents = None):
        self.__filename = filename
        self.__fileContents = file_contents
        self.__version = self.__parse_version(filename)

    def __enter__(self):
        return self.__get_archive()

    def __exit__(self):
        self.close()

    def install_to(self, destination):
        archive = self.__get_archive()
        archive.extractall(destination)
        archive.close()

    def get_name(self):
        return self.__filename

    def get_version(self):
        return self.__version

    def close(self):
        if self.__archive != None:
            self.__archive.close()

    def __get_archive(self):
        installer_script_stream = StringIO(self.__get_installer_as_string())

        # Seek to the line before the archive's binary data starts.
        seekedToLine = False
        for line in iter(installer_script_stream.readline, b''):
            if line == "__END_HEADER__\n":
                seekedToLine = True
                break

        if not seekedToLine:
            raise StandardError('Could not find archive contents, archive extraction failed.')

        # Return a TarFile of the remaining lines in the installer script.
        return tarfile.open(fileobj = installer_script_stream, mode = "r:gz")

    def __get_installer_as_string(self):
        if self.__fileContents == None:
            with open(self.__filename, 'r') as filehandle:
                self.__fileContents = filehandle.read()

        return self.__fileContents

    def __parse_version(self, filename):
        try:
            matches = self.INSTALLER_SCRIPT_FILE_REGEX.search(filename)

            return matches.group('version')
        except StandardError:
            raise StandardError('Could not parse greenplum version from given filename %s' % filename)