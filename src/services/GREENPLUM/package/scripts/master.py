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

        self.install_packages(env)

        greenplum.preinstallation_configure(env)
        greenplum.create_master_data_directory()
        greenplum.create_gpinitsystem_config(params.admin_user, params.greenplum_initsystem_config_file)
        greenplum.add_psql_variables()

        greenplum.master_install(env)

        # Ambari requires service to be in a stopped state after installation
        try:
            self.status(env)
            self.stop(env)
        except ComponentIsNotRunning:
            pass

    def start(self, env):
        import params
        env.set_params(params)

        self.configure(env)

        Execute(
            params.source_cmd + "gpstart -a -v",
            user=params.admin_user
        )

    def stop(self, env):
        import params

        Execute(
            params.source_cmd + "gpstop -a -M smart -v",
            user=params.admin_user
        )

    def forcestop(self, env):
        import params

        Execute(
            params.source_cmd + "gpstop -a -M fast -v",
            user=params.admin_user
        )

    def recover_master():
        print "Noop: Recovering master"

    def configure(self, env):
        import params

        greenplum.create_host_files()
        greenplum.preinstallation_configure(env)
        greenplum.refresh_pg_hba_file()

         
    def status(self, env):
        import params
        if not greenplum.is_running(params.master_pid_path):
            raise ComponentIsNotRunning()

if __name__ == "__main__":
    Master().execute()
