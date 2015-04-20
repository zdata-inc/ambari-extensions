import sys
import os
import greenplum
import utilities
from resource_management import *

class Client(Script):
    def install(self, env):
        import params

        utilities.append_bash_profile(params.admin_user, "source %s;" % os.path.join(params.absolute_installation_path, 'greenplum_path.sh'))
        utilities.append_bash_profile(params.admin_user, 'export PGPORT="%s";' % params.master_port)
        utilities.append_bash_profile(params.admin_user, 'export PGDATABASE="%s";' % params.database_name)

    def configure(self, env):
        greenplum.create_host_files()

    def status(self, env):
        pass

if __name__ == "__main__":
    Client().execute()