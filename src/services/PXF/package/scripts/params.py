from resource_management import *
import os

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

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
