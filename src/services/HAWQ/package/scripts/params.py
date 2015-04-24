from resource_management import *
from library import utilities
from os import path

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

# User info
hawq_user = config["configurations"]["hawq-env"]["hawq_user"]
hawq_password = config["configurations"]["hawq-env"]["hawq_password"]
hashed_hawq_password = utilities.crypt_password(hawq_password)

# Host info
hawq_master_hosts = default("/clusterHostInfo/hawq_master_hosts",[])
hawq_segment_hosts = default("/clusterHostInfo/hawq_slave_hosts", [])
hawq_all_hosts = set(hawq_master_hosts + hawq_segment_hosts)
standby_master_hostname = ""

# User configurations
set_kernel_parameters = default('configurations/greenplum-env/set_kernel_parameters', True)
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
DFS_DIRECTORY = 'hawq_data'

# Important paths
security_conf_path = "/etc/security/limits.d"
hawq_install_path = "/usr/local/hawq/"
MASTER_DIRECTORY = config["configurations"]["hawq-env"]["MASTER_DIRECTORY"]
hadoop_home = config["configurations"]["hawq-env"]["hadoop_home"]
hawq_environment_path = path.join(hawq_install_path, "greenplum_path.sh")
hawq_hostfile_all_path = path.join(hawq_install_path, "hostfile_all")
hawq_hostfile_seg_path = path.join(hawq_install_path, "hostfile_segments")
gpconfigs_path = path.join("/home", hawq_user, "gpconfigs")
gpinitsystem_config_path = path.join(gpconfigs_path, "gpinitsystem_config")

segments_per_node = config['configurations']['hawq-env']['segments_per_node']
data_directory_template = config['configurations']['hawq-env']['data_directory']

# Generate list of data and mirror directory paths from their templates
@utilities.call()
def data_directories():
    directories = []
    for segment_number in range(segments_per_node):
        directories.append(InlineTemplate(data_directory_template, segment_number=(segment_number + 1)).get_content().strip())

    return directories

# Pull in some configs from HDFS
if config["commandType"] == 'EXECUTION_COMMAND':
    dfs_superuser = config["configurations"]["hdfs-site"]["dfs.cluster.administrators"].strip()
    dfs_supergroup = config["configurations"]["hdfs-site"]["dfs.permissions.superusergroup"]
    DFS_URL = config["configurations"]["core-site"]["fs.defaultFS"].replace("hdfs://", "")
    DFS_URI = path.join(DFS_URL, DFS_DIRECTORY)

# Common commands
source_cmd = "source %s; " % hawq_environment_path
exkeys_cmd = "gpssh-exkeys -f %s; " % hawq_hostfile_seg_path
export_mdd_cmd = "export MASTER_DATA_DIRECTORY=%s/gpseg-1" % MASTER_DIRECTORY

# Pid files
master_pid_path = path.join(MASTER_DIRECTORY, SEG_PREFIX + '-1', 'postmaster.pid')
slave_pid_globs = map(lambda pid_path: path.join(pid_path, SEG_PREFIX + '[0-9]', 'postmaster.pid'), data_directories)