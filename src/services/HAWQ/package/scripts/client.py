import sys
from resource_management import *
class Client(Script):
  def install(self, env):
    print 'Install the Hawq Client';
  def configure(self, env):
    print 'Configure the Hawq Client';
if __name__ == "__main__":
  Client().execute()
