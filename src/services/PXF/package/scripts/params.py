from os import path
import utilities
from resource_management import *

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

java_home = utilities.detect_java_home()
if java_home == None:
    raise StandardError('Cannot automatically find JAVA_HOME')

# Important directories
pxf_root_path = "/usr/lib/gphd/pxf"
pxf_instance_root_path = "/var/gphd/pxf"
pxf_etc_config_path = "/etc/gphd/pxf/conf"

pxf_env_script = path.join(pxf_etc_config_path, "pxf-env.sh") # Environment variables for PXF 
pxf_site = path.join(pxf_etc_config_path, "pxf-site.xml") # Kerberos security configuration file for PXF service
pxf_profiles = path.join(pxf_etc_config_path, "pxf-profiles.xml") # PXF profiles definition file
pxf_private_classpath = path.join(pxf_etc_config_path, "pxf-private.classpath") # Classpaths required to run PXF
pxf_public_classpath = path.join(pxf_etc_config_path, "pxf-public.classpath") # Classpaths for custom connectors 
pxf_log4j_properties = path.join(pxf_etc_config_path, "pxf-log4j.properties") # PXF Logging configuration
pxf_pid_file = path.join(pxf_instance_root_path, "pxf-service/logs/tcserver.pid")
