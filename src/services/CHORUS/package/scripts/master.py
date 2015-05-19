"""
Ambari service implementation for Chorus master.
"""

import sys
import os
from resource_management import Script
from resource_management.core.exceptions import ComponentIsNotRunning
from library.chorus import Chorus

class Master(Script):
    """Manages a Chorus server"""

    chorusInstance = None

    def _chorus(self):
        """
        Creates Chorus instance for the current installation of Chorus.
        """

        if self.chorusInstance == None:
            import params
            self.chorusInstance = Chorus(params)

        return self.chorusInstance

    def install(self, env):
        """
        Install Chorus with error handling.
        """
        self.configEnv(env)

        self.install_packages(env)
        env.set_params(self._chorus().params)

        # Install
        try:
            print self._chorus().install()
        except AttributeError as exception:
            print "Configuration error: ", exception
            sys.exit(1)
        except StandardError as exception:
            print "There were errors during the installation: %s" % exception
            sys.exit(1)
        else:
            print "Installation finished successfully!"

    def start(self, env):
        """
        Configure and start Chorus.
        """
        self.configEnv(env)

        self._chorus().configure()
        self._chorus().start()

    def stop(self, env):
        """
        Stop Chorus.
        """
        self.configEnv(env)

        self._chorus().stop()


    def status(self, env):
        """
        Verify Chorus is running.
        Throw ComponentIsNotRunning if one or more of its services aren't active.
        """
        self.configEnv(env)

        result = self._chorus().is_running()
        if result != True:
            raise ComponentIsNotRunning(", ".join(result) + " " + ("isn't" if len(result) == 1 else "aren't") + " currently running")

    def configure(self, env):
        """
        Perform configurations on Chorus.
        """
        self.configEnv(env)

        self._chorus().configure()

    def configEnv(self, env):
        import params
        env.set_params(params)

if __name__ == "__main__":
    Master().execute()
