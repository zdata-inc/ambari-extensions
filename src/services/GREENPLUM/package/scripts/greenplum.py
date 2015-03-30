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

    version_installation_path = path.join(params.installation_path, 'greenplum-db-%s' % greenplumInstaller.get_version())
    
    Directory(
        version_installation_path,
        action="create",
        owner=params.admin_user, mode=0755
    )

    greenplumInstaller.install_to(version_installation_path)

    Execute(
        'ln -s "%s" "%s"' % (version_installation_path, params.absolute_installation_path),
        creates=params.absolute_installation_path
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

    try:
        gpinitsystemCommand = ['gpinitsystem', '-a', '-c "%s"' % params.greenplum_initsystem_config_file]
        if params.mirroring_enabled and params.enable_mirror_spreading:
            gpinitsystemCommand.append('-S')

        Execute(
            source_path_command + " ".join(gpinitsystemCommand),
            user=params.admin_user
        )
    except Fail as exception:
        print "gpinitsystem reported failure to install.  Scanning logs manually for consensus."

        logfile = re.search(format(r'.*:-(/home/[^/]+/gpAdminLogs/gpinitsystem_[0-9]+\.log)'), str(exception))
        if logfile == None:
            print "No log file could be found to be scanned.  Failing."
            raise exception

        logfile = logfile.group(1)
        print "Scanning log file: %s" % logfile

        log_file_errors = scan_installation_logs(logfile)
        if len(log_file_errors) > 0:
            print "Errors detected in logfile:"

            for error in log_file_errors:
                print " - %s" % error

            print "Due to above errors Greenplum installation marked failed."

            raise exception
        else:
            print "No consensus.  Installation considered successful."
            print ">>>>> The log file located at %s should be reviewed so any reported warnings can be fixed!" % logfile

def is_running(pidFile):
    try:
        with open(pidFile, 'r') as filehandle:
            pid = int(filehandle.readlines()[0])
            return utilities.is_process_running(pidFile, pid)

    except IOError:
        return False


def scan_installation_logs(logFile, minimum_error_level='info'):
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
    error_lines = remove_lines_between_dots_logs(error_lines)

    return error_lines

def remove_lines_between_dots_logs(lines):
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