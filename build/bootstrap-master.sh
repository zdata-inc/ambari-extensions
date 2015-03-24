#!/bin/bash

# Setup repo
/vagrant/build/setup-repo.sh

rpm --replacepkgs --nosignature -i \
  /vagrant/artifacts/rpms/postgresql-libs-8.4.20-1.el6_5.x86_64.rpm \
  /vagrant/artifacts/rpms/postgresql-8.4.20-1.el6_5.x86_64.rpm \
  /vagrant/artifacts/rpms/postgresql-server-8.4.20-1.el6_5.x86_64.rpm \
  /vagrant/artifacts/rpms/ambari-server-1.7.0-209.noarch.rpm \
  || sudo yum install -y ambari-server

rpm --replacepkgs --nosignature -i \
  /vagrant/artifacts/rpms/ambari-agent-1.7.0-209.x86_64.rpm \
  || sudo yum install -y ambari-agent

if [ -f /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz ]; then
  cp /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz /var/lib/ambari-server/resources/jdk-7u67-linux-x64.tar.gz
fi

if [ -f /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip ]; then 
  cp /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip /var/lib/ambari-server/resources/UnlimitedJCEPolicyJDK7.zip
fi

sudo service postgresql initdb
sudo ambari-server setup -s 

sudo ambari-server start

sudo chkconfig postgresql on
sudo chkconfig ambari-server on

echo 'URL: http://master.ambaricluster.local:8080'
echo 'Default username and password: admin/admin'
