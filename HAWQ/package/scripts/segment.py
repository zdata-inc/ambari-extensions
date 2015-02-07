from resource_management import *
from utils import * 
import sys

class Slave(Script):
 
  # This installation assumes that the /etc/hosts file includes the host names and all interface address names for every machine participating in your HAWQ system.
  # In the future, we can check to make sure this is true.
  def install(self, env):
    import params
    
    # Install hawq package
    self.install_packages(env)
    
    # Add user
    hawq_useradd()

    # Modify system level settings for Hawq
    hawq_modify_kernel_parameters()
    hawq_modify_security_parameters()
    hawq_modify_mount_options()

    os.system("mkdir -p " + params.DATA_DIRECTORY)
    os.system("chown -R "+ params.hawq_user +" "+params.DATA_DIRECTORY)
  
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
