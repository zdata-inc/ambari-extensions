import sys
import os
from library import utilities
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from ambari_commons import OSCheck
import re

def create_user():
    import params

    # Add Hawq User
    User(
        params.hawq_user,
        groups=["hdfs"],
        password=params.hashed_hawq_password,
        action="create",
        shell="/bin/bash"
    )

    # Source hawq functions for hawq admin, save to bash profile
    utilities.appendBashProfile(params.hawq_user, "source %s;" % params.hawq_environment_path)
    utilities.appendBashProfile(params.hawq_user, "export HADOOP_HOME=%s" % params.hadoop_home)

def add_psql_environment_variables(user):
    """Add relevant psql variables to the given user's bash profile."""

    utilities.appendBashProfile(user, "export PGPORT=%s" % params.MASTER_PORT)
    utilities.appendBashProfile(user, "export PGUSER=%s" % params.hawq_user)
    utilities.appendBashProfile(user, "export PGDATABASE=%s" % params.DATABASE_NAME)

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
    return utilities.is_process_running(pidFile, lambda filehandle: int(filehandle.readlines()[0]))

def scan_installation_logs(logFile, minimum_error_level='info'):
    """Given a log file, return if there are any log lines with an error level above minimum_error_level."""

    log_levels = {'debug': 1, 'info': 2, 'warn': 3, 'error': 4, 'fatal': 5}

    if minimum_error_level.lower() not in log_levels:
        raise ValueError('Invalid minimum_error_level value "%s".' % minimum_error_level.lower())

    error_lines = []
    minimum_error_level = log_levels[minimum_error_level.lower()]

    with open(logFile, 'r') as filehandle:
        for line in filehandle.readlines():
            matches = re.findall(r"\[([A-Z]+)\]", line)
            if len(matches) == 0:
                continue

            line_log_level = matchs[0].lower()

            if line_log_level not in log_levels or log_levels[line_log_level] > minimum_error_level:
                error_lines.append(line)

    # Don't care about lines between sets of asterisks, are metadata and therefore don't need to be included.
    error_lines = remove_lines_between_dots_logs(error_lines)

    return error_lines

def remove_lines_between_delimiter(lines, delimiter=r".*:-\*+$"):
    """Given a list of lines, remove all lines in between lines which match the given delimiter pattern, including the asterisks."""

    inside_delimiter = False
    lines_outside_delimiter = []

    for line in lines:
        line_is_delimiter = re.match(delimiter, line) != None

        if line_is_delimiter:
            inside_delimiter = not inside_delimiter

        if not inside_delimiter and not line_is_delimiter:
            lines_outside_delimiter.append(line)

    return lines_outside_delimiter