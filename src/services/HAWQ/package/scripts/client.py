import sys
from resource_management import *
from library import hawq_master, hawq


class Client(Script):
  def install(self, env):
    import params
    hawq.add_psql_environment_variables()

    # Create hadoop log directory for hawq user
    # This allows hdfs commands to be run as hawq user without errors
    Directory(
        os.path.join('/var/log/hadoop', params.hawq_user),
        action="create",
        owner=params.hawq_user
    )

  def configure(self, env):
    pass

if __name__ == "__main__":
  Client().execute()
