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


class Master(Script):
    """Manages a Chorus server"""

    def install(self, env):
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
            bufsize = 1,
            shell = True
        )

        installationProcess.stdin.write("\n".join(installationOptions) + "\n")

        installationProcess.wait()

        if (len(installationProcess.stderr.read()) > 0):
            cprint('FAIL', "There were errors during the installation:")
            print installationProcess.stderr.read()
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

if __name__ == "__main__":
    Master().execute()