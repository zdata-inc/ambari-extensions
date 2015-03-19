from os import path
import urllib
from resource_management import *
from pprint import pprint
import utilities
import greenplum_installer

def install(env):
    import params

    try:
        # ON_UPGRADE: Switch to using with keyword with greenplum_tar
        greenplum_tar = greenplum_installer.get_tar(params.installer_location)
        greenplum_tar.extractall(path.join(params.installation_path))
    finally:
        if greenplum_tar != None:
            greenplum_tar.close()

    # GPSeginstall && gpinitsystem

def initialize(env):
    pass

def preinstallation_configure(env):
    import params

    # Create user
    User(
        params.admin_user,
        action="create", shell="/bin/bash"
    )

    Directory(
        path.dirname(params.greenplum_initsystem_config_file),
        action="create",
        recursive=True,
        owner=params.admin_user
    )

    # Create installation directory
    Directory(
        params.installation_path,
        action="create",
        owner=params.admin_user, mode=0755
    )

    # Create data directories, mirror directories
    Directory(
        params.data_directories + params.mirror_data_directories,
        action="create",
        recursive=True,
        owner=params.admin_user, mode=0755
    )

    # Create segment file
    TemplateConfig(
        params.greenplum_segments_file,
        owner=params.admin_user, mode=0644
    )

    # Create gpinit_config file
    TemplateConfig(
        params.greenplum_initsystem_config_file,
        owner=params.admin_user, mode=0644
    )

def postinstallation_configure(env):
    pass