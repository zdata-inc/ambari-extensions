import sys, os
from library import utilities
from resource_management import *
from ambari_commons import OSCheck
import re
from library import utilities

def create_user():
    import params

    # Add Hawq User
    User(
        params.hawq_user,
        groups=[params.dfs_supergroup],
        password=params.hashed_hawq_password,
        action="create",
        shell="/bin/bash"
    )

    # Source hawq functions for hawq admin, save to bash profile
    utilities.append_bash_profile(params.hawq_user, "source %s;" % params.hawq_environment_path)
    utilities.append_bash_profile(params.hawq_user, "export HADOOP_HOME=%s" % params.hadoop_home)

def add_psql_environment_variables(user):
    """Add relevant psql variables to the given user's bash profile."""
    import params

    utilities.append_bash_profile(user, "export PGPORT=%s" % params.MASTER_PORT)
    utilities.append_bash_profile(user, "export PGUSER=%s" % params.hawq_user)
    utilities.append_bash_profile(user, "export PGDATABASE=%s" % params.DATABASE_NAME)

def configure_kernel_parameters():
    """Configure correct kernel parameters."""
    import params

    if not params.set_kernel_parameters:
        return

    if System.get_instance().os_family == "redhat" and int(OSCheck.get_os_major_version()) >= 6:
        utilities.set_kernel_parameters(utilities.get_configuration_file('system-variables-redhat6'))
    else:
        utilities.set_kernel_parameters(utilities.get_configuration_file('system-variables'))

def configure_security_limits():
    """Configure correct limit.d parameters for hawq user."""
    import params

    if not params.set_kernel_parameters:
        return

    TemplateConfig(
        os.path.join(params.security_conf_path, 'hawq.conf'),
        template_tag="limits",
        owner=params.hawq_user, mode=0644
    )

def is_running(pidFile):
    return utilities.is_process_running(pidFile, lambda filehandle: int(filehandle.readlines()[0]))

def scan_installation_logs(logFile, minimum_error_level='info'):
    """Given a log file, return if there are any log lines with an error level
    above minimum_error_level."""

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

            line_log_level = matches[0].lower()

            if line_log_level not in log_levels or log_levels[line_log_level] > minimum_error_level:
                error_lines.append(line)

    # Don't care about lines between sets of asterisks,
    # they are metadata and therefore don't need to be included.
    error_lines = remove_lines_between_delimiter(error_lines)

    return error_lines

def remove_lines_between_delimiter(lines, delimiter=r".*:-\*+$"):
    """Given a list of lines, remove all lines in between lines which match
    the given delimiter pattern, including the asterisks."""

    inside_delimiter = False
    lines_outside_delimiter = []

    for line in lines:
        line_is_delimiter = re.match(delimiter, line) != None

        if line_is_delimiter:
            inside_delimiter = not inside_delimiter

        if not inside_delimiter and not line_is_delimiter:
            lines_outside_delimiter.append(line)

    return lines_outside_delimiter

