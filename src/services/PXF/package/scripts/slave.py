from library import *
from resource_management import *

class Slave(Script):
    def install(self, env):
        import params

        env.set_params(params)
        self.install_packages(env)

        pxf.initialize()

    def stop(self, env):
        pxf.stop()

    def start(self, env):
        if not pxf.is_running():
            self.configure(env)
            pxf.start()

    def status(self, env):
        import params
    
        if not pxf.is_running():
            raise ComponentIsNotRunning()

    def configure(self, env):
        TemplateConfig(params.pxf_env_script)
        TemplateConfig(params.pxf_public_classpath)

if __name__ == "__main__":
    Slave().execute()
