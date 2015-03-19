from os import path
import urllib
from resource_management import *
from pprint import pprint
import sys
import utilities
import greenplum_installer

def install(env):
    import params

    distributedArchive = greenplum_installer.GreenplumDistributed(params.installer_location, params.tmp_dir)
    greenplumInstaller = distributedArchive.get_installer()

    absolute_installation_path = path.join(params.installation_path, 'greenplum-db')
    version_installation_path = path.join(params.installation_path, 'greenplum-db-%s' % greenplum_installer.get_version())
    greenplum_installer.install_to(version_installation_path)

    Execute('ln -s "%s" "%s"' % (version_installation_path, absolute_installation_path))

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