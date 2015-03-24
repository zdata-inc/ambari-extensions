from resource_management import *
import os
import subprocess

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

# FIXME Find a better way to learn java_home
#java_home = subprocess.call("find / -name java -path *bin* 2> /dev/null | head -1 | sed 's/\/bin\/java//g'", shell=True)
java_home = "/usr/jdk64/jdk1.7.0_67/jre"

# Important directories
pxf_root_path = "/usr/lib/gphd/pxf"
pxf_instance_root_path = "/var/gphd/pxf"
pxf_etc_config_path = "/etc/gphd/pxf/conf"

# Environment variables for PXF 
pxf_env_script = os.path.join(pxf_etc_config_path, "pxf-env.sh")
# Kerberos security configuration file for PXF service
pxf_site = os.path.join(pxf_etc_config_path, "pxf-site.xml")
# PXF profiles definition file
pxf_profiles = os.path.join(pxf_etc_config_path, "pxf-profiles.xml")
# Classpaths required to run PXF
pxf_private_classpath = os.path.join(pxf_etc_config_path, "pxf-private.classpath")
# Classpaths for custom connectors 
pxf_public_classpath = os.path.join(pxf_etc_config_path, "pxf-public.classpath")
# PXF Logging configuration 
pxf_log4j_properties = os.path.join(pxf_etc_config_path, "pxf-log4j.properties")
# PID file Location
pxf_pid_file = os.path.join(pxf_instance_root_path, "pxf-service/logs/tcserver.pid");
