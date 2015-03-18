import os
import utilities
import time
import re
from glob import glob

from resource_management.core.exceptions import ComponentIsNotRunning, Fail
from resource_management import *
from library import hawq

def create_user():
    import params

    hawq.create_user()

    # Export master data directory environment variable
    utilities.appendBashProfile(
        params.hawq_user,
        "export MASTER_DATA_DIRECTORY=%s/gpseg-1" % params.MASTER_DIRECTORY,
        run=True
    )

    # Set owner of hawq directory to hawq user
    Execute(format("chown -R {params.hawq_user} {params.hawq_install_path}"))

    # Source hawq functions for root as well
    Execute("source %s" % params.hawq_environment_path)


def exchange_keys():
    import params

    # Exchange private keys for root and gpadmin
    Execute('gpssh-exkeys -f"%s" -p"%s";' % (params.hawq_hostfile_seg_path, params.hawq_password), user=params.hawq_user, tries=3, try_sleep=15)

    Execute("source %s; gpssh-exkeys -f %s;" % (params.hawq_environment_path, params.hawq_hostfile_seg_path))

def create_host_files():
    import params

    # Hostfiles
    TemplateConfig(
        params.hawq_hostfile_seg_path,
        owner=params.hawq_user, mode=0644
    )

    TemplateConfig(
        params.hawq_hostfile_all_path,
        owner=params.hawq_user, mode=0644
    )

def initialize():
    import params

    # Create master directory
    hawq.create_data_dirs(params.MASTER_DIRECTORY)

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
    # Fixes issue #5
    Execute("sed -i 's/GP_CHECK_HDFS=.*/GP_CHECK_HDFS=echo/' /usr/local/hawq/bin/lib/gp_bash_functions.sh")

    Execute(
        "hdfs dfs -mkdir hdfs://%s; hdfs dfs -chown %s:%s hdfs://%s;" % (params.DFS_URL, params.hawq_user, params.hawq_user, params.DFS_URL),
        user="hdfs"
    )
        

    try:
        Execute(
            format("gpinitsystem -a -c %s" % params.gpinitsystem_config_path),
            user=params.hawq_user
        )
    except Fail as exception:
        print "gpinitsystem reported failure to install.  Scanning logs manually for consensus."

        logfile = re.search(format(r'.*:-(/home/[^/]+/gpAdminLogs/gpinitsystem_[0-9]+\.log)'), str(exception))
        if logfile == None:
            print "No log file could be found to be scanned.  Failing."
            raise exception

        logfile = logfile.group(1)
        print "Scanning log file: %s" % logfile

        log_file_errors = hawq.scan_installation_logs(logfile)
        if len(log_file_errors) > 0:
            print "Errors detected in logfile:"

            for error in log_file_errors:
                print " - %s" % error

            print "Due to above errors HAWQ installation marked failed."

            raise exception
        else:
            print "No consensus.  Installation considered successful."
            print ">>>>> The log file located at %s should be reviewed so any reported warnings can be fixed!" % logfile

def is_hawq_initialized():
    import params

    try:
        Execute('hadoop fs -ls "/gpseg*"', user=params.hawq_user)
        return True
    except Fail as e:
        return False

def gpcheck():
    """
    Validates various platform-specific, HAWQ, and HDFS specific configuration settings. Stores results in home dir hawq user.
    """
    import params

    # TODO Make multirunnable
    try:
        Execute(
            "gpcheck -f %s --zipout" % params.hawq_hostfile_all_path,
            user=params.hawq_user
        )
    except Fail as e:
        print "Failed to run gpcheck! \n"
        print e


def configure():
    pass

def start():
    import params

    Execute(
        format("gpstart -a -v"),
        user=params.hawq_user
    )

def stop():
    import params

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
    import params

    return hawq.is_running(params.hawq_master_pid_path)

def check_hawq_installed():
    import params

    return os.path.exists(params.MASTER_DIRECTORY)
