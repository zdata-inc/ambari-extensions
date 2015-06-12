"""
Contains class used to install and manage a Chorus installation
"""

import os
from library import utilities
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management import *

class Chorus(object):
    """
    Manage a Chorus installation
    """

    _accountName = "chorus"
    _account = None

    def __init__(self, params):
        self.params = params

    def user(self):
        """
        Create a chorus user if it doesn't exist, and
        return the user's uid and gid.
        """

        if self._account == None:
            self._account = utilities.create_user(self._accountName)

        return self._account

    def create_directory(self, directory):
        """
        Create a directory with the chorus user as owner and group.
        """

        user = self.user()
        os.makedirs(directory)
        os.chown(directory, user['uid'], user['gid'])

    def install(self):
        """
        Prepare and install Chorus onto the system via a given self extracting shell script.
        """
        user = self.user()

        if not os.path.exists(self.params.INSTALLATION_DIRECTORY):
            self.create_directory(self.params.INSTALLATION_DIRECTORY)

        if not os.path.exists(self.params.DATA_DIRECTORY):
            self.create_directory(self.params.DATA_DIRECTORY)

        installer_path, is_installer_temporary = self.get_installer_path()
        os.chown(installer_path, user['uid'], user['gid'])

        install_output = utilities.run(
            "/usr/bin/env bash %s" % installer_path,
            communicate=self._build_installation_parameters(),
            user=user
        )

        if install_output.find("An error has occurred. Trying to back out and restore previous state") != -1:
            with open(os.path.join(self.params.INSTALLATION_DIRECTORY, 'install.log'), 'r') as filehandle:
                raise Exception("The installation encountered an error and attempted to roll back: %s" % filehandle.read())

        # Delete installer if it was a temporary file.
        if is_installer_temporary:
            os.remove(installer_path)

        self.configure()

        return install_output

    def _build_installation_parameters(self):
        """
        Create the string passed to the self extracting installation script to install Chorus.
        """

        installation_options = []

        # Terms accepted
        installation_options.append('y' if self.params.TERMS_ACCEPTED else 'n')

        # Installation Directory
        if not os.path.exists(self.params.INSTALLATION_DIRECTORY):
            raise AttributeError("Installation directory '%s' does not exist." % self.params.INSTALLATION_DIRECTORY)

        installation_options.append(self.params.INSTALLATION_DIRECTORY)

        # Data directory
        if not os.path.exists(self.params.DATA_DIRECTORY):
            raise AttributeError("Data directory '%s' does not exist." % self.params.DATA_DIRECTORY)

        installation_options.append(self.params.DATA_DIRECTORY)

        # Salt
        installation_options.append(self.params.SECURITY_SALT)

        return "\n".join(installation_options) + "\n"

    def configure(self):
        """
        Prepare the system for Chorus to be installed.
        """

        TemplateConfig(
            os.path.join(self.params.INSTALLATION_DIRECTORY, 'shared', 'chorus.properties'),
            owner=self.user()['uid'], mode=0600
        )

        ## More configurations here in the future

    def start(self):
        """
        Start Chorus as the chorus user using chorus_control.sh
        """

        print utilities.run(os.path.join("source " + self.params.INSTALLATION_DIRECTORY, "chorus_path.sh") + " && chorus_control.sh start", communicate="", user=self.user())

    def stop(self):
        """
        Stop Chorus as the chorus user using chorus_control.sh
        """

        print utilities.run(os.path.join("source " + self.params.INSTALLATION_DIRECTORY, "chorus_path.sh") + " && chorus_control.sh stop", communicate="", user=self.user())

    def is_running(self):
        """
        Check if Chorus is running by verifying the processes using their various pid files.
        Returns true if all are running, or an array of process which should be running.
        """

        pid_files = {
            'solr': os.path.join(self.params.INSTALLATION_DIRECTORY, "shared/tmp/pids/solr-production.pid"),
            'nginx': os.path.join(self.params.INSTALLATION_DIRECTORY, "shared/tmp/pids/nginx.pid"),
            'jetty': os.path.join(self.params.INSTALLATION_DIRECTORY, "shared/tmp/pids/jetty.pid"),
            'scheduler': os.path.join(self.params.INSTALLATION_DIRECTORY, "shared/tmp/pids/scheduler.production.pid"),
            'worker': os.path.join(self.params.INSTALLATION_DIRECTORY, "shared/tmp/pids/worker.production.pid"),
            'postgres': os.path.join(self.params.DATA_DIRECTORY, "db/postmaster.pid")
        }

        not_running = []

        for process, pidFile in pid_files.iteritems():
            pid = None

            if process == 'postgres':
                with open(pidFile, 'r') as filehandle:
                    pid = int(filehandle.readlines()[0])

            if not utilities.is_process_running(pidFile, pid):
                not_running.append(process)

        if len(not_running) > 0:
            return not_running
        else:
            return True


    def get_installer_path(self):
        """Return the path for the Chorus installer.
        Download to a temporary file if necessary."""

        return utilities.resolve_from_source(self.params.INSTALLER_PATH)