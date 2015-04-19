from resource_management import *
import os
import string
import random

def append_bash_profile(user, to_be_appended, run=False, allow_duplicates=False):
    """Append a given line to a user's bashrc file.

    user -- The user whose bashrc file will have the given line appended to it.
    to_be_appended -- Line to append to the bashrc file.
    run -- Should the line also be executed?
    allow_duplicates -- If the line already exists in the file, should it be appended anyways?  Whitespace is ignored.
    """

    bashrc = "/home/%s/.bashrc" % user

    with open(bashrc, 'a+') as filehandle:
        if to_be_appended.strip() not in map(lambda line: line.strip(), filehandle.readlines()) or allow_duplicates:
            Logger.info(format("Appending {to_be_appended} to {bashrc}"))
            filehandle.write(format("{to_be_appended}\n"))

    if run:
        Execute(to_be_appended, user=user)

def set_kernel_parameters(parameters, logoutput=True):
    """Given a dictionary of parameters, set each one."""

    for key, value in parameters.iteritems():
        set_kernel_parameter(key, value, logoutput=logoutput)

def set_kernel_parameter(name, value, logoutput=True):
    """Set a kernel paramater vis sysctl, also append to sysctl.conf.

    name -- Name of parameter to set.
    value -- Value of parameter.
    logoutput -- Logoutput of command?
    """

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
    """Generate a SHA512 hash correctly formatted for the shadow file."""

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