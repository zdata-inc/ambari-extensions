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
        params.hawq_hostfile_seg_path,
        owner=params.hawq_user, mode=0644
    )

    # Exchange private keys for root and gpadmin
    Execute("source %s; gpssh-exkeys -f %s;" % (params.hawq_environment_path, params.hawq_hostfile_seg_path))
    Execute("gpssh-exkeys -f %s -p %s;" % (params.hawq_hostfile_seg_path, params.hawq_password), user=params.hawq_user)

    hawq.configure_kernel_parameters()
    hawq.configure_security_limits()
    # hawq.configure_mount_options()

    # Create master directory
    Directory(
        params.MASTER_DIRECTORY,
        action="create",
        mode=0755,
        recursive=True,
        owner=params.hawq_user
    )

    # Export master data directory environment variable
    utilities.appendBashProfile(
        params.hawq_user,
        "export MASTER_DATA_DIRECTORY=%s/gpseg-1" % params.MASTER_DIRECTORY,
        run=True
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
        format("gpinitsystem -c {params.gpinitsystem_config_path} -h {params.hawq_hostfile_seg_path} -a"),
        user=params.hawq_user
    )

    # Validates various platform-specific, HAWQ, and HDFS specific configuration settings. Stores results in home dir hawq user.
    Execute(
        format("gpcheck -f %s --zipout" % params.hawq_hostfile_all_path),
        cwd="~",
        user=params.hawq_user
    )

def configure():
    pass

def start():
    Execute(
        format("gpstart -a -v"),
        user=params.hawq_user
    )

def stop():
    Execute(
        format("gpstop -a -M smart -v"),
        user=params.hawq_user
    )

def force_stop():
    Execute(
        format("gpstop -a -M fast -v"),
        user=params.hawq_user
    )

def is_running():
    pass
