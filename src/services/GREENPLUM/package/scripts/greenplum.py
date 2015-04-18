from os import path
import urllib
from resource_management import *
from textwrap import dedent
import sys
import utilities
import greenplum_installer
from client import Client

def preinstallation_configure(env):
    import params

    env.set_params(params)

    # Create user
    User(
        params.admin_user,
        password=params.hashed_admin_password,
        action="create", shell="/bin/bash"
    )

    utilities.set_kernel_parameters(utilities.get_configuration_file('system-variables'));

    TemplateConfig(
        params.security_conf_file,
        template_tag="limits",
        owner=params.admin_user, mode=0644
    )

def master_install(env):
    import params

    distributedArchive = greenplum_installer.GreenplumDistributed.fromSource(params.installer_location, params.tmp_dir)
    greenplumInstaller = distributedArchive.get_installer()

    version_installation_path = path.join(params.installation_path, 'greenplum-db-%s' % greenplumInstaller.get_version())
    
    Directory(
        version_installation_path,
        action="create",
        owner=params.admin_user, mode=0755
    )

    greenplumInstaller.install_to(version_installation_path)

    source_path_command = 'source %s;' % path.join(params.absolute_installation_path, 'greenplum_path.sh')
    greenplum_path_file = path.join(version_installation_path, 'greenplum_path.sh')

    preinstallcommands = format(dedent("""
        ln -s '{version_installation_path}' '{params.absolute_installation_path}';
        sed -i 's@^GPHOME=.*@GPHOME={version_installation_path}@' '{greenplum_path_file}';
    """.rstrip()))

    # Run locally to allow gpseginstall to function correctly.
    Execute(preinstallcommands)

    create_host_files()

    Execute(
        format(source_path_command + 'gpseginstall -f "{params.greenplum_all_hosts_file}" -u "{params.admin_user}" -p "{params.admin_password}"')
    )

    # Perform preinstallcommands on rest of machines in cluster.
    Execute(format(dedent("""
        {source_path_command}
        cat <<EOF | gpssh -f '{params.greenplum_all_hosts_file}' -e
            {preinstallcommands}
        EOF
    """.rstrip())))

    Client().install(env)

    try:
        gpinitsystemCommand = ['gpinitsystem', '-a', '-c "%s"' % params.greenplum_initsystem_config_file]

        if params.master_standby_node != None:
            gpinitsystemCommand.append('-s "' + params.master_standby_node + '"')

        if params.mirroring_enabled and params.enable_mirror_spreading:
            gpinitsystemCommand.append('-S')

        Execute(
            source_path_command + " ".join(gpinitsystemCommand),
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

        log_file_errors = _scan_installation_logs(logfile)
        if len(log_file_errors) > 0:
            Logger.error("Errors detected in logfile:")

            for error in log_file_errors:
                Logger.error(" - %s" % error)

            Logger.error("Due to above errors Greenplum installation marked failed.")

            raise exception
        else:
            Logger.info("No consensus.  Installation considered successful.")
            Logger.warning(">>>>> The log file located at %s should be reviewed so any reported warnings can be fixed!" % logfile)

def create_host_files():
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
    import params

    Directory(
        params.master_data_directory,
        action="create",
        recursive=True,
        owner=params.admin_user
    )

    utilities.append_bash_profile(params.admin_user, 'export MASTER_DATA_DIRECTORY="%s";' % params.master_data_segment_directory)

def create_gpinitsystem_config():
    import params

    Directory(
        path.dirname(params.greenplum_initsystem_config_file),
        action="create",
        recursive=True,
        owner=params.admin_user
    )

    TemplateConfig(
        params.greenplum_initsystem_config_file,
        owner=params.admin_user, mode=0644
    )


def is_running(pidFile):
    try:
        with open(pidFile, 'r') as filehandle:
            pid = int(filehandle.readlines()[0])
            return utilities.is_process_running(pidFile, pid)

    except IOError:
        return False


def _scan_installation_logs(logFile, minimum_error_level='info'):
    """
    Given a log file, return if there are any log lines with an error level above minimum_error_level.
    """
    logLevels = {'debug': 1, 'info': 2, 'warn': 3, 'error': 4, 'fatal': 5}

    minimum_error_level = logLevels[minimum_error_level.lower()]
    error_lines = []

    with open(logFile, 'r') as filehandle:
        for line in filehandle.readlines():
            matches = re.findall(r"\[([A-Z]+)\]", line)
            if len(matches) == 0:
                continue

            loglevel = logLevels[matches[0].lower()]
            if loglevel > minimum_error_level:
                error_lines.append(line)

    # Don't care about the lines that say errors were found in logs, remove them
    error_lines = _remove_lines_between_dots_logs(error_lines)

    return error_lines

def _remove_lines_between_dots_logs(lines):
    """
    Given a set of lines from a log file, remove all lines in between lines of asterisks.
    """
    inDots = False
    linesToDelete = []
    for i in range(len(lines)):
        lineIsDots = False
        if re.match(r".*:-\*+$", lines[i]) != None:
            inDots = not inDots
            lineIsDots = True

        if inDots or lineIsDots:
            linesToDelete.append(i)

    linesToDelete.reverse()
    for lineNumber in linesToDelete:
        del lines[lineNumber]

    return lines