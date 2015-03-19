from os import path
import io
import zipfile, tarfile
from StringIO import StringIO
import urllib

def get_tar(installation_source):
    greenplum_installer_archive_path = _fetch_greenplum_installer_path(installation_source)
    greenplum_installer_script = _get_installer_stream_from_archive(greenplum_installer_archive_path)

    return _get_tar_stream_from_installer_script(greenplum_installer_script)

def _fetch_greenplum_installer_path(installer_path):
    if path.exists(installer_path):
        if not path.isfile(installer_path):
            raise LookupError('Could not find greenplum installer at %s' % installer_path)
        return installer_path

    tmpPath = path.join(params.tmp_dir, 'greenplum-db.zip')
    urllib.urlretrieve(installer_path, tmpPath)

    return tmpPath

def _get_installer_stream_from_archive(installer_archive):
    archive = None

    # ON_UPGRADE: Can't use with for archive in Python 2.6.6, fix when python version is bumped.
    try:
        archive = zipfile.ZipFile(installer_archive, 'r')

        installer_archive_path = filter(lambda f: f.filename.endswith('.bin'), archive.infolist())

        if len(installer_archive_path) != 1:
            raise StandardError('Incorrect number of .bin files found in referenced greenplum installation archive.  Found %s, expected 1.' % (len(installer_archive_path)))
        installer_archive_path = installer_archive_path[0]

        return archive.read(installer_archive_path)
    finally:
        if archive != None:
            archive.close()

def _get_tar_stream_from_installer_script(installerScript):
    installer_script_stream = StringIO(installerScript)

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