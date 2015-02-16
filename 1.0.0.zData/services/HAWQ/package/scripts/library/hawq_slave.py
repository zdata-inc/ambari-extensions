import os
from library import utilities
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management import *
from library import hawq

def install(env):
    import params

    hawq.create_user()
    hawq.configure_kernel_parameters()
    hawq.configure_security_limits()
    # hawq.configure_mount_options()

    hawq.create_data_dirs(params.DATA_DIRECTORY.split())

def configure():
    pass

def start():
    pass

def stop():
    pass

def is_running():
    from glob import glob

    for pidFile in glob(hawq_slave_pids_glob):
        if not hawq.is_running(pidFile)
            return False

    return True