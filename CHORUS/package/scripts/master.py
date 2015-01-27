from resource_management import *
import subprocess
import sys
from pprint import pprint

class Master(Script):
    """Manages a Chorus server"""

    def install(self, env):
        config = Script.get_config()
        pprint(config)
        pprint(env)
        installationProcess = subprocess.Popen(
            config['configurations']['installation-config']['Chorus Installer Location']
        )
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