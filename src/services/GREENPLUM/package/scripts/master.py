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
        self.install_packages(env)
        greenplum.install(env)
        greenplum.initialize(env)

        print 'Install the Greenplum Master'
        sys.exit(1)
 
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