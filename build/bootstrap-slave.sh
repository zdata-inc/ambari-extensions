#!/bin/bash
rpm --replacepkgs --nosignature -i \
  /vagrant/artifacts/rpms/ambari-agent-1.7.0-209.x86_64.rpm \
  || sudo yum install -y ambari-agent

sudo chkconfig ambari-agent on
