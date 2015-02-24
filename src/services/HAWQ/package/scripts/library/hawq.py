import os
from library import utilities
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from ambari_commons import OSCheck

def create_user():
    import params

    # Add Hawq User
    User(params.hawq_user, action="create", groups="hdfs", shell="/bin/bash")
    Execute('echo %s | passwd --stdin %s' % (params.hawq_password, params.hawq_user))

    # Source hawq functions for hawq admin, save to bash profile
    utilities.appendBashProfile(params.hawq_user, "source %s;" % params.hawq_environment_path, run=True)

    utilities.appendBashProfile(params.hawq_user, "export PGPORT=%s" % params.MASTER_PORT)
    utilities.appendBashProfile(params.hawq_user, "export PGUSER=%s" % params.hawq_user)
    utilities.appendBashProfile(params.hawq_user, "export PGDATABASE=%s" % params.DATABASE_NAME)
    utilities.appendBashProfile(params.hawq_user, "export HADOOP_HOME=%s" % params.hadoop_home)

def create_data_dirs(data_directories):
    import params

    Directory(
        data_directories,
        action="create",
        mode=0755,
        owner=params.hawq_user,
        recursive=True
    )

def configure_kernel_parameters():
    if System.get_instance().os_family == "redhat" and int(OSCheck.get_os_major_version()) >= 6:
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
            #'vm.overcommit_memory': '2',
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
            #'sysctl.vm.overcommit_memory': '2',
            'sysctl.fs.nr_open': '3000000',
            'sysctl.kernel.threads-max': '798720',
            'sysctl.kernel.pid_max': '798720',
            'sysctl.net.core.rmem_max': '2097152',
            'sysctl.net.core.wmen_max': '2097152'
        })

def configure_security_limits():
    import params

    TemplateConfig(
        params.security_conf_file,
        template_tag="limits",
        owner=params.hawq_user, mode=0644
    )

def configure_mount_options():
    # TODO Not implemented
    raise StandardError('Not implemented.')
    pass

def is_running(pidFile):
    try:
        with open(pidFile, 'r') as filehandle:
            pid = int(filehandle.readlines()[0])
            return utilities.is_process_running(pidFile, pid)

    except IOError:
        return False
