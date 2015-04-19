from __future__ import with_statement
import os
import random
import re, json, string

from resource_management import *
from resource_management.core.logger import Logger
from textwrap import dedent

def append_bash_profile(user, to_be_appended, run=False, allow_duplicates=False):
    bashrc = "/home/%s/.bashrc" % user

    with open(bashrc, 'a+') as filehandle:
        if to_be_appended.strip() not in map(lambda line: line.strip(), filehandle.readlines()) or allow_duplicates:
            Logger.info(format("Appending {command} to {bashrc}"))
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
    name = name.strip()
    log_line = [format("{name} = {value} - ")]

    try:
        with open('/etc/sysctl.conf', 'a+') as filehandle:
            if name not in map(lambda line: line.split('=')[0].strip(), filehandle.readlines()):
                # Add via sysctl so value will be updated immediately.
                Execute(format('sysctl -w {name}="{value}"'), logoutput=False)
                log_line.append("added")

                # Add to sysctl conf file so value will be updated on subsequent reboots.
                filehandle.write(format("{name} = {value}\n"))
                log_line.append("saved")
            else:
                log_line.append("already saved")

    except Fail as exception:
        log_line.append("sysctl failed to modify parameter, considered bad.")
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

def gpsshify(command, host=None, hostfile=None, args=None):
    if host == None and hostfile == None:
        raise ValueError('Either host or hostfile must be given')

    arguments = []
    if host != None:
        arguments.append('-h "%s"' % host)
    if hostfile != None:
        arguments.append('-f "%s"' % hostfile)
    if args != None:
        arguments.append(args)

    arguments = " ".join(arguments)

    return format(dedent("""
        cat <<EOF | gpssh {arguments}
            {command}
        EOF
    """.rstrip()))

def random_string(length, character_set=None):
    """Generate a random string.

    length -- Length of string to generate.
    character_set -- Characters as a list to use during generation.  Defaults to letters and digits.
    """
    output = ""

    if character_set == None:
        character_set = string.letters + string.digits

    for i in range(length):
        output += random.choice(character_set)

    return output

def crypt_password(plaintext):
    import crypt
    salt = '$6$' + random_string(16) + '$'
    return crypt.crypt(plaintext, salt)

def is_process_running(pid_file, pid_parser=None):
    """Checks whether a process is running given a pid_file.
    Process is considered running if the given pid file exists, and
    the pid is running.

    pid_file -- Pidfile to check.
    pid_parser -- Lambda to parse pid from pidfile given the pidfile's filehandle, optional.
    """

    if pid_parser == None:
        pid_parser = lambda filehandle: int(filehandle.read().strip())

    if not pid_file or not os.path.isfile(pid_file):
        return False

    try:
        with open(pid_file, 'r') as filehandle:
            pid = pid_parser(filehandle)
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