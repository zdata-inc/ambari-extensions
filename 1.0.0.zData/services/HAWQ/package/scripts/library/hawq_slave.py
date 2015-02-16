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
    import params
    from glob import glob

    for segmentPath in glob(params.hawq_slave_glob):
        Execute('pg_ctl -D "%s" start' % segmentPath, user=params.hawq_user)

def stop():
    import params
    from glob import glob

    for segmentPath in glob(params.hawq_slave_glob):
        Execute('pg_ctl -D "%s" stop' % segmentPath, user=params.hawq_user)

def is_running():
    import params
    from glob import glob

    for segmentPath in glob(params.hawq_slave_glob):
        if not hawq.is_running(os.path.join(segmentPath, 'postmaster.pid')):
            return False

    return True