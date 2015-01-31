import os
from subprocess import Popen, PIPE
from textwrap import dedent

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

    return int(os.popen("id --user %s" % user).read().strip()), int(os.popen('id --group %s' % user).read().strip())

def demoter(user_uid, user_gid):
    def result():
        os.setgid(user_uid)
        os.setuid(user_uid)
    return result

def run(cmd, options={}, communicate=False, uid=None, gid=None):
    if (uid != None and gid != None):
        options['preexec_fn'] = demoter(uid, gid)

    if (communicate):
        options['stdin']   = PIPE
        options['stdout']  = PIPE
        options['stderr']  = PIPE
        options['bufsize'] = 1
        options['shell']   = True

    return Popen(cmd, **options)