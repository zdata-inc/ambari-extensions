import sys
import os
import subprocess
import re
from resource_management import *
from pwd import getpwnam

class Master(Script):

  def install(self, env):
    print 'Install the Greenplum Master'
    config = Script.get_config()
    
    accept = config['configurations']['installation-config']['gp.accept.license.agreement']
    password = config['configurations']['installation-config']['gp.admin.password']
    user = config['configurations']['installation-config']['gp.admin.user']
    installPath = config['configurations']['installation-config']['gp.installation.path']
    greenplumZipFilePath = config['configurations']['installation-config']['gp.installer.zip.file.location']
    # Usually something like 'HDP/2.0.6/services/GREENPLUM/package' 
    servicePackageFolder = config['commandParams']['service_package_folder']
    currentDirectory = "/var/lib/ambari-agent/cache/stacks/"+servicePackageFolder

    if accept != "yes":
      sys.exit("Cannot proceed with installation. License agreement not accepted with 'yes'.")
    
    if not os.path.isfile(greenplumZipFilePath):
      sys.exit("Cannot find Greenplum zip file path: "+greenplumZipFilePath)

    #FIXME don't hardcode user name password and cluster name (abc)
    FNULL = open(os.devnull, 'w')
    gpSlaveInfo = subprocess.Popen(["/usr/bin/curl","--user", "admin:admin", "http://127.0.0.1:8080/api/v1/clusters/abc/services/GREENPLUM/components/GREENPLUM_SLAVE?fields=host_components/HostRoles/host_name"], stdout=subprocess.PIPE, stderr=FNULL).communicate()[0]
    
    # possibly use groups instead to simplify code
    regex = re.compile('"host_name" : "[A-Za-z0-9.-]+"');
    hostLineMatch = regex.findall(gpSlaveInfo);
    hosts = []
    for hostLine in hostLineMatch:
        hosts.append(hostLine.split(":")[1].strip().strip('"'))

    print "printing the hosts out. they are: "
    print hosts
    hostfile = "/tmp/hostfile_exkeys"
    f = open(hostfile, 'w')
    if f:
      for host in hosts:
        f.write(host+'\n');
        print(host);
        f.close()
    else:
      FNULL.close()
      sys.exit("cannot open "+hostfile)

    unzipScript=currentDirectory+"/scripts/unzip.sh"
   
    
    self.create_data_directories()
    self.create_gpinitsystem_config("/tmp")
 
    print("------------------------------- Unzipping gp zip file") 
    subprocess.call(['chmod','755',unzipScript]);
    unzipReturn = subprocess.Popen([unzipScript, greenplumZipFilePath, installPath, user, password], stdout=subprocess.PIPE, stderr=FNULL).communicate()[0];
    
    print("this is the resturn of calling the .sh file_--------------------------------------")
    print(unzipReturn)

    #  curl  --user admin:admin http://127.0.0.1:8080/api/v1/clusters/abc/services/GREENPLUM/components/GREENPLUM_SLAVE?fields=host_components/HostRoles/host_name | awk -F: '/"host_name"/ {print $2}' | tr -d '" ' > /tmp/hostfile

    # confirm your installation. make sure you can do the following
    # su - gpadmin
    # source /usr/local/greenplum-db/greenplum_path.sh
    # Use the gpssh utility to see if you can login to all hosts without a password prompt, and to confirm that the Greenplum software was installed on all hosts. Use the hostfile_exkeys file you used for installation for example : gpssh -f hostfile_exkeys -e ls -l $GPHOME
    print "finished with the installation"
    FNULL.close()
    #sys.exit("Exited on purpose") 
 
  def stop(self, env):
    print 'Stop the Greenplum Master';
  def start(self, env):
    print 'Start the Greenplum Master';
     
  def status(self, env):
    print 'Status of the Greenplum Master';
  def configure(self, env):
    print 'Configure the Greenplum Master';

  @staticmethod
  def create_data_directories():

    config = Script.get_config()
    

    use_mirrors                         = config['configurations']['gpinitsystem_config']['use_mirrors']
    MASTER_DIRECTORY                    = config['configurations']['gpinitsystem_config']['MASTER_DIRECTORY']
    DATA_DIRECTORY                      = config['configurations']['gpinitsystem_config']['DATA_DIRECTORY']
    MIRROR_DATA_DIRECTORY               = config['configurations']['gpinitsystem_config']['MIRROR_DATA_DIRECTORY']
    gpUserName                          = config['configurations']['installation-config']['gp.admin.user']
    gpPassword                          = config['configurations']['installation-config']['gp.admin.password']
    addUserReturn = os.system("useradd -p "+gpPassword + " " + gpUserName)

    #if addUserReturn != "0":
    #  sys.exit("Install error: Unable to add " + gpUserName)

    uid=getpwnam(gpUserName)[2]
    gid=getpwnam(gpUserName)[3]

    # os.mkdirs(MASTER_DIRECTORY, 700)
    os.system("mkdir -p "+MASTER_DIRECTORY)
    os.chown(MASTER_DIRECTORY, uid, gid)

    for dir in DATA_DIRECTORY.split(' '):
      #os.mkdirs(dir, 700)
      os.system("mkdir -p "+dir)
      os.chown(dir, uid, gid)

    if use_mirrors == "true":
      for dir in MIRROR_DATA_DIRECTORY.split(' '):
        #os.mkdirs(dir, 700)
        os.system("mkdir -p "+dir)
        os.chown(dir, uid, gid)

  @staticmethod
  def create_gpinitsystem_config(path):
    config = Script.get_config()
    gpConfigPath = path+"/gpinitsystem_config"

    # Check to make sure gpConfigPath exists and is readable
    if not os.path.exists(path):
      sys.exit("Install error: "+ gpConfigPath + " does not exist.")

    # Get required gpinitsystem configuration variables. Lower-case variables are used for internal use only for logic.
    # Upper-case variable values are written to the gpinitsystem_config.
    use_mirrors                         = config['configurations']['gpinitsystem_config']['use_mirrors']
    ARRAY_NAME                          = config['configurations']['gpinitsystem_config']['ARRAY_NAME']
    SEG_PREFIX                          = config['configurations']['gpinitsystem_config']['SEG_PREFIX']
    PORT_BASE                           = config['configurations']['gpinitsystem_config']['PORT_BASE']
    DATA_DIRECTORY                      = config['configurations']['gpinitsystem_config']['DATA_DIRECTORY']
    # FIXME Get automatically
    MASTER_HOSTNAME                     = config['configurations']['gpinitsystem_config']['MASTER_HOSTNAME']
    MASTER_DIRECTORY                    = config['configurations']['gpinitsystem_config']['MASTER_DIRECTORY']
    MASTER_PORT                         = config['configurations']['gpinitsystem_config']['MASTER_PORT']
    TRUSTED_SHELL                       = config['configurations']['gpinitsystem_config']['TRUSTED_SHELL']
    CHECK_POINT_SEGMENTS                = config['configurations']['gpinitsystem_config']['CHECK_POINT_SEGMENTS']
    ENCODING                            = config['configurations']['gpinitsystem_config']['ENCODING']
    MIRROR_PORT_BASE                    = config['configurations']['gpinitsystem_config']['MIRROR_PORT_BASE']
    REPLICATION_PORT_BASE               = config['configurations']['gpinitsystem_config']['REPLICATION_PORT_BASE']
    MIRROR_REPLICATION_PORT_BASE        = config['configurations']['gpinitsystem_config']['MIRROR_REPLICATION_PORT_BASE']
    MIRROR_DATA_DIRECTORY               = config['configurations']['gpinitsystem_config']['MIRROR_DATA_DIRECTORY']
    DATABASE_NAME                       = config['configurations']['gpinitsystem_config']['DATABASE_NAME']
    MACHINE_LIST_FILE                   = config['configurations']['gpinitsystem_config']['MACHINE_LIST_FILE']

    f = open(gpConfigPath, 'w')
    if f:
      f.write("# Auto-generated by Ambari\n");
      f.write("ARRAY_NAME="+str(ARRAY_NAME)+"\n");
      f.write("SEG_PREFIX="+str(SEG_PREFIX)+"\n");
      f.write("PORT_BASE="+str(PORT_BASE)+"\n");
      f.write("declare -a DATA_DIRECTORY=(" + DATA_DIRECTORY+")\n");
      # FIXME Get automatically
      f.write("MASTER_HOSTNAME="+str(MASTER_HOSTNAME)+"\n");
      f.write("MASTER_DIRECTORY="+str(MASTER_DIRECTORY)+"\n");
      f.write("MASTER_PORT="+str(MASTER_PORT)+"\n");
      f.write("TRUSTED_SHELL="+str(TRUSTED_SHELL)+"\n");
      f.write("CHECK_POINT_SEGMENTS="+str(CHECK_POINT_SEGMENTS)+"\n");
      f.write("ENCODING="+str(ENCODING)+"\n");
      f.write("DATABASE_NAME="+str(DATABASE_NAME)+"\n")
      f.write("MACHINE_LIST_FILE="+str(MACHINE_LIST_FILE)+"\n")

      # Don't include configuration info for mirrors if use_mirrors is false.
      if use_mirrors == "true":
        f.write("MIRROR_PORT_BASE="+str(MIRROR_PORT_BASE)+"\n")
        f.write("REPLICATION_PORT_BASE="+str(REPLICATION_PORT_BASE)+"\n")
        f.write("MIRROR_REPLICATION_PORT_BASE="+str(MIRROR_REPLICATION_PORT_BASE)+"\n")
        f.write("declare -a MIRROR_DATA_DIRECTORY=(" + MIRROR_DATA_DIRECTORY+")\n")
      f.close()
    else:
      sys.exit("Install error: Cannot open "+ configFilePath + "for writing.")

if __name__ == "__main__":
  Master().execute()
