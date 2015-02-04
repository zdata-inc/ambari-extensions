from resource_management import *
from utils import * 
import sys
import os

class Master(Script):

  # This installation assumes that the /etc/hosts file includes the host names and all interface address names for every machine participating in your HAWQ system.
  # In the future, we can check to make sure this is true.
  def install(self, env):
    import params

    # Install hawq package
    self.install_packages(env)

    # Add user
    hawq_useradd()

    # Create hawq_hostfile_segments file (Should contain secondary master and all segments for Hawq service)
    f = open(params.hawq_hostfile_segments,'w')
    for host in params.hawq_segment_hosts:
      f.write(host.strip()+'\n')
    f.close()

    # Source hawq environment and perform the ssh key exchange (allows you to log in to all hosts as root user without a password prompt)
    # Note: This may not be needed at all if Ambari install used 'root' account to install all agents
    os.system(params.source_cmd + params.exkeys_cmd)
   
    # Source the path file from the HAWQ installation directory and do the ssh key exchange as the hawq user
    os.system("su - "+ params.hawq_user +" -c \""+ params.source_cmd + params.exkeys_cmd +"\"")

    # Modify system level settings for Hawq
    hawq_modify_kernel_parameters()
    hawq_modify_security_parameters()
    hawq_modify_mount_options()

    # Setup master data storage area
    # FIXME Create the master data directory location on your standby master as well
    os.system("mkdir -p " + params.MASTER_DIRECTORY)
    os.system("chown -R "+ params.hawq_user +" "+ params.MASTER_DIRECTORY)
    
    # Create gpinitsystem_config file
    hawq_create_gpinitsystem_config()
    os.system("echo "+ params.export_mdd_cmd +" >> /home/"+params.hawq_user+"/.bashrc")
    os.system(params.export_mdd_cmd)
    os.system("su - "+ params.hawq_user +" -c \""+ params.export_mdd_cmd +"\"")
    os.system("su - "+ params.hawq_user +" -c \""+ params.source_cmd + params.gpinitsystem_cmd +"\"")
    
    sys.exit(1)

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
