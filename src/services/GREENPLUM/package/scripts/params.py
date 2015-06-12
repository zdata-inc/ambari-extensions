from resource_management.libraries.functions.default import default
from resource_management import *
from resource_management.core.source import InlineTemplate
import utilities
from os import path

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

license_accepted = default('/configurations/greenplum-env/accept_license_agreement', False) == "yes"
installer_location = config['configurations']['greenplum-env']['installer_location']
set_kernel_parameters = default('configurations/greenplum-env/set_kernel_parameters', True)

installation_path = config['configurations']['greenplum-env']['installation_path']
absolute_installation_path = path.join(installation_path, 'greenplum-db')
admin_user = config['configurations']['greenplum-env']['admin_user']
admin_password = config['configurations']['greenplum-env']['admin_password']
hashed_admin_password = utilities.crypt_password(admin_password)

cluster_name = config['configurations']['greenplum-env']['cluster_name']
database_name = config['configurations']['greenplum-env']['database_name']
segments_per_node = int(config['configurations']['greenplum-env']['segments_per_node'])

master_data_directory = config['configurations']['greenplum-env']['master_data_directory']
data_directory_template = config['configurations']['greenplum-env']['data_directory']

master_port = int(config['configurations']['greenplum-env']['master_port'])
encoding = config['configurations']['greenplum-env']['encoding']

check_point_segments = config['configurations']['greenplum-env']['check_point_segments']

portbase = int(config['configurations']['greenplum-env']['port_base'])
portbase_replication = int(config['configurations']['greenplum-env']['replication_port_base'])

segment_prefix = config['configurations']['greenplum-env']['segment_prefix']

mirroring_enabled = default('/configurations/greenplum-mirroring/enable_mirroring', False)
mirror_data_directory_template = config['configurations']['greenplum-mirroring']['mirror_data_directory']
portbase_mirror = config['configurations']['greenplum-mirroring']['mirror_port_base']
portbase_mirror_replication = config['configurations']['greenplum-mirroring']['mirror_replication_port_base']

# Import file paths
master_data_segment_directory = path.join(master_data_directory, segment_prefix + '-1')
greenplum_segment_hosts_file = path.join(installation_path, 'greenplum-db', 'greenplum_segments')
greenplum_all_hosts_file = path.join(installation_path, 'greenplum-db', 'greenplum_hosts')
greenplum_initsystem_config_file = path.join('/home', admin_user, 'gpconfigs', 'gpinitsystem_config')
security_conf_file = "/etc/security/limits.d/greenplum.conf"

# Hosts
hostname = config['hostname']
master_node = default("/clusterHostInfo/greenplum_master_hosts", [None])[0]
master_standby_node = default("/clusterHostInfo/greenplum_standby_master_hosts", [None])[0]
segment_nodes = set(default("/clusterHostInfo/greenplum_slave_hosts", []))

# If a node is both a master and standby, don't consider it a standby.
if master_standby_node == master_node:
    master_standby_node = None

all_nodes = segment_nodes.copy()
if master_node != None:
    all_nodes.add(master_node)
if master_standby_node != None:
    all_nodes.add(master_standby_node)

is_standby_masternode = hostname == master_standby_node
is_masternode = hostname == master_node
is_segmentnode = hostname in segment_nodes

# If there are more nodes than segments mirror spreading can be enabled, if mirroring is enabled
enable_mirror_spreading = len(segment_nodes) > segments_per_node

# Generate list of data and mirror directory paths from their templates
@utilities.call()
def data_directories():
    return utilities.parse_path_pattern_expression(data_directory_template, segments_per_node)

@utilities.call()
def mirror_data_directories():
    global mirroring_enabled
    if not mirroring_enabled:
        return []

    return utilities.parse_path_pattern_expression(mirror_data_directory_template, segments_per_node)

@utilities.call()
def all_data_directories():
    return data_directories + mirror_data_directories

# Pid files
master_pid_path = path.join(master_data_segment_directory, 'postmaster.pid')
segment_pid_globs = map(lambda pid_path: path.join(pid_path, segment_prefix + '[0-9]', 'postmaster.pid'), all_data_directories)
