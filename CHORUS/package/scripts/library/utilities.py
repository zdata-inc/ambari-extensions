"""
Utility methods for Chorus installation and management
"""

import os
from subprocess import Popen, PIPE
from textwrap import dedent

def cprint(color, message):
    """
    Prints a message to console in a given color.
    Available colors: HEADER, OKBLUE, OKGREEN, WARNING
    FAIL, BOLD, UNDERLINE
    """
    colors = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    color = colors[color.upper()]

    print color + message + colors['ENDC']

def create_user(user):
    """
    Creates a user on a POSIX compliant system,
    returns the new user's uid and gid.  If the user
    already exists, just returns their uid and gid.
    """
    os.system(dedent("""
        USER=%s
        id $USER > /dev/null 2>1
        if [ $? -ne 0 ]; then
            useradd $USER
            echo "$USER" | passwd --stdin $USER
        fi
        """ % (user)))

    return {
        'uid': int(os.popen("id --user %s" % user).read().strip()),
        'gid': int(os.popen('id --group %s' % user).read().strip())
    }

def _demoter(user):
    """
    Creates an executable method which changes the
    current process's uid and gid to those given.
    """
    def result():
        """
        Changes the uid and gid to their new values.
        Have to change gid first.
        """
        os.setgid(user['gid'])
        os.setuid(user['uid'])
    return result

def run(cmd, options=None, communicate=None, user=None):
    """
    Run a given command with given options using Popen.
    Optionally give a string to communicate to the process,
    if this is done any errors will be caught and an exception raised.
    Optionally give a user to run the process as, only works if the parent
    process is run as root.
    """

    # pylint: disable=W0142

    if options == None:
        options = {}

    if user != None:
        options['preexec_fn'] = _demoter(user)

    if communicate != None:
        process = Popen(cmd,
                        stdin=PIPE,
                        stdout=PIPE,
                        stderr=PIPE,
                        bufsize=1,
                        shell=True,
                        **options
                       )
        out, err = process.communicate(communicate)
        process.wait()

        if len(err) > 0:
            raise Exception("Error running " + cmd + ": " + err)
        if process.returncode != 0:
            raise Exception(cmd + " gave non-zero exit code " + str(process.returncode) + ": " + out)

        return out
    else:
        return Popen(cmd, **options)

    # pylint: enable=W0142
