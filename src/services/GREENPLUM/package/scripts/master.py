import sys
import os
import greenplum
import utilities
from resource_management import *

class Master(Script):

    def install(self, env):
        import params

        if not params.license_accepted:
            sys.exit("Installation failed, license agreement not accepted.")

        if os.path.exists(params.master_data_segment_directory):
            Logger.info("Found master data directory.  Assuming Greenplum already installed.")
            return

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
        greenplum.master_install(env)

        # Ambari requires service to be in a stopped state after installation
        self.stop(env)

    def start(self, env):
        import params
        env.set_params(params)

        self.configure(env)

        Execute(
            "gpstart -a -v",
            user=params.admin_user
        )

    def stop(self, env):
        import params

        Execute(
            "gpstop -a -M smart -v",
            user=params.admin_user
        )

    def forcestop(self, env):
        import params

        Execute(
            "gpstop -a -M fast -v",
            user=params.admin_user
        )

    def recover_master():
        print "Noop: Recovering master"

    def configure(self, env):
        import params

        greenplum.create_host_files()
        greenplum.preinstallation_configure(env)

         
    def status(self, env):
        import params
        if not greenplum.is_running(params.master_pid_path):
            raise ComponentIsNotRunning()

if __name__ == "__main__":
    Master().execute()
