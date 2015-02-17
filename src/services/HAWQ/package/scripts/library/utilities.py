from resource_management import *
from resource_management.core.exceptions import Fail
import os
import json
import logging

def _lines_contain(haystack, needle):
    for line in haystack:
        if line.strip() == needle.strip():
            return True

    return False

def _lines_startsWith(haystack, prefix):
    """
    Checks if one of a group of lines starts with a given prefix.
    """
    for line in haystack:
        if line.strip().startswith(prefix):
            return True

    return False

def appendBashProfile(user, toBeAppended, run=False, allowDuplicates=False):
    bashrc = "/home/%s/.bashrc" % user
    command = json.dumps(toBeAppended)[1:-1]

    with open(bashrc, 'a+') as filehandle:
        if not _lines_contain(filehandle.readlines(), command):
            print "Appending " + command
            filehandle.write(format("{toBeAppended}\n"))

    if run:
        Execute(toBeAppended)

def setKernelParameters(parameters):
    for key, value in parameters.iteritems():
        setKernelParameter(key, value)
    pass

def setKernelParameter(name, value, logoutput=True):
    logLine = "%s = %s" % (name, value)

    try:
        Execute('sysctl -w %s=%s' % (name, value), logoutput=False)
        logLine += " Added"

        with open('/etc/sysctl.conf', 'a+') as filehandle:
            line = format("{name} = {value}\n")
            if not _lines_contain(filehandle.readlines(), line):
                logLine += " Saved"
                filehandle.write(line)
            else:
                logLine += " Already Saved"

    except Fail as exception:
        logLine += " Bad"
        pass
    finally:
        if logoutput:
            print logLine

def is_process_running(pid_file, pid=None):
    """
    Function checks whether process is running.
    Process is considered running, if pid file exists, and process with
    a pid, mentioned in pid file is running
    @param pid_file: path to service pid file
    @param pid: The pid in the pid file, useful if pidfile is of nonstandard format
    @return: Whether or not the process is running
    """

    if not pid_file or not os.path.isfile(pid_file):
        return False

    if pid == None:
        try:
            with open(pid_file, 'r') as filehandle:
                try:
                    pid = int(filehandle.read())
                except:
                    return False
        except IOError:
            return False

    try:
        # Kill will not actually kill the process
        # From the doc:
        # If sig is 0, then no signal is sent, but error checking is still
        # performed; this can be used to check for the existence of a
        # process ID or process group ID.
        os.kill(pid, 0)
    except OSError:
        return False

    return True