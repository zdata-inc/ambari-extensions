from resource_management.libraries.functions.version import compare_versions
from resource_management.libraries.functions.default import default
from resource_management import *
import status_params

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

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


# Hosts
hostname = config['hostname']
namenode_host = default('/clusterHostInfo/namenode_host', [])
hdfs_slaves = default('/clusterHostInfo/slave_hosts', [])

is_namenode = hostname in namenode_host