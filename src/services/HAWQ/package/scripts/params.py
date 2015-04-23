from resource_management import *
from library import utilities
from os import path

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

# User info
hawq_user = config["configurations"]["hawq-env"]["hawq_user"]
hawq_password = config["configurations"]["hawq-env"]["hawq_password"]
hashed_hawq_password = utilities.crypt_password(hawq_password)

dfs_superuser = config["configurations"]["hdfs-site"]["dfs.cluster.administrators"].strip()
dfs_supergroup = config["configurations"]["hdfs-site"]["dfs.permissions.superusergroup"]

# Important paths, directories, and files
hawq_install_path = "/usr/local/hawq/"
hawq_environment_path = path.join(hawq_install_path, "greenplum_path.sh")
hawq_hostfile_all_path = path.join(hawq_install_path, "hostfile_all")
hawq_hostfile_seg_path = path.join(hawq_install_path, "hostfile_segments")
sysctl_conf_file = "/etc/sysctl.conf"
security_conf_file = "/etc/security/limits.d/hawq.conf"
MASTER_DIRECTORY = config["configurations"]["hawq-env"]["MASTER_DIRECTORY"]
DATA_DIRECTORY = config["configurations"]["hawq-env"]["DATA_DIRECTORY"]
hadoop_home = config["configurations"]["hawq-env"]["hadoop_home"]
gpconfigs_path = path.join("/home", hawq_user, "gpconfigs")
gpinitsystem_config_path = path.join(gpconfigs_path, "gpinitsystem_config")

# Host info
hawq_master_hosts = default("/clusterHostInfo/hawq_master_hosts",[])
hawq_segment_hosts = default("/clusterHostInfo/hawq_slave_hosts", [])
hawq_all_hosts = set(hawq_master_hosts + hawq_segment_hosts)
standby_master_hostname = ""

# Common commands
source_cmd = "source %s; " % hawq_environment_path
exkeys_cmd = "gpssh-exkeys -f %s; " % hawq_hostfile_seg_path
export_mdd_cmd = "export MASTER_DATA_DIRECTORY=%s/gpseg-1" % MASTER_DIRECTORY

# User configurations
ARRAY_NAME = config["configurations"]["hawq-env"]["ARRAY_NAME"]
SEG_PREFIX = config["configurations"]["hawq-env"]["SEG_PREFIX"]
PORT_BASE = config["configurations"]["hawq-env"]["PORT_BASE"]
MASTER_HOSTNAME = config["hostname"]
MASTER_PORT = config["configurations"]["hawq-env"]["MASTER_PORT"]
TRUSTED_SHELL = config["configurations"]["hawq-env"]["TRUSTED_SHELL"]
CHECK_POINT_SEGMENTS = config["configurations"]["hawq-env"]["CHECK_POINT_SEGMENTS"]
ENCODING = config["configurations"]["hawq-env"]["ENCODING"]
DATABASE_NAME = config["configurations"]["hawq-env"]["DATABASE_NAME"]
KERBEROS_KEYFILE = config["configurations"]["hawq-env"]["KERBEROS_KEYFILE"]
ENABLE_SECURE_FILESYSTEM = config["configurations"]["hawq-env"]["ENABLE_SECURE_FILESYSTEM"]

DFS_NAME = config["configurations"]["hawq-env"]["DFS_NAME"]
DFS_URL = config["configurations"]["core-site"]["fs.defaultFS"].replace("hdfs://", "")

# Pids
hawq_master_pid_path = path.join(MASTER_DIRECTORY, SEG_PREFIX + '-1/postmaster.pid')
hawq_slave_glob = "/data[0-9]/primary/gpseg[0-9]"
