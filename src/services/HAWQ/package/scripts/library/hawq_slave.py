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

    Directory(
        params.DATA_DIRECTORY.split(),
        action="create",
        mode=0755,
        owner=params.hawq_user,
        recursive=True
    )

def configure():
    pass

def start():
    pass

def stop():
    pass

def is_running():
    import params
    from glob import glob

    for segmentPath in glob(params.hawq_slave_glob):
        if not hawq.is_running(os.path.join(segmentPath, 'postmaster.pid')):
            return False

    return True