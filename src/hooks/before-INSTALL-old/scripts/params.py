from resource_management import *
from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

stack_version_unformatted = str(config['hostLevelParams']['stack_version'])
stack_version = format_hdp_stack_version(stack_version_unformatted)

user_group = config['configurations']['cluster-env']['user_group']

# Java
artifact_dir = format("{tmp_dir}/AMBARI-artifacts/")

java_home = config['hostLevelParams']['java_home']

jdk_name = default("/hostLevelParams/jdk_name", None) # None when jdk is already installed by user
jce_policy_zip = default("/hostLevelParams/jce_name", None) # None when jdk is already installed by user
jce_location = config['hostLevelParams']['jdk_location']
jdk_location = config['hostLevelParams']['jdk_location']

# Repositories
repo_info = config['hostLevelParams']['repo_info']
service_repo_info = default("/hostLevelParams/service_repo_info", None)