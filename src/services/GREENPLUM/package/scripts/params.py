from resource_management.libraries.functions.default import default
from resource_management import *
from resource_management.core.source import InlineTemplate
import utilities
from os import path

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

license_accepted = default('/configurations/greenplum-env/accept_license_agreement', False) == "yes"
installer_location = default('/configurations/greenplum-env/installer_location', None)

installation_path = default('/configurations/greenplum-env/installation_path', None)
absolute_installation_path = path.join(installation_path, 'greenplum-db')
admin_user = default('/configurations/greenplum-env/admin_user', None)
admin_password = default('/configurations/greenplum-env/admin_password', None)
hashed_admin_password = utilities.crypt_password(admin_password)

cluster_name = default('/configurations/greenplum-env/cluster_name', None)
database_name = default('/configurations/greenplum-env/database_name', None)
segments_per_node = int(default('/configurations/greenplum-env/segments_per_node', None))

master_data_directory = default('/configurations/greenplum-env/master_data_directory', None)
data_directory_template = default('/configurations/greenplum-env/data_directory', None)

master_port = int(default('/configurations/greenplum-env/master_port', None))
encoding = default('/configurations/greenplum-env/encoding', None)

check_point_segments = default('/configurations/greenplum-env/check_point_segments', None)

portbase = int(default('/configurations/greenplum-env/port_base', None))
portbase_replication = int(default('/configurations/greenplum-env/replication_port_base', None))

segment_prefix = default('/configurations/greenplum-env/segment_prefix', None)

mirroring_enabled = default('/configurations/greenplum-mirroring/enable_mirroring', False)
mirror_data_directory_template = default('/configurations/greenplum-mirroring/mirror_data_directory', False)
portbase_mirror = default('/configurations/greenplum-mirroring/mirror_port_base', False)
portbase_mirror_replication = default('/configurations/greenplum-mirroring/mirror_replication_port_base', False)

# Import file paths
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
    directories = []
    for segment_number in range(segments_per_node):
        directories.append(InlineTemplate(data_directory_template, segment_number=(segment_number + 1)).get_content().strip())

    return directories

@utilities.call()
def mirror_data_directories():
    global mirroring_enabled
    if not mirroring_enabled:
        return []

    directories = []
    for segment_number in range(segments_per_node):
        directories.append(InlineTemplate(mirror_data_directory_template, segment_number=(segment_number + 1)).get_content().strip())

    return directories

# Pid files
master_pid_path = path.join(master_data_directory, segment_prefix + '-1/postmaster.pid')
segment_pid_globs = map(lambda pid_path: path.join(pid_path, segment_prefix + '[0-9]', 'postmaster.pid'), data_directories)