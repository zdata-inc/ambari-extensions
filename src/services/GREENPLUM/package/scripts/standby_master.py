import sys
import os
import greenplum
import utilities
from resource_management import *

class StandbyMaster(Script):

    def install(self, env):
        import params

        if not params.license_accepted:
            sys.exit("Installation failed, license agreement not accepted.")

        env.set_params(params)

        greenplum.preinstallation_configure(env)
        greenplum.create_master_data_directory()

        self.install_packages(env)

    def start(self, env):
        pass

    def stop(self, env):
        pass

    def configure(self, env):
        greenplum.create_host_files()
        greenplum.preinstallation_configure(env)
         
    def status(self, env):
        pass

if __name__ == "__main__":
    StandbyMaster().execute()