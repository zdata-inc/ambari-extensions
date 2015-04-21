from __future__ import with_statement
import os, re
import urllib
import zipfile, tarfile
import shutil
import tempfile
import functools
from StringIO import StringIO
from resource_management import *

class GreenplumDistributed(object):
    @staticmethod
    def make_tmpfile(tmp_dir=None):
        """Create a temporary named file and return its path."""

        filehandle, tmp_path = tempfile.mkstemp(dir=tmp_dir)
        os.close(filehandle) # Don't need a filehandle
        return tmp_path

    @classmethod
    def from_source(cls, installer_path, tmp_dir=None):
        """Create a GreenplumDistributed from a source path.

        installer_path -- Path to the distributed zip archive.
        tmp_dir -- Where to store temporary files.  Uses system temporary directory by default.

        The installer_path can be either a local filepath or URL (one which can be downloaded by urllib).
        """

        tmp_path = cls.make_tmpfile(tmp_dir)

        # Attempt to locate locallay
        if os.path.exists(installer_path):
            return GreenplumDistributed(installer_path)

        # Attempt to download URL
        try:
            Logger.info('Downloading Greenplum from %s to %s.' % (installer_path, tmp_path))
            urllib.urlretrieve(installer_path, tmp_path)

            return GreenplumDistributed(tmp_path, True)
        except IOError:
            pass

        # Default to erroring if none of the above retrieval methods were successful.
        raise ValueError('Could not find greenplum installer at %s' % installer_path)

    def __init__(self, file_path, is_temporary=False):
        # If the archive is temporary or not.  If it is it'll be removed during cleanup.
        self.__delete_archive_on_close = is_temporary

        self.__file_path = file_path
        self.__archive = None

    def __enter__(self):
        # Open and cache installer archive handler.
        return self

    def __exit__(self, type, value, trace):
        self.close()

    def __del__(self):
        self.close()

        if self.__delete_archive_on_close and os.path.exists(self.__file_path):
            Logger.info('Removing temporary Greenplum file %s.' % self.__file_path)
            os.remove(self.__file_path)

    def get_installer(self):
        """Extract the installation script from the distributed zip file and return it as a GreenplumInstaller."""

        installer_file = GreenplumInstaller.find_installer_name(map(lambda fileinfo: fileinfo.filename, self.__get_archive().infolist()))

        if len(installer_file) != 1:
            raise StandardError('Incorrect number of installer scripts found in referenced greenplum installation archive.  Found %s, expected 1.  Scripts found: ' % (len(installer_file), ", ".join(installer_file)))

        installer_file = installer_file[0]
        installer_tmp_file = self.make_tmpfile()

        # Extract installer file to a temporary file.
        # Can't use extract as it attempts to keep the compressed file's name.
        with file(installer_tmp_file, 'wb') as target:
            source = self.__get_archive().open(installer_file)
            shutil.copyfileobj(source, target)

        return GreenplumInstaller(installer_file, installer_tmp_file, True)

    def close(self):
        if self.__archive != None:
            self.__archive.close()

    def __get_archive(self):
        if self.__archive == None:
            self.__archive = zipfile.ZipFile(self.__file_path, 'r')

        return self.__archive

class GreenplumInstaller(object):
    INSTALLER_SCRIPT_FILE_REGEX = re.compile(r"greenplum-db-(?P<version>[0-9\.]+)[^/]+\.bin$")

    @classmethod
    def find_installer_name(cls, filelist):
        """Given a list of filenames, return the ones which would install greenplum."""

        return filter(functools.partial(lambda cls, filename: cls.INSTALLER_SCRIPT_FILE_REGEX.search(filename) != None, cls), filelist)

    def __init__(self, filename, file_path = None, is_temporary=False):
        self.__filename = filename
        self.__file_path = file_path
        self.__version = self.__parse_version(filename)
        self.__delete_archive_on_close = is_temporary
        self.__archive = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()

    def __del__(self):
        self.close()

        if self.__delete_archive_on_close and os.path.exists(self.__file_path):
            Logger.info('Removing temporary Greenplum file %s.' % self.__file_path)
            os.remove(self.__file_path)

    def install_to(self, destination):
        """Install this version of Greenplum into the given destination directory."""

        archive = self.__get_archive()
        archive.extractall(destination)

    def get_name(self):
        """Get the name of the installation script."""
        return self.__filename

    def get_version(self):
        """Get the version of Greenplum the installation script will install."""
        return self.__version

    def close(self):
        if self.__archive != None:
            self.__archive.close()

        self.__archive = None

    def __get_archive(self):
        """Lazy load and return installation archive."""
        if self.__archive != None:
            return self.__archive

        installer_script_stream = self.__get_installer_stream()

        # Seek to the line before the archive's binary data starts.
        seekedToLine = False
        for line in iter(installer_script_stream.readline, b''):
            if line == "__END_HEADER__\n":
                seekedToLine = True
                break

        if not seekedToLine:
            raise StandardError('Could not find archive contents, archive extraction failed.')

        # Return a TarFile of the remaining lines in the installer script.
        self.__archive = tarfile.open(fileobj = installer_script_stream, mode = "r:gz")

        return self.__archive

    def __get_installer_stream(self):
        return open(self.__file_path, 'r')

    def __parse_version(self, filename):
        try:
            matches = self.INSTALLER_SCRIPT_FILE_REGEX.search(filename)

            return matches.group('version')
        except StandardError:
            raise StandardError('Could not parse greenplum version from given filename %s' % filename)