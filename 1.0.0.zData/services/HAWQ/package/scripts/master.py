from resource_management import *
from utils import * 
import sys
import os
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

  def stop(self, env):
    print 'Stop the Hawq Master';
  def start(self, env):
    print 'Start the Hawq Master';
  def status(self, env):
    print 'Status of the Hawq Master';
  def configure(self, env):
    print 'Configure the Hawq Master';

if __name__ == "__main__":
  Master().execute()
