from resource_management import *
from library import hawq_slave
import sys

class Slave(Script):

    # This installation assumes that the /etc/hosts file includes the host names and all interface address names for every machine participating in your HAWQ system.
    # In the future, we can check to make sure this is true.
    def install(self, env):
        import params

        # Install hawq package
        self.install_packages(env)

        env.set_params(params)

        hawq_slave.install(env)

    def stop(self, env):
        hawq_slave.stop()

    def start(self, env):
        hawq_slave.start()

    def status(self, env):
        if not hawq_slave.is_running():
            raise ComponentIsNotRunning()

    def configure(self, env):
        pass

if __name__ == "__main__":
  Slave().execute()
