import sys
from resource_management import *
from library import * 

class Slave(Script):
  def install(self, env):
    
    self.install_packages(env)
    Execute("service pxf-service init")

  def stop(self, env):
    Execute("service pxf-service stop")

  def start(self, env):
    Execute("service pxf-service start")

  def status(self, env):
    import params

    if not pxf.is_running(params.pxf_pid_file):
      raise ComponentIsNotRunning()

  def configure(self, env):
    pass

if __name__ == "__main__":
  Slave().execute()
