from resource_management import *
from subprocess import Popen, PIPE
import sys
import os
import select
from pprint import pprint

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

    color = colors[color]

    print color + message + colors['ENDC']

def demoter(user_uid, user_gid):
    def result():
        os.setgid(user_uid)
        os.setuid(user_uid)
    return result

class Master(Script):
    """Manages a Chorus server"""

    def install(self, env):
        self.install_packages(env)

        pprint(self.create_user(env))

        demoterFunction = demoter(*self.create_user(env))

        config = Script.get_config()['configurations']['installation-config']
        # pprint(Script.get_config())
        # pprint(env)

        if (not os.path.exists(os.path.abspath(config['chorus.installation.installerpath']))):
            pprint('FAIL', 'Installer could not be found at ' + os.path.abspath(config['chorus.installation.installerpath']))
            sys.exit(1)

        installerPath = os.path.abspath(config['chorus.installation.installerpath'])

        ### Installation Optinos
        installationOptions = []

        # Terms accepted
        installationOptions.append('y' if config['chorus.termsaccepted'] == 'yes' else 'n')

        # Installation Directory
        if (not os.path.exists(os.path.abspath(config['chorus.installation.directory']))):
            cprint('WARNING', 'Given installation directory does not exist, creating...')
            os.makedirs(os.path.abspath(config['chorus.installation.directory']))

        installationOptions.append(os.path.abspath(config['chorus.installation.directory']))

        # Data directory
        if (not os.path.exists(os.path.abspath(config['chorus.installation.datadirectory']))):
            cprint('WARNING', 'Given data directory does not exist, creating...')
            os.makedirs(os.path.abspath(config['chorus.installation.datadirectory']))

        installationOptions.append(os.path.abspath(config['chorus.installation.datadirectory']))

        # Salt
        installationOptions.append('' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt'])


        installationProcess = Popen(
            "/usr/bin/env bash %s" % installerPath,
            stdin = PIPE, stdout = PIPE, stderr = PIPE,
            preexec_fn=demoterFunction(),
            bufsize = 1,
            shell = True
        )

        stdout,stderr = installationProcess.communicate("\n".join(installationOptions) + "\n")
        installationProcess.wait()

        print stdout

        if (len(stderr) > 0):
            cprint('FAIL', "There were errors during the installation:")
            print stderr
            sys.exit(1)
        elif (stdout.find("An error has occurred. Trying to back out and restore previous state") != -1):
            cprint('FAIL', "The installation encountered an error and attempted to roll back:")

            with open('%s/install.log' % os.path.abspath(config['chorus.installation.directory']), 'r') as f:
                print f.read()

            sys.exit(1)
        else:
            cprint('OKGREEN', "Installation finished!")

        sys.exit(1)

    def start(self, env):
        print "Start"

    def stop(self, env):
        print "stop"


    def status(self, env):
        print "status"


    def configure(self, env):
        print "configure"

    def create_user(self, env):
        os.system('useradd chorus')
        os.system('echo "chorus" | passwd --stdin chorus')

        return int(os.popen('id --user chorus').read().strip()), int(os.popen('id --group chorus').read().strip())

if __name__ == "__main__":
    Master().execute()