from os import path
import urllib
from resource_management import *
import sys
import utilities
import greenplum_installer

def preinstallation_configure(env):
    import params

    # Create user
    User(
        params.admin_user,
        password=params.hashed_admin_password,
        action="create", shell="/bin/bash"
    )

    # Create data directories, mirror directories
    utilities.recursively_create_directory(
        params.data_directories + params.mirror_data_directories,
        owner=params.admin_user, mode=0755
    )

    utilities.set_kernel_parameters(utilities.get_configuration_file('system-variables'));

    TemplateConfig(
        params.security_conf_file,
        template_tag="limits",
        owner=params.admin_user, mode=0644
    )

def install(env):
    import params

    distributedArchive = greenplum_installer.GreenplumDistributed.fromSource(params.installer_location, params.tmp_dir)
    greenplumInstaller = distributedArchive.get_installer()

    absolute_installation_path = path.join(params.installation_path, 'greenplum-db')
    version_installation_path = path.join(params.installation_path, 'greenplum-db-%s' % greenplumInstaller.get_version())
    
    Directory(
        version_installation_path,
        action="create",
        owner=params.admin_user, mode=0755
    )

    greenplumInstaller.install_to(version_installation_path)

    Execute(
        'ln -s "%s" "%s"' % (version_installation_path, absolute_installation_path),
        creates=absolute_installation_path
    )

    # Create segment file
    TemplateConfig(
        params.greenplum_segments_file,
        owner=params.admin_user, mode=0644
    )

    utilities.search_replace(r'GPHOME=.*\n', 'GPHOME=%s\n' % version_installation_path, path.join(version_installation_path, 'greenplum_path.sh'))

    source_path_command = 'source %s;' % path.join(version_installation_path, 'greenplum_path.sh')

    Execute(
        format(source_path_command + 'gpseginstall -u {params.admin_user} -p {params.admin_password} -f {params.greenplum_segments_file}')
    )

    Execute(
        format(source_path_command + 'gpinitsystem -a -c {params.greenplum_initsystem_config_file}'),
        user=params.admin_user
    )