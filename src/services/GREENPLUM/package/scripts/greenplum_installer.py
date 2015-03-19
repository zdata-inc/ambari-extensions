from os import path
import os
import io
import re
import zipfile, tarfile
from StringIO import StringIO
import urllib

def get_tar(installation_source):
    """
    Get a tarfile resource from the installation script inside a distributed greenplum installation zip.
    """
    greenplum_installer_archive_path = _get_greenplum_installer_path(installation_source)
    greenplum_installer_script = _get_installer_stream_from_archive(greenplum_installer_archive_path)

    return _get_tar_stream_from_installer_script(greenplum_installer_script)

def get_version(installation_source):
    """
    Get the version of a distributed greenplum installation zip.
    """
    greenplum_installer_archive_path = _get_greenplum_installer_path(installation_source)

    return _get_version_from_archive(greenplum_installer_archive_path)

def _get_version_from_archive(installer_archive):
    """
    Retrieve the version from a distributed greenplum installation zip.
    This is done by find the installer script in the zip archive, and extracting the
    version from its filename.
    """
    greenplum_installer_archive_path = _get_greenplum_installer_path(installation_source)
    installer_name = _get_greenplum_installer_name(greenplum_installer_archive_path).filename

    return _get_version_from_filename(installer_name)

def _get_greenplum_installer_path(installer_path):
    """
    Given an installer path or URI, verify it exists and provide a path to.
    If the installer_path is a path, verify it exists and return the path.
    If the installer_path is a URI, materialize it into a temporary directory, correctly name it, and return the path.
    """
    import params

    if path.exists(installer_path):
        if not path.isfile(installer_path):
            raise LookupError('Could not find greenplum installer at %s' % installer_path)
        return installer_path

    tmpPath = path.join(params.tmp_dir, 'greenplum-db.zip')
    urllib.urlretrieve(installer_path, tmpPath)

    version = _get_version_from_archive(tmpPath)
    tmpPathWithVersion = path.join(params.tmp_dir, 'greenplum-db-%s.zip' % version)
    os.rename(tmpPath, tmpPathWithVersion)

    return tmpPathWithVersion

def _get_installer_stream_from_archive(installer_archive):
    """
    Retrieve the contents of the installer file from the distributed greenplum installation zip.
    """
    try:
        archive, should_close = _maybe_open_zip(installer_archive)
        return archive.read(_get_greenplum_installer_name(archive))
    finally:
        if should_close and archive != None:
            archive.close()

def _get_greenplum_installer_name(installer_archive):
    """
    Retrieve the name of the installer file from the distributed greenplum installation zip.
    """
    try:
        installer_archive, should_close = _maybe_open_zip(installer_archive)
        installer_archive_path = filter(lambda f: f.filename.endswith('.bin'), installer_archive.infolist())

        if len(installer_archive_path) != 1:
            raise StandardError('Incorrect number of .bin files found in referenced greenplum installation archive.  Found %s, expected 1.' % len(installer_archive_path))

        return installer_archive_path[0]
    finally:
        if should_close and installer_archive != None:
            installer_archive.close()

def _get_tar_stream_from_installer_script(installer_script):
    """
    Given a string containing the greenplum installation script, parse out
    the appended tar file and return it as a TarFile instance.
    """
    installer_script_stream = StringIO(installer_script)

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

def _get_version_from_filename(filename):
    """
    Given the .bin filename for greenplum, extract its version
    from the filename.
    """
    matches = re.search(r"greenplum-db-([0-9\.]+)[^/]+\.bin", filename)

    return matches.group(1)

def _maybe_open_zip(stream_or_path):
    if isinstance(stream_or_path, basestring) and path.isfile(stream_or_path):
        return zipfile.ZipFile(stream_or_path, 'r'), True

    return stream_or_path, False