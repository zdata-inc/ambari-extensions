from os import path
import os
import io
import re
import zipfile, tarfile
from StringIO import StringIO
import urllib

class GreenplumDistributed(object):
    def __init__(self, path, tmp_dir):
        self.__materialized_path = self.__materialize_archive(path, tmp_dir)
        self.__archive = None

    def get_installer(self):
        installer_file = GreenplumInstaller.find_installer_name(self.__get_archive().infolist())

        if len(installer_file) != 1:
            raise StandardError('Incorrect number of .bin files found in referenced greenplum installation archive.  Found %s, expected 1.' % len(installer_file))

        installer_file = installer_file[0]

        return GreenplumInstaller(installer_file, self.__get_archive().read(installer_file))        

    def close(self):
        if self.__archive != None:
            self.__archive.close()

    def __del__(self):
        self.close()

    def __get_archive(self):
        if self.__archive == None:
            self.__archive = zipfile.ZipFile(self.__materialized_path, 'r')

        return self.__archive

    def __materialize_archive(self, source, tmp_dir):
        if path.exists(source):
            if not path.isfile(source):
                raise LookupError('Could not find greenplum installer at %s' % source)
            return source

        tmp_path = path.join(tmp_dir, 'greenplum-db.zip')
        urllib.urlretrieve(source, tmp_path)

        version = _get_version_from_archive(tmp_path)
        tmp_path_with_version = path.join(tmp_dir, 'greenplum-db-%s.zip' % version)
        os.rename(tmp_path, tmp_path_with_version)

class GreenplumInstaller(object):
    @staticmethod
    def find_installer_name(filelist):
        """
        Given a list of ZipFileInfo objects, return the ones which would install greenplum.
        """
        return filter(lambda f: f.filename.endswith('.bin'), filelist)

    def __init__(self, filename, fileContents):
        self.__filename = filename
        self.__fileContents = fileContents
        self.__version = self.__parse_version(filename)

    def install_to(self, destination):
        archive = self.__get_archive()
        archive.extractall(destination)
        archive.close()

    def get_name(self):
        return self.__filename

    def get_version(self):
        return self.__version

    def __get_archive(self):
        installer_script_stream = StringIO(self.__fileContents)

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

    def __parse_version(self, filename):
        try:
            matches = re.search(r"greenplum-db-([0-9\.]+)[^/]+\.bin", filename)

            return matches.group(1)
        except StandardError:
            raise StandardError('Could not parse greenplum version from given filename %s' % filename)