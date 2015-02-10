from resource_management import *
import os

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

# User info
hawq_user = "gpadmin"
hawq_password = "changeme"

# Important paths, directories, and files
hawq_install_path = "/usr/local/hawq/"
hawq_environment_path = os.path.join(hawq_install_path, "greenplum_path.sh")
hawq_hostfile_path = os.path.join(hawq_install_path, "hostfile")
sysctl_conf_file = "/etc/sysctl.conf"
security_conf_file = "/etc/security/limits.d/hawq.conf"
MASTER_DIRECTORY = config["configurations"]["hawq_config"]["MASTER_DIRECTORY"]
DATA_DIRECTORY = config["configurations"]["hawq_config"]["DATA_DIRECTORY"]
gpconfigs_path = "/home/"+hawq_user+"/gpconfigs/"
gpinitsystem_config_path = gpconfigs_path+"gpinitsystem_config"
MACHINE_LIST_FILE = gpconfigs_path+"hostfile_gpinitsystem"

# Host info
hawq_master_hosts = default("/clusterHostInfo/hawq_master_hosts",[])
hawq_segment_hosts = default("/clusterHostInfo/hawq_slave_hosts", [])
hawq_all_hosts = set(hawq_master_hosts + hawq_segment_hosts)
standby_master_hostname = ""

# Common commands
source_cmd = "source "+hawq_environment_path+"; "
exkeys_cmd = "gpssh-exkeys -f "+hawq_hostfile_path+"; "
export_mdd_cmd = "export MASTER_DATA_DIRECTORY="+ MASTER_DIRECTORY +"/gpseg-1"
gpinitsystem_cmd = "gpinitsystem -c " + gpinitsystem_config_path +" -h "+ hawq_hostfile_path + " -a; "
gpinitsystem_with_standby_cmd = "gpinitsystem -c " + gpinitsystem_config_path +" -h "+ hawq_hostfile_path + "-s "+ standby_master_hostname +" -a; " 

# User configurations
ARRAY_NAME = config["configurations"]["hawq_config"]["ARRAY_NAME"]
SEG_PREFIX = config["configurations"]["hawq_config"]["SEG_PREFIX"]
PORT_BASE = config["configurations"]["hawq_config"]["PORT_BASE"]
MASTER_HOSTNAME = config["hostname"] 
MASTER_PORT = config["configurations"]["hawq_config"]["MASTER_PORT"]
TRUSTED_SHELL = config["configurations"]["hawq_config"]["TRUSTED_SHELL"]
CHECK_POINT_SEGMENTS = config["configurations"]["hawq_config"]["CHECK_POINT_SEGMENTS"]
ENCODING = config["configurations"]["hawq_config"]["ENCODING"]
DATABASE_NAME = config["configurations"]["hawq_config"]["DATABASE_NAME"]
DFS_NAME = config["configurations"]["hawq_config"]["DFS_NAME"]
DFS_URL = config["configurations"]["hawq_config"]["DFS_URL"]
KERBEROS_KEYFILE = config["configurations"]["hawq_config"]["KERBEROS_KEYFILE"]
ENABLE_SECURE_FILESYSTEM = config["configurations"]["hawq_config"]["ENABLE_SECURE_FILESYSTEM"]
