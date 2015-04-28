from os import path
from library import hawq
from resource_management import *

def install(env):
    import params

    hawq.create_user()
    hawq.configure_kernel_parameters()
    hawq.configure_security_limits()

    Directory(
        params.data_directories,
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

    # Given an array of globs, loop through each pid file which matches any of the globs and
    # verify the pid it references is running.
    for pid_path in [pid_path for pid_glob in params.slave_pid_globs for pid_path in glob(path.dirname(pid_glob))]:
        if not hawq.is_running(path.join(pid_path, path.basename(pid_glob))):
            return False

    return True
