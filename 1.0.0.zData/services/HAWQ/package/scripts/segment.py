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
    print 'Stop the Sample Srv Slave';
  def start(self, env):
    print 'Start the Sample Srv Slave';
  def status(self, env):
    print 'Status of the Sample Srv Slave';
  def configure(self, env):
    print 'Configure the Sample Srv Slave';
if __name__ == "__main__":
  Slave().execute()
