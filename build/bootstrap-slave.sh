#!/bin/bash
cd /tmp

if [ -d /vagrant/artifacts/rpms ]; then
    rpm --replacepkgs --nosignature -i /vagrant/artifacts/rpms/ambari-agent-1.7.0-209.x86_64.rpm
else
    yum install -y ambari-agent
fi

chkconfig ambari-agent on
