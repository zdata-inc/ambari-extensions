from resource_management import *

def initialize():
    Execute("service pxf-service init")

def start():
    Execute("service pxf-service start")

def stop():
    Execute("service pxf-service stop")

def is_running():
    import params

    try:
        check_process_status(params.pxf_pid_file)
        return True
    except ComponentIsNotRunning:
        return False