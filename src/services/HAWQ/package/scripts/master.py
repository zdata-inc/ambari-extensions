import os
from library import hawq_master, hawq
from resource_management import *

class Master(Script):

    def install(self, env):
        import params

        # Install hawq package
        self.install_packages(env)

        env.set_params(params)

        hawq_master.create_user()
        hawq.add_psql_environment_variables(params.hawq_user)

        hawq_master.create_host_files()
        hawq_master.exchange_keys()

        hawq.configure_kernel_parameters()
        hawq.configure_security_limits()

    def stop(self, env):
        hawq_master.stop()

    def start(self, env):
        import params
        env.set_params(params)

        if not hawq_master.is_hawq_initialized():
            hawq_master.initialize()
            hawq_master.gpcheck()
        else:
            hawq_master.start()

    def status(self, env):
        if not hawq_master.is_running():
            raise ComponentIsNotRunning()

    def configure(self, env):
        pass

if __name__ == "__main__":
    Master().execute()
