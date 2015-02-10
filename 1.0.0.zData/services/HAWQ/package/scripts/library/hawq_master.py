import os
import utilities

from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management import *

def install(self, env):
    self.install_packages(env)

    # Add Hawq User
    User(env.hawq_user, action="create", groups="hadoop", password=env.hawq_password, shell="/bin/bash")
    utilities.appendBashProfile(env.hawq_user, "source %s;" % env.hawq_environment_path, run=True)

    # Hostfile Segments
    TemplateConfig(
        env.hawq_hostfile_path,
        owner=env.hawq_user, mode=0644
    )

    Execute("gpssh-exkeys -f %s;" % hawq_hostfile_path, environment={})

def configure(self):

def start(self):

def stop(self):

def is_running(self):