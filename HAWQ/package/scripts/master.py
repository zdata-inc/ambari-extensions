import sys
import os
import subprocess
import re
from resource_management import *
from pwd import getpwnam

class Master(Script):

  def install(self, env):
    print 'Install the Hawq Master'; 
  def stop(self, env):
    print 'Stop the Hawq Master';
  def start(self, env):
    print 'Start the Hawq Master';
  def status(self, env):
    print 'Status of the Hawq Master';
  def configure(self, env):
    print 'Configure the Hawq Master';

if __name__ == "__main__":
  Master().execute()
