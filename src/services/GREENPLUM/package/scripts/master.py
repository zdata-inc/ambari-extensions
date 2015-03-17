import sys
import os
from resource_management import *

class Master(Script):

    def install(self, env):
        import params

        self.install_packages(env)
        env.set_params(params)

        self.configure(env)
        print 'Install the Greenplum Master'
 
    def stop(self, env):
        print 'Stop the Greenplum Master'

    def start(self, env):
        print 'Start the Greenplum Master'

    def configure(self, env):
        
         
    def status(self, env):
        print 'Status of the Greenplum Master'

if __name__ == "__main__":
    Master().execute()