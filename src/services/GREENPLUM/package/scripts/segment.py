import sys
import time
from os import path
import greenplum
from resource_management import *

class Segment(Script):

    def install(self, env):
        import params

        env.set_params(params)
        self.install_packages(env)

        greenplum.preinstallation_configure(env)

        # Create data directories, mirror directories
        Directory(
            params.data_directories + params.mirror_data_directories,
            recursive=True,
            owner=params.admin_user, mode=0755
        )

    def stop(self, env):
        import params

        pids = [
            {'pidfile': pidfile, 'running': True}
            for pidfile in params.segment_pids
        ]

        print 'Waiting for', str(len(pids)), 'segments to stop.',

        while True:
            running_pids = [pid for pid in pids if pid['running']]

            if len(running_pids) == 0:
                break

            for pid in running_pids:
                pid['running'] = greenplum.is_running(pid['pidfile'])

            time.sleep(1)
            sys.stdout.write('.')

        print
        if all([pid['running'] == False for pid in pids]):
            print "All segments on host stopped."
        else:
            raise RuntimeError("Error stopping all segments!")

    def start(self, env):
        import params
        self.configure(env)

        pids = [
            {'pidfile': pidfile, 'running': False}
            for pidfile in params.segment_pids
        ]

        print 'Waiting for', str(len(pids)), 'segments to start.',

        while True:
            stopped_pids = [pid for pid in pids if not pid['running']]

            if len(stopped_pids) == 0:
                break

            for pid in stopped_pids:
                pid['running'] = greenplum.is_running(pid['pidfile'])

            time.sleep(1)
            sys.stdout.write('.')

        print
        if all([pid['running'] == True for pid in pids]):
            print "All segments on host started."
        else:
            raise RuntimeError("Not all segments on host started!")

    def configure(self, env):
        pass

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
