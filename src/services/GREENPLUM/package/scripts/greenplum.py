from __future__ import with_statement
import sys
import urllib
from os import path
from textwrap import dedent
from resource_management import *
import greenplum_installer
import utilities

def preinstallation_configure(env):
    """Should be run before installation on all hosts."""

    import params

    env.set_params(params)

    # Create user
    Group(
        params.admin_group
    )

    User(
        params.admin_user,
        password=params.hashed_admin_password,
        groups=[params.admin_group],
        action="create", shell="/bin/bash"
    )

    if params.set_kernel_parameters:
        utilities.set_kernel_parameters(utilities.get_configuration_file('system-variables'))

        TemplateConfig(
            params.security_conf_file,
            template_tag="limits",
            owner=params.admin_user, mode=0644
        )

def master_install(env):
    """Perform installation for master node."""

    import params

    with greenplum_installer.GreenplumDistributed.from_source(params.installer_location, params.tmp_dir) as distributed_archive:
        with distributed_archive.get_installer() as gp_install_script:
            version_installation_path = path.join(params.installation_path, 'greenplum-db-%s' % gp_install_script.get_version())

            Directory(
                version_installation_path,
                action="create",
                owner=params.admin_user, mode=0755
            )

            gp_install_script.install_to(version_installation_path)


    relative_greenplum_path_file = path.join(version_installation_path, 'greenplum_path.sh')

    Link(params.absolute_installation_path, to=version_installation_path)
    Execute("sed -i 's@^GPHOME=.*@GPHOME={0}@' '{1}';".format(version_installation_path, relative_greenplum_path_file))

    for host in params.all_nodes:
        Execute("ssh-keyscan {0} >> ~/.ssh/known_hosts".format(host))

    create_host_files()

    Execute(format(params.source_cmd + 'gpseginstall -f "{params.greenplum_all_hosts_file}" -u "{params.admin_user}" -g "{params.admin_group}" -p "{params.admin_password}"'))

    # Link version installation path to absolute one.
    Execute(params.source_cmd + utilities.gpsshify(
        "if [ ! -e '{1}' ]; then ln -s '{0}' '{1}'; fi".format(version_installation_path, params.absolute_installation_path),
        hostfile=params.greenplum_all_hosts_file
    ))

    try:
        gpinitsystem_command = ['gpinitsystem', '-a', '-c "%s"' % params.greenplum_initsystem_config_file]

        if params.master_standby_node != None:
            gpinitsystem_command.append('-s "' + params.master_standby_node + '"')

        if params.mirroring_enabled and params.enable_mirror_spreading:
            gpinitsystem_command.append('-S')

        Execute(
            params.source_cmd + " ".join(gpinitsystem_command),
            user=params.admin_user
        )
    except Fail as exception:
        Logger.info("gpinitsystem reported failure to install.  Scanning logs manually for consensus.")

        logfile = re.search(format(r'.*:-(/home/[^/]+/gpAdminLogs/gpinitsystem_[0-9]+\.log)'), str(exception))
        if logfile == None:
            Logger.error("No log file could be found to be scanned.  Failing.")
            raise exception

        logfile = logfile.group(1)
        Logger.info("Scanning log file: %s" % logfile)

        log_file_errors = scan_installation_logs(logfile)
        if len(log_file_errors) > 0:
            Logger.error("Errors detected in logfile:")

            for error in log_file_errors:
                Logger.error(" - %s" % error)

            Logger.error("Due to above errors Greenplum installation marked failed.")

            raise exception
        else:
            Logger.info("No consensus.  Installation considered successful.")
            Logger.warning(">>>>> The log file located at %s should be reviewed so any reported warnings can be fixed!" % logfile)

def refresh_pg_hba_file():
    import params
    utilities.add_block_to_file(params.pg_hba_file, InlineTemplate(params.pg_hba_appendable_data).get_content(), 'zdata-gp')

def create_host_files():
    """Create segment and all host files in greenplum absolute installation path."""

    import params

    # Create segment hosts file
    TemplateConfig(
        params.greenplum_segment_hosts_file,
        owner=params.admin_user, mode=0644
    )

    # Create all hosts file
    TemplateConfig(
        params.greenplum_all_hosts_file,
        owner=params.admin_user, mode=0644
    )

def create_master_data_directory():
    """Create the master data directory, append relevant environment variable to admin user."""

    import params

    Directory(
        params.master_data_directory,
        action="create",
        recursive=True,
        owner=params.admin_user
    )

    utilities.append_bash_profile(params.admin_user, 'export MASTER_DATA_DIRECTORY="%s";' % params.master_data_segment_directory)

def create_gpinitsystem_config(user, destination):
    """Create gpinitsystem_config file."""

    Directory(
        path.dirname(destination),
        action="create",
        recursive=True,
        owner=user
    )

    TemplateConfig(
        destination,
        owner=user, mode=0644
    )

def add_psql_variables(user=None):
    import params

    if user == None:
        user = params.admin_user

    utilities.append_bash_profile(user, "source %s;" % path.join(params.absolute_installation_path, 'greenplum_path.sh'))
    utilities.append_bash_profile(user, 'export PGPORT="%s";' % params.master_port)
    utilities.append_bash_profile(user, 'export PGDATABASE="%s";' % params.database_name)

def is_running(pid_file):
    return utilities.is_process_running(pid_file, lambda filehandle: int(filehandle.readlines()[0]))

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

            line_log_level = matches[0].lower()

            if line_log_level not in log_levels or log_levels[line_log_level] > minimum_error_level:
                error_lines.append(line)

    # Don't care about lines between sets of asterisks, are metadata and therefore don't need to be included.
    error_lines = remove_lines_between_delimiter(error_lines)

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
