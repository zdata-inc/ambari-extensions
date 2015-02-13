import os
import utilities

from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management import *

def install(env):
    import params

    # Add Hawq User
    User(params.hawq_user, action="create", groups="hadoop", password=params.hawq_password, shell="/bin/bash")

    # Source hawq functions for hawq admin, save to bash profile
    utilities.appendBashProfile(params.hawq_user, "source %s;" % params.hawq_environment_path, run=True)

    # Export master data directory environment variable
    utilities.appendBashProfile(
        params.hawq_user,
        "export MASTER_DATA_DIRECTORY=%s/gpseg-1" % params.MASTER_DIRECTORY,
        run=True
    )

    # Source hawq functions for root as well
    Execute("source %s" % params.hawq_environment_path)

    # Hostfile Segments
    TemplateConfig(
        params.hawq_hostfile_path,
        owner=params.hawq_user, mode=0644
    )

    # Exchange private keys for root and gpadmin
    Execute("source %s; gpssh-exkeys -f %s;" % (params.hawq_environment_path, params.hawq_hostfile_path))
    Execute("su - %s -c 'gpssh-exkeys -f %s;'" % (params.hawq_user, params.hawq_hostfile_path))

    # Configure kernel paramters
    if System.get_instance().os_family == "redhat":
        utilities.setKernelParameters({
            'kernel.shmmax': '500000000',
            'kernel.shmmni': '4096',
            'kernel.shmall': '4000000000',
            'kernel.sem': '250 512000 100 2048',
            'kernel.sysrq': '1',
            'kernel.core_uses_pid': '1',
            'kernel.msgmnb': '65536',
            'kernel.msgmax': '65536',
            'kernel.msgmni': '2048',
            'net.ipv4.tcp_syncookies': '0',
            'net.ipv4.ip_forward': '0',
            'net.ipv4.conf.default.accept_source_route': '0',
            'net.ipv4.tcp_tw_recycle': '1',
            'net.ipv4.tcp_max_syn_backlog': '200000',
            'net.ipv4.conf.all.arp_filter': '1',
            'net.ipv4.ip_local_port_range': '1025 65535',
            'net.core.netdev_max_backlog': '200000',
            'vm.overcommit_memory': '2',
            'fs.nr_open': '3000000',
            'kernel.threads-max': '798720',
            'kernel.pid_max': '798720',
            'net.core.rmem_max': '2097152',
            'net.core.wmem_max': '2097152'
        })
    else:
        utilities.setKernelParameters({
            'sysctl.kernel.shmmax': '500000000',
            'sysctl.kernel.shmmni': '4096',
            'sysctl.kernel.shmall': '4000000000',
            'sysctl.kernel.sem': '250 512000 100 2048',
            'sysctl.kernel.sysrq': '1',
            'sysctl.kernel.core_uses_pid': '1',
            'sysctl.kernel.msgmnb': '65536',
            'sysctl.kernel.msgmax': '65536',
            'sysctl.kernel.msgmni': '2048',
            'sysctl.net.ipv4.tcp_syncookies': '0',
            'sysctl.net.ipv4.ip_forward': '0',
            'sysctl.net.ipv4.conf.default.accept_source_route': '0',
            'sysctl.net.ipv4.tcp_tw_recycle': '1',
            'sysctl.net.ipv4.tcp_max_syn_backlog': '200000',
            'sysctl.net.ipv4.conf.all.arp_filter': '1',
            'sysctl.net.ipv4.ip_local_port_range': '1025 65535',
            'sysctl.net.core.netdev_max_backlog': '200000',
            'sysctl.vm.overcommit_memory': '2',
            'sysctl.fs.nr_open': '3000000',
            'sysctl.kernel.threads-max': '798720',
            'sysctl.kernel.pid_max': '798720',
            'sysctl.net.core.rmem_max': '2097152',
            'sysctl.net.core.wmen_max': '2097152'
        })

    # Configure security limits
    TemplateConfig(
        params.security_conf_file,
        template_tag="limits",
        owner=params.hawq_user, mode=0644
    )

    # TODO: HAWQ Mount Options

    # Create data directories
    for directory in params.MASTER_DIRECTORY.split():
        Directory(
            directory,
            action="create",
            mode=0755,
            owner=params.hawq_user,
            recursive=True
        )

    # Create gpinitsystem_config file
    Directory(
        params.gpconfigs_path,
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