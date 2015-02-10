from resource_management import *
from resource_management.core.exceptions import Fail
import json
import logging

def _lines_contain(haystack, needle):
    for line in haystack:
        if line.strip() == needle.strip():
            return True;

    return False;

def _file_contains(file, needle):
    with open(file, 'r') as filehandle:
        return _lines_contain(filehandle.readlines(), needle)

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