import sys
from resource_management import *
class Client(Script):
  def install(self, env):
    print 'Install the Greenplum Client';
  def configure(self, env):
    print 'Configure the Greenplum Client';
if __name__ == "__main__":
  Client().execute()
