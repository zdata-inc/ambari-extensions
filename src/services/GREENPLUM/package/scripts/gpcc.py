from resource_management import *
import os, sys
import greenplum
import utilities

class GPCC(Script):
    def install(self, env):
        print "Installing GPCC"
        pass

    def start(self, env):
        pass

    def stop(self, env):
        pass

    def configure(self, env):
        pass

    def status(self, env):
        pass

if __name__ == "__main__":
    GPCC().execute()
