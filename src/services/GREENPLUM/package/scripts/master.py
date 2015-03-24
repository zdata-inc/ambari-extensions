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

        utilities.appendBashProfile(params.admin_user, "source %s;" % os.path.join(params.absolute_installation_path, 'greenplum_path.sh'))
        utilities.appendBashProfile(params.admin_user, 'export MASTER_DATA_DIRECTORY="%s";' % os.path.join(params.master_data_directory, 'gpseg-1'))

        # Ambari requires service end installation in a stopped state
        stop()

    def start(self, env):
        import params
        env.set_params(params)

        self.configure(env)

        Execute(
            format("gpstart -a -v"),
            user=params.admin_user
        )

    def stop():
        import params

        Execute(
            format("gpstop -a -M smart -v"),
            user=params.admin_user
        )

    def force_stop():
        import params

        Execute(
            format("gpstop -a -M fast -v"),
            user=params.admin_user
        )

    def configure(self, env):
        greenplum.preinstallation_configure(env)
         
    def status(self, env):
        print 'Status of the Greenplum Master'

if __name__ == "__main__":
    Master().execute()