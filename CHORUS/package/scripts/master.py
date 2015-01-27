import subprocess
import pprint

class Master(Script):
    """Manages a Chorus installation"""

    def install(self, env):
        pprint.pprint(config)
        installationProcess = subprocess.Popen(
            config['configurations']['installation-config']['Chorus Installer Location']
        )

    def start(self, env):


    def stop(self, env):


    def status(self, env):


    def configure(self, env):
