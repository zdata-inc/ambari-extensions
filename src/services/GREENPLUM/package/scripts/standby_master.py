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
        utilities.append_bash_profile(params.admin_user, 'export MASTER_DATA_DIRECTORY="%s";' % params.master_data_segment_directory)

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

        self.install_packages(env)

    def start(self, env):
        pass

    def stop(self, env):
        pass

    def configure(self, env):
        greenplum.create_host_files()
        greenplum.preinstallation_configure(env)

        utilities.append_bash_profile(params.admin_user, 'export MASTER_DATA_DIRECTORY="%s";' % params.master_data_segment_directory)
         
    def status(self, env):
        pass

if __name__ == "__main__":
    StandbyMaster().execute()