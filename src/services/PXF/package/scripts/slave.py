import sys
from resource_management import *
from library import * 

class Slave(Script):
  def install(self, env):

    import params
    env.set_params(params)
    self.install_packages(env)
  
    TemplateConfig(
      params.pxf_env_script,
    )
   
    TemplateConfig(
      params.pxf_public_classpath,
    )

    Execute("service pxf-service init")

  def stop(self, env):
    Execute("service pxf-service stop")

  def start(self, env):
    Execute("service pxf-service start")

  def status(self, env):
    import params
  
    if check_process_status(params.pxf_pid_file):
      raise ComponentIsNotRunning()

  def configure(self, env):
    pass

if __name__ == "__main__":
  Slave().execute()
