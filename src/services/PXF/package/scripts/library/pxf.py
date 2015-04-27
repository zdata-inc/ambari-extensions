# Shared methods for PXF can go here... 

def initialize():
    Execute("service pxf-service init")

def start():
    Execute("service pxf-service start")

def stop():
    Execute("service pxf-service stop")

def is_running():
    import params
    return check_process_status(params.pxf_pid_file)