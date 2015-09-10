import sys
import os
import greenplum
import utilities
from resource_management import *

class Client(Script):
    def install(self, env):
        greenplum.add_psql_variables()

    def configure(self, env):
        greenplum.create_host_files()

    def status(self, env):
        raise ClientComponentHasNoStatus()

if __name__ == "__main__":
    Client().execute()
