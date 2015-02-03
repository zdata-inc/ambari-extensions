import os
import utilities

class Chorus:
    _accountName = "chorus"
    _account = None

    def __init__(self, params):
        self.params = params

    def user(self):
        if (self._account == None):
            self._account = utilities.create_user(self._accountName)

        return self._account

    def createDirectory(self, directory):
        user = self.user()
        os.makedirs(directory)
        os.chown(directory, user['uid'], user['gid'])

    def install(self):
        self.configure()

        try:
            installOutput = utilities.run("/usr/bin/env bash %s" % self.params.installerPath, communicate=self.buildInstallationParameters(), user=self.user())
        except Exception as e:
            raise Exception("There were errors during the installation: %s" % e)

        if (installOutput.find("An error has occurred. Trying to back out and restore previous state") != -1):
            with open('%s/install.log' % os.path.abspath(config['chorus.installation.directory']), 'r') as f:
                raise Exception("The installation encountered an error and attempted to roll back: %s" % f.read())

        return installOutput

    def buildInstallationParameters(self):
        installationOptions = []

        # Terms accepted
        installationOptions.append('y' if self.params.termsAccepted else 'n')

        # Installation Directory
        if (not os.path.exists(self.params.installationDirectory)):
            raise AttributeError("Installation directory '%s' does not exist." % self.params.installationDirectory)

        installationOptions.append(self.params.installationDirectory)

        # Data directory
        if (not os.path.exists(self.params.dataDirectory)):
            raise AttributeError("Data directory '%s' does not exist." % self.params.dataDirectory)

        installationOptions.append(self.params.dataDirectory)

        # Salt
        installationOptions.append(self.params.securitySalt)

        return "\n".join(installationOptions) + "\n"

    def configure(self):
        if (not os.path.exists(self.params.installationDirectory)):
            self.createDirectory(self.params.installationDirectory)

        if (not os.path.exists(self.params.dataDirectory)):
            self.createDirectory(self.params.dataDirectory)

        ## More configurations here in the future

    def start(self):
        print utilities.run(os.path.join("source " + self.params.installationDirectory, "chorus_path.sh") + " && chorus_control.sh start", communicate="", user=self.user())

    def stop(self):
        print utilities.run(os.path.join("source " + self.params.installationDirectory, "chorus_path.sh") + " && chorus_control.sh stop", communicate="", user=self.user())

    def isRunning(self):
        pidFiles = {
            'solr': os.path.join(self.params.installationDirectory, "tmp/pids/solr-production.pid"),
            'nginx': os.path.join(self.params.installationDirectory, "tmp/pids/nginx.pid"),
            'jetty': os.path.join(self.params.installationDirectory, "tmp/pids/jetty.pid"),
            'schedulrer': os.path.join(self.params.installationDirectory, "tmp/pids/scheduler.production.pid"),
            'worker': os.path.join(self.params.installationDirectory, "tmp/pids/worker.production.pid"),
            'mizuno': os.path.join(self.params.installationDirectory, "tmp/pids/mizuno.pid"),
            'postgres': os.path.join(self.params.installationDirectory, "postgres-db/postmaster.pid")
        }

        notRunning = []

        for process, pid in pidFiles.iteritems():
            try:
                check_process_status(pid)
            except ComponentIsNotRunning as e:
                notRunning.push(process)

        if (len(notRunning) > 0):
            raise ComponentIsNotRunning("\n".join(notRunning) + " aren't currently running")