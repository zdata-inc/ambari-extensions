from resource_management import *
import json

def _fileContains(file, needle):
    with open(file, 'r') as filehandle:
        for line in filehandle.readlines():
            if line.strip() == needle.strip():
                return True;

    return False;

def appendBashProfile(user, toBeAppended, run=False, allowDuplicates=False):
    bashrc = "/home/%s/.bashrc" % user
    command = json.dumps(toBeAppended)[1:-1]
    if not _fileContains(bashrc, toBeAppended) or allowDuplicates:
        Execute("echo %s >> \"%s\"" % (json.dumps(toBeAppended), bashrc))

    if run:
        Execute(toBeAppended)

def kernelParameters(parameters):
    for key, value in parameters.iteritems():
        print key + ": " + value
        # Execute('sysctl -w %s=%s' % (key, value))
    pass