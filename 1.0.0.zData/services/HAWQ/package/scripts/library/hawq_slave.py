import os
from library import utilities
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management import *
from library import hawq

def install(env):
    import params

    create_user()
    configure_kernel_parameters()
    configure_security_limits()
    # configure_mount_options()

    create_data_dirs(params.MASTER_DIRECTORY.split())

def configure():
    pass

def start():
    pass

def stop():
    pass

def is_running():
    pass