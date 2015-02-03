import os
from subprocess import Popen, PIPE
from textwrap import dedent
from collections import namedtuple

def cprint(color, message):
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

def demoter(userAccount):
    def result():
        os.setgid(userAccount['gid'])
        os.setuid(userAccount['uid'])
    return result

def run(cmd, options={}, communicate=None, user=None):
    if (user != None):
        options['preexec_fn'] = demoter(user)

    if (communicate != None):
        process = Popen(cmd,
            stdin = PIPE, stdout = PIPE, stderr = PIPE,
            bufsize = 1,
            shell = True,
            **options
        )
        out, err = process.communicate(communicate)
        process.wait()

        if (len(err) > 0):
            raise Exception(err)
        if (process.returncode != 0):
            raise Exception("Non-zero exit code " + str(process.returncode))

        return out
    else:
        return Popen(cmd, **options)