import sys
import os
from resource_management import *
from library import hawq_master

class Master(Script):

  # This installation assumes that the /etc/hosts file includes the host names and all interface address names for every machine participating in your HAWQ system.
  # In the future, we can check to make sure this is true.
  def install(self, env):
    import params

    # Install hawq package
    self.install_packages(env)

    env.set_params(params)

    hawq_master.install(env)

    hawq_master.stop()

  def stop(self, env):
    hawq_master.stop()

  def start(self, env):
    hawq_master.start()

  def status(self, env):
    if not hawq_master.is_running():
      raise ComponentIsNotRunning()

  def configure(self, env):
    print 'Configure the Hawq Master';

if __name__ == "__main__":
  Master().execute()
