import os

from resource_management import *
import getpass

def setup_java():
  """
  Installs jdk using specific params, that comes from ambari-server
  """
  import params

  jdk_curl_target = format("{params.artifact_dir}/{params.jdk_name}")
  java_dir = os.path.dirname(params.java_home)
  java_exec = format("{params.java_home}/bin/java")
  tmp_java_dir = format("{params.tmp_dir}/jdk")

  if not params.jdk_name:
    return

  Directory(params.artifact_dir,
      recursive = True,
  )
  File(jdk_curl_target,
       content = DownloadSource(format("{params.jdk_location}/{params.jdk_name}")),
  )

  if params.jdk_name.endswith(".bin"):
    chmod_cmd = ("chmod", "+x", jdk_curl_target)
    install_cmd = format("mkdir -p {tmp_java_dir} && cd {tmp_java_dir} && echo A | {jdk_curl_target} -noregister && sudo cp -rp {tmp_java_dir}/* {java_dir}")
  elif params.jdk_name.endswith(".gz"):
    chmod_cmd = ("chmod","a+x", java_dir)
    install_cmd = format("mkdir -p {tmp_java_dir} && cd {tmp_java_dir} && tar -xf {jdk_curl_target} && sudo cp -rp {tmp_java_dir}/* {java_dir}")

  Directory(java_dir)

  Execute(chmod_cmd,
    not_if = format("test -e {java_exec}"),
    sudo = True,
  )

  Execute(install_cmd,
    not_if = format("test -e {java_exec}")
  )

  # Execute(("chgrp","-R", params.user_group, params.java_home),
  #   sudo = True,
  # )
  # Execute(("chown","-R", getpass.getuser(), params.java_home),
  #   sudo = True,
  # )

def install_packages():
  import params
  packages = ['unzip', 'curl']
  Package(packages)