import sys
import os
import greenplum
from resource_management import *

class Segment(Script):

    def install(self, env):
        import params

        env.set_params(params)
        print 'Install the Greenplum Segment'
        greenplum.preinstallation_configure(env)
 
    def stop(self, env):
        print 'Stop the Greenplum Segment'

    def start(self, env):
        self.configure(env)
        print 'Start the Greenplum Segment'

    def configure(self, env):
        print 'configure the Greenplum instance'

    def status(self, env):
        print 'Status of the Greenplum Segment'

if __name__ == "__main__":
    Segment().execute()