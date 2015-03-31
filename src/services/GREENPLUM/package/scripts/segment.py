import sys
from os import path
import greenplum, utilities
from resource_management import *

class Segment(Script):

    def install(self, env):
        import params

        env.set_params(params)
        self.install_packages(env)

        greenplum.preinstallation_configure(env)

        # Create data directories, mirror directories
        utilities.recursively_create_directory(
            params.data_directories + params.mirror_data_directories,
            owner=params.admin_user, mode=0755
        )
 
    def stop(self, env):
        print 'Stop the Greenplum Segment'

    def start(self, env):
        self.configure(env)
        print 'Start the Greenplum Segment'

    def configure(self, env):
        print 'configure the Greenplum instance'

    def status(self, env):
        import params
        from glob import glob

        # Given an array of globs, loop through each pid file which matches any of the globs and
        # verify the pid it references is running.
        for pid_path in [pid_path for pid_glob in params.segment_pid_globs for pid_path in glob(path.dirname(pid_glob))]:
            if not greenplum.is_running(path.join(pid_path, path.basename(pid_glob))):
                raise ComponentIsNotRunning()

if __name__ == "__main__":
    Segment().execute()