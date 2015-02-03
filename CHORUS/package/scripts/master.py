"""
Ambari service implementation for Chorus master.
"""

import sys
import os
from resource_management import Script
from library.chorus import Chorus
from library import utilities
from pprint import pprint

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

        if not os.path.exists(self._chorus().params.installerPath):
            raise AttributeError('Installer could not be found at ' + self._chorus().params.installerPath)

        self.install_packages(env)
        env.set_params(self._chorus().params)

        # Install
        try:
            print self._chorus().install()
        except AttributeError as e:
            print "Configuration error: ", e
            sys.exit(1)
        except Exception as e:
            print e
            sys.exit(1)
        else:
            print "Installation finished successfully!"

    def start(self, env):
        """
        Configure and start Chorus.
        """

        self._chorus().configure()
        self._chorus().start()

    def stop(self, env):
        """
        Stop Chorus.
        """

        self._chorus().stop()


    def status(self, env):
        """
        Verify Chorus is running.
        Throw ComponentIsNotRunning if one or more of its services aren't active.
        """

        self._chorus().is_running()

    def configure(self, env):
        """
        Perform configurations on Chorus.
        """

        self._chorus().configure()

if __name__ == "__main__":
    Master().execute()
