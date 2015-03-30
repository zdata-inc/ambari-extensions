import os
import re
import json
import string
import random
from collections import deque
from resource_management import *
from resource_management.core.logger import Logger

def _lines_contain(haystack, needle):
    for line in haystack:
        if line.strip() == needle.strip():
            return True

    return False

def append_bash_profile(user, to_be_appended, run=False, allow_duplicates=False):
    bashrc = "/home/%s/.bashrc" % user
    command = json.dumps(to_be_appended)[1:-1]

    with open(bashrc, 'a+') as filehandle:
        if not _lines_contain(filehandle.readlines(), command) or allow_duplicates:
            print "Appending " + command
            filehandle.write(format("{to_be_appended}\n"))

    if run:
        Execute(to_be_appended)

def get_configuration_file(variable_file):
    variables = {}
    for line in StaticFile(variable_file).get_content().split('\n'):
        if len(line) == 0 or line.startswith('#'):
            continue

        key, value = map(lambda item: item.strip(), line.split('='))
        variables[key] = value

    return variables

def set_kernel_parameters(parameters, logoutput=True):
    for key, value in parameters.iteritems():
        set_kernel_parameter(key, value, logoutput=logoutput)

def set_kernel_parameter(name, value, logoutput=True):
    log_line = [format("{name} = {value}")]

    try:
        Execute('sysctl -w %s=%s' % (name, value), logoutput=False)
        log_line.append("added")

        with open('/etc/sysctl.conf', 'a+') as filehandle:
            line = format("{name} = {value}\n")
            if not _lines_contain(filehandle.readlines(), line):
                log_line.append("saved")
                filehandle.write(line)
            else:
                log_line.append("already saved")

    except Fail as exception:
        log_line.append("bad")
    finally:
        if logoutput:
            Logger.info(" ".join(log_line))

def search_replace(search, replace, subject):
    with open(subject, 'r+') as filehandle:
        file_contents = filehandle.read()
        file_contents = re.sub(search, replace, file_contents)
        filehandle.seek(0)
        filehandle.write(file_contents)
        filehandle.truncate()

def create_salt():
    output = ""
    for i in range(16):
        output += random.choice(string.letters + string.digits)
    return output

def crypt_password(plaintext):
    import crypt
    salt = '$6$' + create_salt() + '$'
    return crypt.crypt(plaintext, salt)

def recursively_create_directory(directory, owner='root', mode=0755):
    if not isinstance(directory, basestring):
        for dir in directory:
            recursively_create_directory(dir, owner=owner, mode=mode)
        return

    directory_path_parts = deque(directory.strip().lstrip('/').split('/'))
    directory_iterator = '/' if directory.startswith('/') else './'

    while len(directory_path_parts) > 0:
        directory_iterator = os.path.join(directory_iterator, directory_path_parts.popleft())

        Directory(
            directory_iterator,
            action="create",
            owner=owner, mode=mode
        )

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

def call(*argv, **kwargs):
    def call_fn(fn):
        return fn(*argv, **kwargs)
    return call_fn