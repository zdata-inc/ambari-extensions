import os
import utilities

from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management import *
from library import hawq

def install(env):
    import params

    hawq.create_user()

    # Source hawq functions for root as well
    Execute("source %s" % params.hawq_environment_path)

    # Hostfile Segments
    TemplateConfig(
        params.hawq_hostfile_path,
        owner=params.hawq_user, mode=0644
    )

    # Exchange private keys for root and gpadmin
    Execute("source %s; gpssh-exkeys -f %s;" % (params.hawq_environment_path, params.hawq_hostfile_path))
    Execute("gpssh-exkeys -f %s -p %s;" % (params.hawq_hostfile_path, params.hawq_password), user=params.hawq_user)

    hawq.configure_kernel_parameters()
    hawq.configure_security_limits()
    # hawq.configure_mount_options()

    hawq.create_data_dirs(params.DATA_DIRECTORY.split())

    # Create master directory
    Directory(
        params.MASTER_DIRECTORY,
        action="create",
        mode=0755,
        recursive=True,
        owner=params.hawq_user
    )

    # Create gpinitsystem_config file
    Directory(
        params.gpconfigs_path.rstrip("/"),
        action="create",
        mode=0755,
        owner=params.hawq_user
    )

    TemplateConfig(
        params.gpinitsystem_config_path,
        owner=params.hawq_user, mode=0644
    )

    # Install
    Execute(
        format("gpinitsystem -c {params.gpinitsystem_config_path} -h {params.hawq_hostfile_path} -a"),
        user=params.hawq_user
    )

def configure():
    pass

def start():
    pass

def stop():
    pass

def is_running():
    pass
