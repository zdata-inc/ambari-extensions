import sys
import os
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from library.chorus import Chorus
from library import utilities
from pprint import pprint

class Master(Script):
    """Manages a Chorus server"""

    chorusInstance = None

    def _chorus(self):
        if (self.chorusInstance == None):
            import params
            self.chorusInstance = Chorus(params)

        return self.chorusInstance

    def install(self, env):
        if (not os.path.exists(installerPath)):
            raise AttributeException('Installer could not be found at ' + installerPath)

        self.install_packages(env)
        env.set_params(params)

        # Install
        try:
            print self._chorus().install()
        except AttributeException as e:
            print "Configuration error: ", e
            sys.exit(1)
        except Exception as e:
            print e
            sys.exit(1)
        else:
            print "Installation finished successfully!"

    def start(self, env):
        self._chorus().start()

    def stop(self, env):
        self._chorus().stop()


    def status(self, env):
        if (not self._chorus().isRunning()):
            raise ComponentIsNotRunning()

    def configure(self, env):
        self._chorus().configure()

if __name__ == "__main__":
    Master().execute()