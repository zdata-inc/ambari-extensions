import sys
from resource_management import *
class Slave(Script):
  def install(self, env):
  
    # FIXME Find a better way to ensure local repo is on each host.
    Execute("cp /vagrant/artifacts/ambari.repo /etc/yum.repos.d/.")
    
    self.install_packages(env)
    Execute("service pxf-service init")

  def stop(self, env):
    Execute("service pxf-service stop")

  def start(self, env):
    Execute("service pxf-service start")

  def status(self, env):
    pass

  def configure(self, env):
    pass

if __name__ == "__main__":
  Slave().execute()
