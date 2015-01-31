from resource_management import *
from subprocess import Popen, PIPE
import sys
import os
import select
from library import utilities
from pprint import pprint

class Master(Script):
    """Manages a Chorus server"""

    def install(self, env):
        self.install_packages(env)

        chorusUID, chorusGID = utilities.create_user('chorus')

        config = Script.get_config()['configurations']['installation-config']

        if (not os.path.exists(os.path.abspath(config['chorus.installation.installerpath']))):
            utilities.cprint('FAIL', 'Installer could not be found at ' + os.path.abspath(config['chorus.installation.installerpath']))
            sys.exit(1)

        installerPath = os.path.abspath(config['chorus.installation.installerpath'])

        ### Installation Optinos
        installationOptions = []

        # Terms accepted
        installationOptions.append('y' if config['chorus.termsaccepted'] == 'yes' else 'n')

        # Installation Directory
        if (not os.path.exists(os.path.abspath(config['chorus.installation.directory']))):
            utilities.cprint('warning', 'Given installation directory does not exist, creating...')
            os.makedirs(os.path.abspath(config['chorus.installation.directory']))
            os.chown(os.path.abspath(config['chorus.installation.directory']), chorusUID, chorusGID)

        installationOptions.append(os.path.abspath(config['chorus.installation.directory']))

        # Data directory
        if (not os.path.exists(os.path.abspath(config['chorus.installation.datadirectory']))):
            utilities.cprint('warning', 'Given data directory does not exist, creating...')
            os.makedirs(os.path.abspath(config['chorus.installation.datadirectory']))
            os.chown(os.path.abspath(config['chorus.installation.datadirectory']), chorusUID, chorusGID)

        installationOptions.append(os.path.abspath(config['chorus.installation.datadirectory']))

        # Salt
        installationOptions.append('' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt'])

        ### Installation
        installationProcess = utilities.run("/usr/bin/env bash %s" % installerPath, communicate=True, uid=chorusUID, gid=chorusGID)

        stdout,stderr = installationProcess.communicate("\n".join(installationOptions) + "\n")
        installationProcess.wait()

        print stdout

        if (len(stderr) > 0):
            utilities.cprint('fail', "There were errors during the installation:")
            print stderr
            sys.exit(1)
        elif (stdout.find("An error has occurred. Trying to back out and restore previous state") != -1):
            utilities.cprint('fail', "The installation encountered an error and attempted to roll back:")

            with open('%s/install.log' % os.path.abspath(config['chorus.installation.directory']), 'r') as f:
                print f.read()

            sys.exit(1)
        else:
            utilities.cprint('okgreen', "Installation finished!")

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