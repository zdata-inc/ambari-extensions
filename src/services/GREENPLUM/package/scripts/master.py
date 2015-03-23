import sys
import os
import greenplum
from resource_management import *

class Master(Script):

    def install(self, env):
        import params

        if not params.license_accepted:
            sys.exit("Installation failed, license agreement not accepted.")

        env.set_params(params)

        Directory(
            os.path.dirname(params.greenplum_initsystem_config_file),
            action="create",
            recursive=True,
            owner=params.admin_user
        )

        Directory(
            params.master_data_directory,
            action="create",
            recursive=True,
            owner=params.admin_user
        )

        # Create gpinit_config file
        TemplateConfig(
            params.greenplum_initsystem_config_file,
            owner=params.admin_user, mode=0644
        )

        greenplum.preinstallation_configure(env)

        self.install_packages(env)
        greenplum.install(env)
 
    def stop(self, env):
        print 'Stop the Greenplum Master'

    def start(self, env):
        self.configure(env)
        print 'Start the Greenplum Master'

    def configure(self, env):
        greenplum.preinstallation_configure(env)
        greenplum.postinstallation_configure(env)
         
    def status(self, env):
        print 'Status of the Greenplum Master'

if __name__ == "__main__":
    Master().execute()