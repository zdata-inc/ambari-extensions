from os import path
import urllib
from resource_management import *
from pprint import pprint
import utilities

def install(env):
    preinstallation_configure(env)



    postinstallation_configure(env)

def initialize(env):
    pass

def preinstallation_configure(env):
    import params

    User(
        params.admin_user,
        action="create", shell="/bin/bash"
    )

    # Create installation directory
    Directory(
        params.installation_path,
        action="create",
        owner=params.admin_user, mode=0755
    )

    # Create data directories, mirror directories
    Directory(
        params.data_directories() + params.mirror_data_directories(),
        action="create",
        recursive=True,
        owner=params.admin_user, mode=0755
    )

    # Create segment file
    TemplateConfig(
        path.join(params.installation_path, 'greenplum_segments'),
        owner=params.admin_user, mode=0644
    )

def postinstallation_configure(env):
    pass


def _fetchGreenplumInstaller(env):
    import params

    if params.installer_location.exists(params.installer_location):
        return params.installer_location

    tmpPath = path.join(params.tmp_dir, 'greenplum-db.zip')
    urllib.urlretrieve(params.installer_location, tmpPath)

    return tmpPath